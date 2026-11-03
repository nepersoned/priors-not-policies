"""E2 cost: how much do 'harder gets more' rules lose in the binary (pass@k) regime?

Truth: each problem's pool accuracy p_i; coverage with k samples = 1 - (1 - p_i)^k.
Policies at equal total budget S = u*N:
  uniform, oracle (greedy on true curves),
  E2 rules found in the survey:
    IAS        k = ceil(log(1-C)/log(1-p)), capped at Nmax (2506.09338, 2605.06785)
    linear     k proportional to (1 - p)          (FSC 2608.24590, DATPO 2609.08650)
    exp        k proportional to exp(-p)          (AttnRL 2509.26628)
    tiers      easy/medium/hard tertiles 21:30:45 (Text2Cypher 2609.02324)
Two settings:
  oracle-difficulty : rules use the true p (isolates the rule's structure)
  probe (m charged)  : p estimated from m probe samples that count against S;
                       plus a correct deployable rule: Bayes marginal-gain greedy
                       under a Beta posterior.
Metric: coverage gain over uniform (accuracy points) and share of oracle headroom captured.
"""
import json
import sys
import numpy as np
import pyarrow.parquet as pq

D = "paper4/data_ext/"
BUDGETS = [2, 4, 8, 16, 32]
M_PROBE = 4
REPS = 20
rng = np.random.default_rng(2026)


def load():
    out = {}
    if "hard" in sys.argv:
        for cfg in ["CodeContests_Llama-3-8B-Instruct", "CodeContests_Gemma-2B",
                    "CodeContests_Llama-3-70B-Instruct", "MATH_Pythia-1.4B", "MATH_Pythia-6.9B",
                    "MATH_Gemma-2B"]:
            x = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()
            out[f"monkey {cfg}"] = [np.asarray(v, float) for v in x]
        return out
    z = np.load(D + "prm800k_compact.npz")
    ids = sorted({k.split("_")[1] for k in z.files}, key=int)
    out["PRM800K MATH (GPT-4 gen)"] = [z[f"c_{i}"] for i in ids]
    for cfg in ["GSM8K_Llama-3-8B-Instruct", "MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct"]:
        x = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()
        out[f"monkey {cfg}"] = [np.asarray(v, float) for v in x]
    x = pq.read_table(D + "weaver_gsm8k_4omini.parquet", columns=["answer_correct"]).column(0).to_pylist()
    out["Weaver GSM8K 4o-mini"] = [np.asarray(v, float) for v in x]
    return out


def coverage(p, k):
    return float(np.mean(1 - (1 - p) ** k))


def fix_sum(w, S, kmin=1, kmax=None):
    """Integer allocation proportional to weights w with sum S, k >= kmin."""
    N = len(w)
    w = np.maximum(np.asarray(w, float), 0)
    free = S - kmin * N
    if w.sum() <= 0:
        w = np.ones(N)
    raw = w / w.sum() * free
    k = np.floor(raw).astype(int)
    rem = free - k.sum()
    k[np.argsort(-(raw - k))[:rem]] += 1
    k += kmin
    if kmax is not None:
        k = np.minimum(k, kmax)
    return k


def greedy_curves(fail, S, kmin=1):
    """fail: (N, K) failure prob after k samples (k = 1..K). Greedy on marginals."""
    N, K = fail.shape
    d = np.minimum.accumulate(fail[:, kmin - 1:-1] - fail[:, kmin:], axis=1)
    extra = S - kmin * N
    if extra <= 0:
        return np.full(N, kmin)
    flat = np.sort(d.ravel())[::-1]
    thr = flat[min(extra, flat.size) - 1]
    take = (d > thr).sum(1)
    short = extra - take.sum()
    for i, _ in np.argwhere(d == thr)[:max(short, 0)]:
        take[i] += 1
    return kmin + take


def oracle(p, S, K):
    ks = np.arange(1, K + 1)
    return greedy_curves((1 - p[:, None]) ** ks[None, :], S)


def ias(p, S, K, C=0.95):
    """IAS rule; bisect Nmax so the total matches S, leftover spread uniformly."""
    lo, hi, best = 1, K, None
    q = np.clip(1 - p, 1e-12, 1 - 1e-12)
    base = np.where(p >= 1, 1, np.ceil(np.log(1 - C) / np.log(q)))
    base = np.maximum(base, 1)
    while lo <= hi:
        nm = (lo + hi) // 2
        k = np.minimum(base, nm).astype(int)
        if k.sum() <= S:
            best, lo = k, nm + 1
        else:
            hi = nm - 1
    if best is None:
        best = np.ones(len(p), int)
    left = S - best.sum()
    order = np.argsort(best)
    best[order[:left % len(p)]] += 1
    best += left // len(p)
    return best


def rules(pd, S, K, kmin=1):
    N = len(pd)
    t1, t2 = np.quantile(pd, [1 / 3, 2 / 3])
    tier = np.where(pd >= t2, 21, np.where(pd >= t1, 30, 45))   # high p = easy
    return {"E2 IAS": ias(pd, S, K) if kmin == 1 else None,
            "E2 linear (1-p)": fix_sum(1 - pd, S, kmin),
            "E2 exp(-p)": fix_sum(np.exp(-pd), S, kmin),
            "E2 tiers 21:30:45": fix_sum(tier, S, kmin)}


def bayes_marginal(s, m, S, K):
    """Greedy on posterior-expected failure E[(1-p)^k], p ~ Beta(1+s, 1+m-s); k counts probe."""
    a, b = 1 + s, 1 + m - s
    j = np.arange(K)
    # E[(1-p)^k] = prod_{j<k} (b+j)/(a+b+j)
    ratio = (b[:, None] + j[None, :]) / (a[:, None] + b[:, None] + j[None, :])
    fail = np.cumprod(ratio, axis=1)          # column k-1 -> k samples
    return greedy_curves(fail, S, kmin=m)


def main():
    data = load()
    res = {}
    for name, arrs in data.items():
        p = np.array([a.mean() for a in arrs])
        pools = arrs
        N = len(p)
        res[name] = {"N": N, "mean_p": float(p.mean()),
                     "share_hopeless(p=0)": float((p == 0).mean()),
                     "share_trivial(p=1)": float((p == 1).mean())}
        print(f"\n== {name}: N={N} mean acc {p.mean():.3f} hopeless {res[name]['share_hopeless(p=0)']:.2f} "
              f"trivial {res[name]['share_trivial(p=1)']:.2f}", flush=True)
        for u in BUDGETS:
            S, K = u * N, 16 * u
            cu = coverage(p, u)
            co = coverage(p, oracle(p, S, K))
            row = {"uniform": cu, "oracle": co}
            for rname, k in rules(p, S, K).items():
                row[f"{rname} [true p]"] = coverage(p, k)
            # probe setting (charged), only when budget allows a probe
            if u > M_PROBE:
                acc = {}
                for _ in range(REPS):
                    s = np.array([rng.choice(a, M_PROBE, replace=True).sum() for a in pools])
                    ph = s / M_PROBE
                    for rname, k in rules(ph, S, K, kmin=M_PROBE).items():
                        if k is not None:
                            acc.setdefault(f"{rname} [probe]", []).append(coverage(p, k))
                    k_ias = np.maximum(ias(ph, S - M_PROBE * N, K) , 0)
                    acc.setdefault("E2 IAS [probe]", []).append(coverage(p, M_PROBE + k_ias - 1 + 1))
                    acc.setdefault("Bayes marginal [probe]", []).append(
                        coverage(p, bayes_marginal(s, M_PROBE, S, K)))
                for kk, v in acc.items():
                    row[kk] = float(np.mean(v))
            head = co - cu
            res[name][f"u{u}"] = {k: {"coverage": v, "gain_pts": 100 * (v - cu),
                                      "share_of_oracle": (v - cu) / head if head > 1e-9 else None}
                                  for k, v in row.items()}
            line = " | ".join(f"{k}: {100*(v-cu):+.1f}" for k, v in row.items() if k not in ("uniform",))
            print(f"  u={u:3d} uniform cov {cu:.3f} | {line}", flush=True)
    tag = "_hard" if "hard" in sys.argv else ""
    json.dump(res, open(f"paper4/e2/e2_cost{tag}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
