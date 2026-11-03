"""Setting 2 (verifier available): sequential allocation with stop-on-success.

Each problem's stored samples are replayed in a random order; drawing a sample costs 1;
a problem is solved at its first correct sample. Total budget S = u*N. Metric: share solved.

Policies
  static uniform      : u samples each, no stopping (Setting-1 reference)
  RR-unsolved         : round-robin over unsolved problems (optimal with exchangeable prior)
  E2 online (IAS cap) : sample-until-success up to IAS cap k_i from history p_hat (harder -> larger cap),
                        leftover budget round-robin over unsolved
  Bayes myopic        : next sample to the unsolved problem with the highest posterior P(success next),
                        prior = mixture of calibration problems' pass rates in the same history bin
                        (deteriorating index -> myopic is optimal for maximizing #solved)
  Bayes myopic (exch.): same with an exchangeable empirical-Bayes prior (no history) -- sanity: ~= RR
History signal: another model's pass rate on the same problems, 2-fold cross-fitted calibration.
"""
import json
import sys
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/e2")
from e2_cost import ias

D = "paper4/data_ext/"
rng = np.random.default_rng(11)
U = [4, 16, 64]
REPS = 20


def load(cfg):
    x = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()
    return [np.asarray(v, bool) for v in x]


def first_success_times(samples, rng):
    """For each problem: index (1-based) of first success in a random order; inf if none."""
    out = np.empty(len(samples))
    for i, s in enumerate(samples):
        perm = rng.permutation(len(s))
        hits = np.flatnonzero(s[perm])
        out[i] = hits[0] + 1 if len(hits) else np.inf
    return out


def run_static_uniform(T, u):
    return float(np.mean(T <= u))


def run_rr(T, S):
    """Round-robin over unsolved: equivalent to giving each unsolved problem one more sample per round."""
    n = np.zeros(len(T))
    solved = np.zeros(len(T), bool)
    left = S
    while left > 0:
        active = np.flatnonzero(~solved)
        if len(active) == 0:
            break
        take = active[:left]
        n[take] += 1
        left -= len(take)
        solved[take] = T[take] <= n[take]
    return float(solved.mean())


def run_e2(T, S, phat, K):
    caps = ias(phat, S, K)
    n = np.zeros(len(T))
    solved = np.zeros(len(T), bool)
    left = S
    # phase 1: sample-until-success up to cap
    for i in range(len(T)):
        use = int(min(caps[i], T[i])) if np.isfinite(T[i]) else int(caps[i])
        use = int(min(use, left))
        n[i] = use
        left -= use
        solved[i] = T[i] <= n[i]
        if left <= 0:
            break
    # phase 2: leftover round-robin over unsolved
    while left > 0:
        active = np.flatnonzero(~solved)
        if len(active) == 0:
            break
        take = active[:left]
        n[take] += 1
        left -= len(take)
        solved[take] = T[take] <= n[take]
    return float(solved.mean())


def run_bayes(T, S, mix_p):
    """mix_p: list of arrays; prior for problem i = empirical mixture of pass rates mix_p[i].
    Index after f failures: E[p (1-p)^f] / E[(1-p)^f]."""
    N = len(T)
    f = np.zeros(N, int)
    solved = np.zeros(N, bool)
    idx = np.array([m.mean() for m in mix_p])
    for _ in range(S):
        cand = np.where(solved, -1.0, idx)
        i = int(np.argmax(cand))
        if cand[i] < 0:
            break
        f[i] += 1
        if T[i] <= f[i]:
            solved[i] = True
        else:
            m = mix_p[i]
            w = (1 - m) ** f[i]
            idx[i] = float((m * w).sum() / w.sum()) if w.sum() > 0 else 0.0
    return float(solved.mean())


def calib_mix(p_target, signal, nbins=5):
    """2-fold cross-fit: for each problem, the calibration-half problems in its signal bin."""
    N = len(p_target)
    perm = rng.permutation(N)
    halves = [perm[: N // 2], perm[N // 2:]]
    mix, phat = [None] * N, np.empty(N)
    for a, b in ((0, 1), (1, 0)):
        cal, tst = halves[a], halves[b]
        edges = np.unique(np.quantile(signal[cal], np.linspace(0, 1, nbins + 1)[1:-1]))
        bc, bt = np.digitize(signal[cal], edges), np.digitize(signal[tst], edges)
        for i, t in zip(tst, bt):
            pool = cal[bc == t] if np.any(bc == t) else cal
            mix[i] = p_target[pool]
            phat[i] = p_target[pool].mean()
    return mix, phat


def main():
    pairs = [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B"), ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B"),
             ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct"),
             ("MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct"),
             ("MATH_Llama-3-70B-Instruct", "MATH_Llama-3-8B-Instruct"),
             ("CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct"),
             ("CodeContests_Llama-3-70B-Instruct", "CodeContests_Llama-3-8B-Instruct")]
    cache = {}
    res = {}
    for tgt, ref in pairs:
        for c in (tgt, ref):
            if c not in cache:
                cache[c] = load(c)
        smp = cache[tgt]
        p = np.array([s.mean() for s in smp])
        sig = np.array([s.mean() for s in cache[ref]])
        N = len(p)
        res[f"{tgt} <- {ref}"] = {}
        for u in U:
            S, K = u * N, 16 * u
            acc = {}
            for _ in range(REPS):
                T = first_success_times(smp, rng)
                mix, phat = calib_mix(p, sig)
                exch = [p] * N            # exchangeable prior: all problems' pass rates (oracle-ish pool)
                r = {"static uniform": run_static_uniform(T, u),
                     "RR-unsolved": run_rr(T, S),
                     "E2 online (IAS cap)": run_e2(T, S, phat, K),
                     "Bayes myopic (history prior)": run_bayes(T, S, mix),
                     "Bayes myopic (exchangeable)": run_bayes(T, S, exch),
                     # tempered: half history-bin mixture, half exchangeable pool (equal mass)
                     "Bayes myopic (tempered)": run_bayes(
                         T, S, [np.concatenate([m, rng.choice(p, len(m), replace=True)]) for m in mix])}
                for k, v in r.items():
                    acc.setdefault(k, []).append(v)
            res[f"{tgt} <- {ref}"][u] = {k: [float(np.mean(v)), float(np.std(v) / np.sqrt(len(v)))]
                                         for k, v in acc.items()}
            row = res[f"{tgt} <- {ref}"][u]
            base = row["RR-unsolved"][0]
            print(f"{tgt:34} <- {ref:28} u={u:3d} | RR {100*base:5.1f}% | " +
                  " ".join(f"{k}: {100*(v[0]-base):+5.1f}" for k, v in row.items() if k != "RR-unsolved"),
                  flush=True)
    json.dump(res, open("paper4/e2/e2_online.json", "w"), indent=1)


if __name__ == "__main__":
    main()
