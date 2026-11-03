"""Replicate the main results on freshly generated samples (Colab, vLLM, Qwen2.5 family, hard MATH-500 problems).

Static: share of the oracle gain captured by IAS / k ∝ 1-p / tiers at u = 16 (true pass rates given).
Online: TS / UCB with the history prior (related model's pass rates) vs RR, 100 replays, bootstrap CIs."""
import json, sys
import numpy as np

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import first_success, rr, bins_mix
from e2_bandits_fast import run as bandit

rng = np.random.default_rng(101)
files = ["paper4/colab/live_samples_small.json", "paper4/colab/live_samples_7b.json"]
models = {}
for f in files:
    try:
        d = json.load(open(f))
        for k, v in d["models"].items():
            models[k] = [np.array(x["correct"], bool) for x in v]
    except FileNotFoundError:
        pass
short = {"Qwen/Qwen2.5-0.5B-Instruct": "0.5B", "Qwen/Qwen2.5-Math-1.5B-Instruct": "Math-1.5B", "Qwen/Qwen2.5-Math-7B-Instruct": "Math-7B"}
P = {short[k]: np.array([s.mean() for s in v]) for k, v in models.items()}
S_ = {short[k]: v for k, v in models.items()}
for k, p in P.items():
    print(f"{k:10} mean p {p.mean():.3f} | p=0 share {np.mean(p == 0):.2f} | solved-ever {np.mean(p > 0):.2f}")

from scipy.stats import spearmanr
pairs = [("0.5B", "Math-1.5B")] + ([("0.5B", "Math-7B"), ("Math-1.5B", "Math-7B")] if "Math-7B" in P else [])
out = {}
for tgt, ref in pairs:
    p, sig, samples = P[tgt], P[ref], S_[tgt]
    N = len(p)
    rho = float(spearmanr(p, sig).correlation)
    for u in (4, 16):
        S = u * N
        g = {"TS": [], "UCB": [], "TS-exch": []}
        base_all = []
        for _ in range(100):
            perm = rng.permutation(N); halves = [perm[: N // 2], perm[N // 2:]]
            mix = [None] * N
            for a, b in ((0, 1), (1, 0)):
                for i, m in zip(halves[b], bins_mix(p[halves[a]], sig[halves[a]], sig[halves[b]])):
                    mix[i] = m
            T = first_success(samples, rng); base = rr(T, S); base_all.append(base)
            g["TS"].append(bandit(T, S, mix, "ts") - base)
            g["UCB"].append(bandit(T, S, mix, "ucb") - base)
            g["TS-exch"].append(bandit(T, S, [p] * N, "ts") - base)
        res = {"rho": rho, "RR": 100 * float(np.mean(base_all))}
        for k, v in g.items():
            v = np.array(v); bs = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(2000)]
            res[k] = [100 * float(v.mean()), 100 * float(np.percentile(bs, 2.5)), 100 * float(np.percentile(bs, 97.5))]
        out[f"{tgt}<-{ref}|u={u}"] = res
        print(f"{tgt:9} <- {ref:9} rho {rho:+.2f} u={u:2d} | RR {res['RR']:5.1f}% | " +
              " | ".join(f"{k} {res[k][0]:+.1f} [{res[k][1]:+.1f},{res[k][2]:+.1f}]" for k in g), flush=True)
json.dump(out, open("paper4/e2/e2_live.json", "w"), indent=1)
