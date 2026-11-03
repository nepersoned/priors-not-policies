"""Prior-calibrated verification: use the history prior for verification as well as allocation.

For a sample with reward-model score s on input i, the posterior probability that it is correct is
    q = p_i f1(s) / (p_i f1(s) + (1 - p_i) f0(s)),
where p_i is the input's prior mean pass rate (history prior, cross-fitted) and f1, f0 are the score densities of
correct and incorrect samples estimated on the calibration half. Accept if q >= theta.

Compared acceptance rules (all with the same allocation policies, RR and TS-history):
  global-FA : one score threshold for all inputs, set so that alpha of incorrect calibration samples are accepted;
  bayes-flat: the posterior rule with a single global p (no input-specific prior);
  bayes-prior: the posterior rule with the input's history-prior mean p_i.
Reported: share truly solved, share falsely accepted, precision. Llama-3.1-8B on hard MATH500 / GPQA, prior from 70B."""
import json, sys
import numpy as np
from scipy.stats import gaussian_kde

sys.path.insert(0, "paper4/e2")
import e2_real_verifier as R
from e2_online_v2 import bins_mix
from e2_noisy_verifier import rr, ts

rng = np.random.default_rng(97)
REPS = 10
CFG = {"MATH500": ["QwenPRM_min_scores", "InternLM2Reward7B_scores"], "GPQA": ["ArmorRM_scores", "QwenPRM_min_scores"]}


def first_accept(recs, accept_fn, r):
    A = np.full(len(recs), np.inf); ok = np.zeros(len(recs), bool)
    for i, rec in enumerate(recs):
        o = r.permutation(len(rec["c"]))
        acc = accept_fn(i, o)
        h = np.flatnonzero(acc)
        if len(h):
            A[i] = h[0] + 1; ok[i] = rec["c"][o][h[0]]
    return A, ok


out = {}
for task, rms in CFG.items():
    T8, T70 = R.load(task, "8B", rms), R.load(task, "70B", [])
    keys = [k for k in T8 if k in T70 and all(rm in T8[k] for rm in rms) and T8[k]["c"].mean() < 0.3]
    recs = [T8[k] for k in keys]
    p = np.array([r["c"].mean() for r in recs]); sig = np.array([T70[k]["c"].mean() for k in keys])
    N = len(p)
    out[task] = {}
    for rm in rms:
        for u in (2, 4, 8):
            S = u * N
            acc = {}
            for _ in range(REPS):
                perm = rng.permutation(N); cal, tst = perm[: N // 2], perm[N // 2:]
                mix = [None] * N
                for a, b in ((cal, tst), (tst, cal)):
                    for i, m in zip(b, bins_mix(p[a], sig[a], sig[b])):
                        mix[i] = m
                pm = np.array([m.mean() for m in mix])
                # score densities from the calibration half (cross-fit symmetric: use both halves' complements)
                def dens(idx):
                    s1 = np.concatenate([recs[i][rm][recs[i]["c"]] for i in idx]); s0 = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in idx])
                    s1, s0 = s1[np.isfinite(s1)], s0[np.isfinite(s0)]
                    return gaussian_kde(s1), gaussian_kde(s0), s0
                d_for = {}
                d_cal, d_tst = dens(cal), dens(tst)
                for i in tst: d_for[i] = d_cal
                for i in cal: d_for[i] = d_tst
                pbar = p[cal].mean()
                rules = {}
                for alpha in (0.01, 0.05):
                    taus = {id(d): np.quantile(d[2], 1 - alpha) for d in (d_cal, d_tst)}
                    rules[f"global-FA{int(alpha*100)}"] = lambda i, o, taus=taus: np.nan_to_num(recs[i][rm][o], nan=-np.inf) >= taus[id(d_for[i])]
                def post(i, o, prior):
                    f1, f0, _ = d_for[i]
                    s = np.nan_to_num(recs[i][rm][o], nan=np.nanmin(recs[i][rm]))
                    l1, l0 = f1(s), f0(s)
                    return prior * l1 / (prior * l1 + (1 - prior) * l0 + 1e-300)
                for theta in (0.5,):
                    rules["bayes-flat"] = lambda i, o: post(i, o, pbar) >= theta
                    rules["bayes-prior"] = lambda i, o: post(i, o, max(pm[i], 1e-3)) >= theta
                for name, fn in rules.items():
                    A, ok = first_accept(recs, fn, rng)
                    for pol, done in (("RR", rr(A, S)), ("TS", ts(A, S, mix))):
                        acc.setdefault(f"{name}|{pol}|true", []).append((done & ok).mean())
                        acc.setdefault(f"{name}|{pol}|false", []).append((done & ~ok).mean())
            res = {k: float(np.mean(v)) for k, v in acc.items()}
            out[task][f"{rm}|u={u}"] = res
            line = []
            for name in ("global-FA1", "global-FA5", "bayes-flat", "bayes-prior"):
                tt, ff = res[f"{name}|TS|true"], res[f"{name}|TS|false"]
                line.append(f"{name}: TS true {100*tt:4.1f} false {100*ff:4.1f} prec {100*tt/max(tt+ff,1e-9):3.0f}% (RR true {100*res[name+'|RR|true']:4.1f})")
            print(f"{task:7} {rm:24} u={u} | " + " | ".join(line), flush=True)
            json.dump(out, open("paper4/e2/e2_prior_verify.json", "w"), indent=1)
