"""Setting 2 with an imperfect verifier.

Each attempt is a draw from the stored pool. The verifier accepts a correct attempt with prob 1 - fn
and an incorrect one with prob fp. An accepted input leaves the pool; it counts as solved only if the
accepted attempt is actually correct. Policies are NOT told about the noise (their posteriors assume a
perfect verifier), which is the realistic, misspecified case.
"""
import json
import sys
import numpy as np

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import mb, aligned, bins_mix
from e2_bandits_fast import pad

rng = np.random.default_rng(23)
REPS = 20
U = 16
FP = [0.0, 0.01, 0.02, 0.05, 0.10]
FN = [0.0, 0.2]
PAIRS = [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B"), ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B"),
         ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct"),
         ("CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct")]


def first_accept(samples, fp, fn, r):
    """Index (1-based) of the first accepted attempt and whether that attempt is correct."""
    A = np.full(len(samples), np.inf)
    ok = np.zeros(len(samples), bool)
    for i, s in enumerate(samples):
        c = s[r.permutation(len(s))]
        u = r.random(len(c))
        acc = np.where(c, u >= fn, u < fp)
        h = np.flatnonzero(acc)
        if len(h):
            A[i] = h[0] + 1
            ok[i] = c[h[0]]
    return A, ok


def rr(A, S):
    n = np.zeros(len(A))
    done = np.zeros(len(A), bool)
    left = int(S)
    while left > 0:
        act = np.flatnonzero(~done)
        if len(act) == 0:
            break
        take = act[:left]
        n[take] += 1
        left -= len(take)
        done[take] = A[take] <= n[take]
    return done


def ts(A, S, mix):
    M, W0 = pad(mix)
    N = len(A)
    logw = np.where(W0 > 0, np.log(np.maximum(W0, 1e-300)), -np.inf)
    log1m = np.log(np.clip(1 - M, 1e-12, 1))
    f = np.zeros(N)
    done = np.zeros(N, bool)
    for _ in range(int(S)):
        act = np.flatnonzero(~done)
        if len(act) == 0:
            break
        lw = logw[act] + f[act, None] * log1m[act]
        lw -= lw.max(1, keepdims=True)
        w = np.exp(lw)
        w /= w.sum(1, keepdims=True)
        j = (np.cumsum(w, 1) < rng.random(len(act))[:, None]).sum(1)
        i = act[int(np.argmax(M[act, np.minimum(j, M.shape[1] - 1)]))]
        f[i] += 1
        if A[i] <= f[i]:
            done[i] = True
    return done


def main():
    out = {}
    for t, r_ in PAIRS:
        tgt, ref = aligned(mb(t), mb(r_))
        p = np.array([s.mean() for s in tgt])
        sig = np.array([s.mean() for s in ref])
        N = len(p)
        S = U * N
        out[t] = {}
        for fn in FN:
            for fp in FP:
                acc = {}
                for _ in range(REPS):
                    perm = rng.permutation(N)
                    halves = [perm[: N // 2], perm[N // 2:]]
                    mix = [None] * N
                    for a, b in ((0, 1), (1, 0)):
                        for i, m in zip(halves[b], bins_mix(p[halves[a]], sig[halves[a]], sig[halves[b]])):
                            mix[i] = m
                    A, ok = first_accept(tgt, fp, fn, rng)
                    for name, done in (("RR", rr(A, S)), ("TS (exchangeable)", ts(A, S, [p] * N)),
                                       ("TS (history)", ts(A, S, mix))):
                        acc.setdefault(name, []).append((done & ok).mean())
                        acc.setdefault(name + " false-accept", []).append((done & ~ok).mean())
                key = f"fn={fn},fp={fp}"
                res = {k: float(np.mean(v)) for k, v in acc.items()}
                res["TS (history) gain sd"] = float(np.std(np.array(acc["TS (history)"]) - np.array(acc["RR"])))
                out[t][key] = res
                b = res["RR"]
                print(f"{t:34} {key:14} | RR solved {100*b:5.1f}% (false {100*res['RR false-accept']:4.1f}%) | "
                      f"TS-exch {100*(res['TS (exchangeable)']-b):+5.1f} | TS-hist {100*(res['TS (history)']-b):+5.1f} "
                      f"(false {100*res['TS (history) false-accept']:4.1f}%)", flush=True)
                json.dump(out, open("paper4/e2/e2_noisy_verifier.json", "w"), indent=1)


if __name__ == "__main__":
    main()
