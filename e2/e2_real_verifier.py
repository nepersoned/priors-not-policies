"""Setting 2 with a real learned verifier (Weaver stored reward-model scores).

Target: Llama-3.1-8B samples (100 per problem) on GPQA and MATH500; history prior from Llama-3.1-70B
pass rates on the same problems. The verifier accepts an attempt when its reward-model score is at
least tau. tau is set on a calibration half of the problems so that a target share alpha of *incorrect*
calibration samples is accepted; the realized false/true acceptance rates are measured on the test half.
An accepted input leaves the pool and counts as solved only if the accepted sample is correct.
Policies assume a perfect verifier (misspecified), as in e2_noisy_verifier.py.
"""
import json
import re
import sys
import glob
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import bins_mix
from e2_noisy_verifier import rr, ts

D = "paper4/data_ext/"
rng = np.random.default_rng(41)
REPS = 20
U = 16
ALPHAS = [0.01, 0.05]
RMS = ["weaver_scores", "Skyworks_scores", "ArmorRM_scores"]
norm = lambda s: re.sub(r"\s+", " ", str(s or "")).strip()


def load(task, size, cols):
    out = {}
    for f in sorted(glob.glob(D + f"weaver_{task}_{size}_*.parquet")):
        names = pq.ParquetFile(f).schema_arrow.names
        key = "problem" if "problem" in names else "instruction"
        have = [c for c in cols if c in names]
        t = pq.read_table(f, columns=[key, "answer_correct"] + have)
        for j, k in enumerate(t.column(key).to_pylist()):
            ac = t.column("answer_correct")[j].as_py()
            if not ac:
                continue
            rec = {"c": np.asarray(ac, bool)}
            for c in have:
                v = t.column(c)[j].as_py()
                if v is not None and len(v) == len(ac):
                    rec[c] = np.asarray([np.nan if x is None else x for x in v], float)
            out[norm(k)] = rec
    return out


def first_accept_rm(recs, score_key, tau, r):
    A = np.full(len(recs), np.inf)
    ok = np.zeros(len(recs), bool)
    for i, rec in enumerate(recs):
        o = r.permutation(len(rec["c"]))
        acc = np.nan_to_num(rec[score_key][o], nan=-np.inf) >= tau
        h = np.flatnonzero(acc)
        if len(h):
            A[i] = h[0] + 1
            ok[i] = rec["c"][o][h[0]]
    return A, ok


def main():
    out = {}
    for task in ["GPQA", "MATH500"]:
        T8 = load(task, "8B", RMS)
        T70 = load(task, "70B", [])
        keys = [k for k in T8 if k in T70 and all(rm in T8[k] for rm in RMS)]
        recs = [T8[k] for k in keys]
        p = np.array([r["c"].mean() for r in recs])
        sig = np.array([T70[k]["c"].mean() for k in keys])
        N = len(p)
        S = U * N
        out[task] = {"N": N, "mean_p": float(p.mean())}
        print(task, "N", N, "mean p %.3f" % p.mean(), flush=True)
        for rm in RMS:
            for alpha in ALPHAS:
                acc = {}
                for _ in range(REPS):
                    perm = rng.permutation(N)
                    cal, tst = perm[: N // 2], perm[N // 2:]
                    wrong_cal = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in cal])
                    wrong_cal = wrong_cal[np.isfinite(wrong_cal)]
                    tau = np.quantile(wrong_cal, 1 - alpha)
                    wt = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in tst])
                    ct = np.concatenate([recs[i][rm][recs[i]["c"]] for i in tst])
                    acc.setdefault("FA", []).append(float(np.mean(wt[np.isfinite(wt)] >= tau)))
                    acc.setdefault("TA", []).append(float(np.mean(ct[np.isfinite(ct)] >= tau)))
                    mix = [None] * N
                    for a, b in ((cal, tst), (tst, cal)):
                        for i, m in zip(b, bins_mix(p[a], sig[a], sig[b])):
                            mix[i] = m
                    A, ok = first_accept_rm(recs, rm, tau, rng)
                    # perfect-verifier reference on the same orderings is not identical; use separate draw
                    for name, done in (("RR", rr(A, S)), ("TS (history)", ts(A, S, mix))):
                        acc.setdefault(name, []).append((done & ok).mean())
                        acc.setdefault(name + " false", []).append((done & ~ok).mean())
                res = {k: float(np.mean(v)) for k, v in acc.items()}
                g = np.array(acc["TS (history)"]) - np.array(acc["RR"])
                res["gain"] = float(g.mean())
                res["gain_ci95"] = [float(np.percentile([g[rng.integers(0, len(g), len(g))].mean() for _ in range(2000)], q)) for q in (2.5, 97.5)]
                out[task][f"{rm}|alpha={alpha}"] = res
                print(f"  {rm:16} a={alpha:.2f} | FA {100*res['FA']:4.1f}% TA {100*res['TA']:4.1f}% | RR {100*res['RR']:5.1f}% "
                      f"(false {100*res['RR false']:4.1f}%) | TS-hist {100*res['gain']:+5.1f} [{100*res['gain_ci95'][0]:+.1f},{100*res['gain_ci95'][1]:+.1f}]",
                      flush=True)
                json.dump(out, open("paper4/e2/e2_real_verifier.json", "w"), indent=1)
        # perfect-verifier reference
        acc = []
        from e2_noisy_verifier import first_accept
        for _ in range(REPS):
            perm = rng.permutation(N)
            cal, tst = perm[: N // 2], perm[N // 2:]
            mix = [None] * N
            for a, b in ((cal, tst), (tst, cal)):
                for i, m in zip(b, bins_mix(p[a], sig[a], sig[b])):
                    mix[i] = m
            A, ok = first_accept([r["c"] for r in recs], 0.0, 0.0, rng)
            acc.append(((ts(A, S, mix) & ok).mean(), (rr(A, S) & ok).mean()))
        acc = np.array(acc)
        out[task]["perfect"] = {"RR": float(acc[:, 1].mean()), "gain": float((acc[:, 0] - acc[:, 1]).mean())}
        print(f"  perfect verifier | RR {100*acc[:,1].mean():5.1f}% | TS-hist {100*(acc[:,0]-acc[:,1]).mean():+5.1f}", flush=True)
        json.dump(out, open("paper4/e2/e2_real_verifier.json", "w"), indent=1)


if __name__ == "__main__":
    main()
