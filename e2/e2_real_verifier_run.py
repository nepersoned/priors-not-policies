"""Phase 2: online allocation with the best available real reward model per task (from phase 1),
plus a perfect-verifier reference on the same problems. 10 replays per cell.
Workload = problems the 8B model solves less than 30% of the time (MATH500 at u = 16 is otherwise ~99% solved)."""
import json
import sys
import numpy as np

sys.path.insert(0, "paper4/e2")
import e2_real_verifier as R
from e2_online_v2 import bins_mix
from e2_noisy_verifier import rr, ts, first_accept

R.rng = rng = np.random.default_rng(47)
REPS = 10
U = int(sys.argv[1]) if len(sys.argv) > 1 else 16
CFG = {"MATH500": ["QwenPRM_min_scores", "InternLM2Reward7B_scores"], "GPQA": ["ArmorRM_scores", "QwenPRM_min_scores"]}
out = {}
for task, rms in CFG.items():
    T8, T70 = R.load(task, "8B", rms), R.load(task, "70B", [])
    keys = [k for k in T8 if k in T70 and all(rm in T8[k] for rm in rms) and T8[k]["c"].mean() < 0.3]  # hard subset
    recs = [T8[k] for k in keys]
    p = np.array([r["c"].mean() for r in recs]); sig = np.array([T70[k]["c"].mean() for k in keys])
    N = len(p); S = U * N
    out[task] = {"N": N, "mean_p": float(p.mean())}
    cells = [("perfect", None, None)] + [(rm, rm, a) for rm in rms for a in (0.01, 0.05)]
    for name, rm, alpha in cells:
        acc = {}
        for _ in range(REPS):
            perm = rng.permutation(N); cal, tst = perm[: N // 2], perm[N // 2:]
            mix = [None] * N
            for a, b in ((cal, tst), (tst, cal)):
                for i, m in zip(b, bins_mix(p[a], sig[a], sig[b])):
                    mix[i] = m
            if rm is None:
                A, ok = first_accept([r["c"] for r in recs], 0.0, 0.0, rng)
            else:
                w = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in cal]); w = w[np.isfinite(w)]
                A, ok = R.first_accept_rm(recs, rm, np.quantile(w, 1 - alpha), rng)
            for pol, done in (("RR", rr(A, S)), ("TS", ts(A, S, mix))):
                acc.setdefault(pol, []).append((done & ok).mean())
                acc.setdefault(pol + " false", []).append((done & ~ok).mean())
        g = np.array(acc["TS"]) - np.array(acc["RR"])
        res = {k: float(np.mean(v)) for k, v in acc.items()}
        res["gain"] = float(g.mean())
        res["gain_ci95"] = [float(np.percentile([g[rng.integers(0, len(g), len(g))].mean() for _ in range(2000)], q)) for q in (2.5, 97.5)]
        key = name if rm is None else f"{rm}|alpha={alpha}"
        out[task][key] = res
        print(f"{task:8} {key:34} RR {100*res['RR']:5.1f}% (false {100*res['RR false']:4.1f}%) | TS gain {100*res['gain']:+5.1f} "
              f"[{100*res['gain_ci95'][0]:+.1f},{100*res['gain_ci95'][1]:+.1f}]", flush=True)
        json.dump(out, open(f"paper4/e2/e2_real_verifier_run_u{U}.json", "w"), indent=1)
