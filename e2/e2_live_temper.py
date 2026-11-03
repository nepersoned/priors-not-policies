"""Tempered history prior for TS on the live samples: the prior for input i is a mixture of its history-bin
distribution (weight w) and the exchangeable distribution (weight 1 - w). w = 1 is the plain history prior,
w = 0 is the exchangeable prior (equivalent to RR). Also an automatic choice of w by 2-fold CV on the calibration
half (pick the w with the highest solved share in a replay on calibration inputs)."""
import json, sys
import numpy as np

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import first_success, rr, bins_mix

rng = np.random.default_rng(113)
models = {}
for f in ["paper4/colab/live_samples_small.json", "paper4/colab/live_samples_7b.json"]:
    d = json.load(open(f))
    for k, v in d["models"].items():
        models[k.split("/")[-1]] = [np.array(x["correct"], bool) for x in v]
P = {k: np.array([s.mean() for s in v]) for k, v in models.items()}


def ts_weighted(T, S, vals, wts):
    """TS with per-input discrete priors given as (values, weights) arrays (padded)."""
    N = len(T)
    L = max(len(v) for v in vals)
    M = np.zeros((N, L)); W = np.zeros((N, L))
    for i, (v, w) in enumerate(zip(vals, wts)):
        M[i, :len(v)] = v; W[i, :len(v)] = w / w.sum()
    logw = np.where(W > 0, np.log(np.maximum(W, 1e-300)), -np.inf)
    log1m = np.log(np.clip(1 - M, 1e-12, 1))
    f = np.zeros(N); done = np.zeros(N, bool)
    for _ in range(int(S)):
        act = np.flatnonzero(~done)
        if len(act) == 0:
            break
        lw = logw[act] + f[act, None] * log1m[act]
        lw -= lw.max(1, keepdims=True)
        w = np.exp(lw); w /= w.sum(1, keepdims=True)
        j = (np.cumsum(w, 1) < rng.random(len(act))[:, None]).sum(1)
        i = act[int(np.argmax(M[act, np.minimum(j, L - 1)]))]
        f[i] += 1
        if T[i] <= f[i]:
            done[i] = True
    return done.mean()


def prior(mix_i, exch, w):
    v = np.concatenate([mix_i, exch])
    wt = np.concatenate([np.full(len(mix_i), w / len(mix_i)), np.full(len(exch), (1 - w) / len(exch))])
    keep = wt > 0
    return v[keep], wt[keep]


W_GRID = [0.0, 0.25, 0.5, 0.75, 1.0]
out = {}
for tgt, ref in [("Qwen2.5-0.5B-Instruct", "Qwen2.5-Math-1.5B-Instruct"), ("Qwen2.5-Math-1.5B-Instruct", "Qwen2.5-Math-7B-Instruct")]:
    p, sig, samples = P[tgt], P[ref], models[tgt]
    N = len(p)
    for u in (4, 16):
        S = u * N
        acc = {}
        for _ in range(30):
            perm = rng.permutation(N); halves = [perm[: N // 2], perm[N // 2:]]
            mix = [None] * N
            for a, b in ((0, 1), (1, 0)):
                for i, m in zip(halves[b], bins_mix(p[halves[a]], sig[halves[a]], sig[halves[b]])):
                    mix[i] = m
            T = first_success(samples, rng); base = rr(T, S)
            for w in W_GRID:
                vals, wts = zip(*[prior(mix[i], p[halves[0] if i in set(halves[1]) else halves[1]], w) for i in range(N)])
                acc.setdefault(f"w={w}", []).append(ts_weighted(T, S, vals, wts) - base)
            # CV choice of w on each calibration half: replay restricted to calibration inputs
            chosen = {}
            for h in (0, 1):
                cal = halves[h]
                Tc = first_success([samples[i] for i in cal], rng); Sc = u * len(cal)
                pc, sc = p[cal], sig[cal]
                sub = rng.permutation(len(cal)); sh = [sub[: len(cal) // 2], sub[len(cal) // 2:]]
                mixc = [None] * len(cal)
                for a, b in ((0, 1), (1, 0)):
                    for i, m in zip(sh[b], bins_mix(pc[sh[a]], sc[sh[a]], sc[sh[b]])):
                        mixc[i] = m
                best = max(W_GRID, key=lambda w: ts_weighted(Tc, Sc, *zip(*[prior(mixc[i], pc, w) for i in range(len(cal))])))
                chosen[h] = best
            wi = [chosen[0] if i in set(halves[1]) else chosen[1] for i in range(N)]
            vals, wts = zip(*[prior(mix[i], p[halves[0] if i in set(halves[1]) else halves[1]], wi[i]) for i in range(N)])
            acc.setdefault("CV-tempered", []).append(ts_weighted(T, S, vals, wts) - base)
            acc.setdefault("chosen_w", []).append(np.mean(wi))
        res = {k: 100 * float(np.mean(v)) if k != "chosen_w" else float(np.mean(v)) for k, v in acc.items()}
        out[f"{tgt}<-{ref}|u={u}"] = res
        print(f"{tgt[:14]:14} <- {ref[:18]:18} u={u:2d} | " + " | ".join(f"{k} {v:+.1f}" if k != "chosen_w" else f"w̄ {v:.2f}" for k, v in res.items()), flush=True)
json.dump(out, open("paper4/e2/e2_live_temper.json", "w"), indent=1)
