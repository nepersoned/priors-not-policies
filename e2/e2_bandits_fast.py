"""Vectorized bandit baselines for Setting 2 (TS / UCB with exchangeable or history prior).
Each problem's prior is an empirical mixture of pass rates, padded to a common length with zero weight.
Only the attempted problem's posterior is updated each step; TS draws for all problems at once."""
import json
import sys
import numpy as np

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import mb, aligned, first_success, rr, bayes, bins_mix

rng = np.random.default_rng(15)
U = [4, 16, 64]
REPS = 20


def pad(mix):
    L = max(len(m) for m in mix)
    M = np.zeros((len(mix), L))
    W = np.zeros((len(mix), L))
    for i, m in enumerate(mix):
        M[i, : len(m)] = m
        W[i, : len(m)] = 1.0 / len(m)
    return M, W


def run(T, S, mix, kind, c=1.0):
    M, W0 = pad(mix)
    N = len(T)
    logw = np.where(W0 > 0, np.log(np.maximum(W0, 1e-300)), -np.inf)
    log1m = np.log(np.clip(1 - M, 1e-12, 1))
    f = np.zeros(N)
    solved = np.zeros(N, bool)

    def post(rows):
        lw = logw[rows] + f[rows, None] * log1m[rows]
        lw -= lw.max(1, keepdims=True)
        w = np.exp(lw)
        return w / w.sum(1, keepdims=True)

    if kind == "ucb":
        w = post(np.arange(N))
        mu = (w * M).sum(1)
        idx = mu + c * np.sqrt(np.maximum((w * (M - mu[:, None]) ** 2).sum(1), 0))
    for _ in range(int(S)):
        act = np.flatnonzero(~solved)
        if len(act) == 0:
            break
        if kind == "ts":
            w = post(act)
            cdf = np.cumsum(w, 1)
            j = (cdf < rng.random(len(act))[:, None]).sum(1)
            draw = M[act, np.minimum(j, M.shape[1] - 1)]
            i = act[int(np.argmax(draw))]
        else:
            i = act[int(np.argmax(idx[act]))]
        f[i] += 1
        if T[i] <= f[i]:
            solved[i] = True
        elif kind == "ucb":
            w = post(np.array([i]))[0]
            mu = (w * M[i]).sum()
            idx[i] = mu + c * np.sqrt(max((w * (M[i] - mu) ** 2).sum(), 0))
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
                     "TS (exchangeable)": run(T, S, exch, "ts"),
                     "UCB (exchangeable)": run(T, S, exch, "ucb"),
                     "TS (history)": run(T, S, mix, "ts"),
                     "UCB (history)": run(T, S, mix, "ucb"),
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
