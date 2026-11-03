"""Bandit baselines for Setting 2 (reviewer request): Thompson Sampling and UCB, each with
(a) an exchangeable prior and (b) the same history prior used by Bayes-myopic.
Prior = empirical mixture of pass rates; posterior after f failures reweights components by (1-p)^f."""
import json
import sys
import numpy as np

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import mb, aligned, first_success, rr, bayes, bins_mix

rng = np.random.default_rng(15)
U = [4, 16, 64]
REPS = 20


def post(m, w0, f):
    w = w0 * (1 - m) ** f
    s = w.sum()
    return (w / s) if s > 0 else np.full(len(m), 1 / len(m))


def run_index(T, S, mix, kind, c=1.0):
    N = len(T)
    f = np.zeros(N, int)
    solved = np.zeros(N, bool)
    W0 = [np.ones(len(m)) / len(m) for m in mix]
    for t in range(int(S)):
        idx = np.full(N, -1.0)
        for i in np.flatnonzero(~solved):
            w = post(mix[i], W0[i], f[i])
            if kind == "ts":
                idx[i] = mix[i][rng.choice(len(w), p=w)]
            else:  # ucb on the posterior of p
                mu = (w * mix[i]).sum()
                sd = np.sqrt(max((w * (mix[i] - mu) ** 2).sum(), 0))
                idx[i] = mu + c * sd
        i = int(np.argmax(idx))
        if idx[i] < 0:
            break
        f[i] += 1
        if T[i] <= f[i]:
            solved[i] = True
    return float(solved.mean())


def main():
    pairs = [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B"), ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B"),
             ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct"),
             ("CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct"),
             ("MiniF2F-MATH_Llama-3-8B-Instruct", "MiniF2F-MATH_Llama-3-70B-Instruct"),
             ("MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct")]
    out = {}
    for t, r_ in pairs:
        tgt, ref = aligned(mb(t), mb(r_))
        p = np.array([s.mean() for s in tgt])
        sig = np.array([s.mean() for s in ref])
        N = len(p)
        out[t] = {}
        for u in U:
            S = u * N
            acc = {}
            for _ in range(REPS):
                perm = rng.permutation(N)
                halves = [perm[: N // 2], perm[N // 2:]]
                mix = [None] * N
                for a, b in ((0, 1), (1, 0)):
                    for i, m in zip(halves[b], bins_mix(p[halves[a]], sig[halves[a]], sig[halves[b]])):
                        mix[i] = m
                exch = [p] * N
                T = first_success(tgt, rng)
                r = {"RR": rr(T, S),
                     "TS (exchangeable)": run_index(T, S, exch, "ts"),
                     "UCB (exchangeable)": run_index(T, S, exch, "ucb"),
                     "TS (history)": run_index(T, S, mix, "ts"),
                     "UCB (history)": run_index(T, S, mix, "ucb"),
                     "Bayes-myopic (history)": bayes(T, S, mix)}
                for k, v in r.items():
                    acc.setdefault(k, []).append(v)
            out[t][u] = {k: float(np.mean(v)) for k, v in acc.items()}
            base = out[t][u]["RR"]
            print(f"{t:34} u={u:3d} | RR {100*base:5.1f}% | " +
                  " ".join(f"{k}: {100*(v-base):+5.1f}" for k, v in out[t][u].items() if k != "RR"), flush=True)
            json.dump(out, open("paper4/e2/e2_bandits.json", "w"), indent=1)


if __name__ == "__main__":
    main()
