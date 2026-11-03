"""Setting 2 (verifier, stop-on-success), expanded.

Data sources: monkey_business (MATH, CodeContests, MiniF2F, GSM8K), Weaver (MATH500, GPQA, MMLU,
MMLU-Pro; Llama-3.1 8B and 70B on the same problems).
Policies (total budget S = u*N target-model samples):
  RR-unsolved            round-robin over unsolved (strongest prior-free baseline)
  E2 online (IAS cap)    sample-until-success up to a harder-gets-more cap, leftover RR
  Bayes-history          myopic posterior P(success next), prior = history-bin mixture
  Bayes-CV               prior = w * history mixture + (1-w) * exchangeable pool, w picked by
                         inner cross-validation on the calibration half (no test-set tuning)
  Bayes-proxy (charged)  history signal = proxy model's pass rate from m fresh samples drawn at test
                         time; cost m * N * (proxy_params / target_params) is subtracted from S
Calibration (signal -> pass-rate mixture) is 2-fold cross-fitted with target labels on the other half.
"""
import json
import re
import sys
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/e2")
from e2_cost import ias

D = "paper4/data_ext/"
rng = np.random.default_rng(12)
U = [4, 16, 64]
REPS = 20
W_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]


# ---------------- loaders: return {key: bool array of samples} ----------------
def mb(cfg):
    t = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects", "orig_dset_idx"])
    return {k: np.asarray(v, bool) for k, v in zip(t.column(1).to_pylist(), t.column(0).to_pylist())}


def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def weaver(task, size):
    import glob
    out = {}
    for f in sorted(glob.glob(D + f"weaver_{task}_{size}_*.parquet")):
        sch = pq.ParquetFile(f).schema_arrow.names
        key = "problem" if "problem" in sch else ("instruction" if "instruction" in sch else sch[0])
        t = pq.read_table(f, columns=[key, "answer_correct"])
        for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist()):
            if v:
                out[norm(k)] = np.asarray([bool(x) for x in v], bool)
    return out


def aligned(a, b):
    keys = [k for k in a if k in b]
    return [a[k] for k in keys], [b[k] for k in keys]


# ---------------- simulation ----------------
def first_success(samples, r):
    T = np.empty(len(samples))
    for i, s in enumerate(samples):
        h = np.flatnonzero(s[r.permutation(len(s))])
        T[i] = h[0] + 1 if len(h) else np.inf
    return T


def rr(T, S):
    n = np.zeros(len(T))
    solved = np.zeros(len(T), bool)
    left = int(S)
    while left > 0:
        act = np.flatnonzero(~solved)
        if len(act) == 0:
            break
        take = act[:left]
        n[take] += 1
        left -= len(take)
        solved[take] = T[take] <= n[take]
    return float(solved.mean())


def e2_online(T, S, phat, K):
    caps = ias(phat, int(S), K)
    n = np.zeros(len(T))
    solved = np.zeros(len(T), bool)
    left = int(S)
    for i in range(len(T)):
        use = int(min(caps[i], T[i])) if np.isfinite(T[i]) else int(caps[i])
        use = min(use, left)
        n[i] = use
        left -= use
        solved[i] = T[i] <= n[i]
        if left <= 0:
            break
    while left > 0:
        act = np.flatnonzero(~solved)
        if len(act) == 0:
            break
        take = act[:left]
        n[take] += 1
        left -= len(take)
        solved[take] = T[take] <= n[take]
    return float(solved.mean())


def bayes(T, S, mix, wts=None):
    """mix[i]: array of candidate pass rates; wts[i]: their weights. Myopic posterior index."""
    N = len(T)
    f = np.zeros(N, int)
    solved = np.zeros(N, bool)
    W = wts if wts is not None else [np.ones(len(m)) for m in mix]
    idx = np.array([(m * w).sum() / w.sum() for m, w in zip(mix, W)])
    for _ in range(int(S)):
        c = np.where(solved, -1.0, idx)
        i = int(np.argmax(c))
        if c[i] < 0:
            break
        f[i] += 1
        if T[i] <= f[i]:
            solved[i] = True
        else:
            w = W[i] * (1 - mix[i]) ** f[i]
            idx[i] = float((mix[i] * w).sum() / w.sum()) if w.sum() > 0 else 0.0
    return float(solved.mean())


def bins_mix(p_cal, sig_cal, sig_tst, nb=5):
    edges = np.unique(np.quantile(sig_cal, np.linspace(0, 1, nb + 1)[1:-1]))
    bc, bt = np.digitize(sig_cal, edges), np.digitize(sig_tst, edges)
    return [p_cal[bc == t] if np.any(bc == t) else p_cal for t in bt]


def tempered(mix_hist, pool, w):
    """Mixture with mass w on the history bin and 1-w on the exchangeable pool."""
    out_m, out_w = [], []
    for m in mix_hist:
        out_m.append(np.concatenate([m, pool]))
        out_w.append(np.concatenate([np.full(len(m), w / len(m)), np.full(len(pool), (1 - w) / len(pool))]))
    return out_m, out_w


def choose_w(samples, p, sig, cal, u, r):
    """Inner CV on the calibration half: build bins on one part, simulate on the other, pick w."""
    perm = r.permutation(cal)
    a, b = perm[: len(perm) // 2], perm[len(perm) // 2:]
    mix = bins_mix(p[a], sig[a], sig[b])
    pool = p[a]
    best, best_w = -1, 1.0
    for w in W_GRID:
        sc = 0
        for _ in range(4):
            T = first_success([samples[i] for i in b], r)
            m, ww = tempered(mix, pool, w)
            sc += bayes(T, u * len(b), m, ww)
        if sc > best:
            best, best_w = sc, w
    return best_w


def evaluate(name, tgt, ref, u_list=U, proxy_ratio=None, m_proxy=16):
    p = np.array([s.mean() for s in tgt])
    sig_full = np.array([s.mean() for s in ref])
    N = len(p)
    res = {}
    for u in u_list:
        S, K = u * N, 16 * u
        acc = {}
        for _ in range(REPS):
            perm = rng.permutation(N)
            halves = [perm[: N // 2], perm[N // 2:]]
            mix = [None] * N
            phat = np.empty(N)
            ws = {}
            for a, b in ((0, 1), (1, 0)):
                cal, tst = halves[a], halves[b]
                mb_ = bins_mix(p[cal], sig_full[cal], sig_full[tst])
                for i, m in zip(tst, mb_):
                    mix[i] = m
                    phat[i] = m.mean()
                ws[b] = choose_w(tgt, p, sig_full, cal, u, rng)
            T = first_success(tgt, rng)
            r = {"RR": rr(T, S), "E2 online": e2_online(T, S, phat, K),
                 "Bayes-history": bayes(T, S, mix)}
            # CV-tempered: each test half uses the w chosen on its own calibration half
            mt, wt = [None] * N, [None] * N
            for b, w in ws.items():
                pool = p[halves[1 - b]]
                m_b, w_b = tempered([mix[i] for i in halves[b]], pool, w)
                for i, mm, ww in zip(halves[b], m_b, w_b):
                    mt[i], wt[i] = mm, ww
            r["Bayes-CV"] = bayes(T, S, mt, wt)
            r["w chosen"] = float(np.mean(list(ws.values())))
            if proxy_ratio is not None:
                # proxy signal from m fresh proxy samples per problem, charged against the budget
                sig_px = np.array([rng.choice(s, m_proxy, replace=False).mean() for s in ref])
                cost = int(round(m_proxy * N * proxy_ratio))
                mixp = [None] * N
                for a, b in ((0, 1), (1, 0)):
                    cal, tst = halves[a], halves[b]
                    for i, m in zip(tst, bins_mix(p[cal], sig_px[cal], sig_px[tst])):
                        mixp[i] = m
                r["Bayes-proxy (charged)"] = bayes(T, max(S - cost, 0), mixp) if S > cost else float("nan")
                r["RR (same charged budget)"] = rr(T, max(S - cost, 0))
            for k, v in r.items():
                acc.setdefault(k, []).append(v)
        res[u] = {k: [float(np.nanmean(v)), float(np.nanstd(v) / np.sqrt(len(v)))] for k, v in acc.items()}
        row = res[u]
        base = row["RR"][0]
        print(f"{name:52} N={N:4d} u={u:3d} | RR {100*base:5.1f}% | " +
              " ".join(f"{k}: {100*(v[0]-base):+5.1f}" if k != "w chosen" else f"w={v[0]:.2f}"
                       for k, v in row.items() if k != "RR"), flush=True)
    return res


def main():
    out = {}
    jobs = []
    # monkey_business
    for t, r_, ratio in [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B", None),
                         ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct", None),
                         ("MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct", None),
                         ("MATH_Llama-3-8B-Instruct", "MATH_Pythia-1.4B", 1.4 / 8),
                         ("MATH_Llama-3-70B-Instruct", "MATH_Llama-3-8B-Instruct", 8 / 70),
                         ("CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct", None),
                         ("CodeContests_Llama-3-70B-Instruct", "CodeContests_Llama-3-8B-Instruct", 8 / 70),
                         ("MiniF2F-MATH_Llama-3-8B-Instruct", "MiniF2F-MATH_Llama-3-70B-Instruct", None),
                         ("MiniF2F-MATH_Llama-3-70B-Instruct", "MiniF2F-MATH_Llama-3-8B-Instruct", 8 / 70),
                         ("GSM8K_Llama-3-8B-Instruct", "GSM8K_Llama-3-70B-Instruct", None),
                         ("GSM8K_Llama-3-70B-Instruct", "GSM8K_Llama-3-8B-Instruct", 8 / 70)]:
        jobs.append((f"monkey {t} <- {r_}", lambda t=t, r_=r_: aligned(mb(t), mb(r_)), ratio))
    # hard targets helped by cheaper Pythia proxies (charged by parameter ratio)
    for t, r_, ratio in [("MATH_Pythia-1.4B", "MATH_Pythia-410M", 0.41 / 1.4),
                         ("MATH_Pythia-1.4B", "MATH_Pythia-160M", 0.16 / 1.4),
                         ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B", 1.4 / 6.9),
                         ("MATH_Pythia-6.9B", "MATH_Pythia-410M", 0.41 / 6.9)]:
        jobs.append((f"pythiaproxy {t} <- {r_}", lambda t=t, r_=r_: aligned(mb(t), mb(r_)), ratio))
    for task in ["MATH500", "GPQA", "MMLU", "MMLU-Pro"]:
        jobs.append((f"weaver {task} 8B <- 70B", lambda task=task: aligned(weaver(task, "8B"), weaver(task, "70B")), None))
        jobs.append((f"weaver {task} 70B <- 8B", lambda task=task: aligned(weaver(task, "70B"), weaver(task, "8B")), 8 / 70))
    only = sys.argv[1:] or None
    for name, loader, ratio in jobs:
        if only and not any(o in name for o in only):
            continue
        try:
            tgt, ref = loader()
        except Exception as e:  # missing download etc.
            print(f"SKIP {name}: {e}", flush=True)
            continue
        if len(tgt) < 40:
            print(f"SKIP {name}: only {len(tgt)} aligned problems", flush=True)
            continue
        out[name] = evaluate(name, tgt, ref, proxy_ratio=ratio)
        import os
        json.dump(out, open(os.environ.get("E2_OUT", "paper4/e2/e2_online_v2.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
