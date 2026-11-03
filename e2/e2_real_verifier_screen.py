"""Phase 1 of the real-verifier test: how well do stored reward models separate correct from incorrect
samples of Llama-3.1-8B on GPQA and MATH500?

For each RM and target false-acceptance rate alpha, tau is the (1 - alpha) quantile of scores of incorrect
samples on a random half of the problems; FA and TA (true acceptance) are measured on the other half.
Also reports AUROC (correct vs incorrect samples), overall and on hard problems (8B pass rate < 0.2).
"""
import json
import sys
import numpy as np
from scipy.stats import rankdata

sys.path.insert(0, "paper4/e2")
from e2_real_verifier import load

rng = np.random.default_rng(43)
RMS = ["weaver_scores", "Skyworks_scores", "ArmorRM_scores", "QRM_scores", "GRM_scores", "URM_scores",
       "INFORM_scores", "Qwen72B_scores", "QwenPRM_min_scores", "EurusPRMStage2_min_scores", "InternLM2Reward7B_scores"]


def auroc(pos, neg):
    x = np.concatenate([pos, neg])
    r = rankdata(x)
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


out = {}
for task in ["GPQA", "MATH500"]:
    T8 = load(task, "8B", RMS)
    keys = list(T8)
    p = np.array([T8[k]["c"].mean() for k in keys])
    out[task] = {"N": len(keys), "mean_p": float(p.mean())}
    print(task, "N", len(keys), "mean p %.3f" % p.mean())
    for rm in RMS:
        ks = [k for k in keys if rm in T8[k]]
        if len(ks) < 0.8 * len(keys):
            continue
        recs = [T8[k] for k in ks]
        pp = np.array([r["c"].mean() for r in recs])
        pos = np.concatenate([r[rm][r["c"]] for r in recs]); neg = np.concatenate([r[rm][~r["c"]] for r in recs])
        pos, neg = pos[np.isfinite(pos)], neg[np.isfinite(neg)]
        hard = pp < 0.2
        hpos = np.concatenate([r[rm][r["c"]] for r, h in zip(recs, hard) if h]); hneg = np.concatenate([r[rm][~r["c"]] for r, h in zip(recs, hard) if h])
        hpos, hneg = hpos[np.isfinite(hpos)], hneg[np.isfinite(hneg)]
        res = {"auroc": auroc(pos, neg), "auroc_hard": auroc(hpos, hneg) if len(hpos) and len(hneg) else None}
        for alpha in (0.01, 0.05):
            fa, ta = [], []
            for _ in range(20):
                perm = rng.permutation(len(recs)); cal, tst = perm[: len(recs) // 2], perm[len(recs) // 2:]
                w = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in cal]); w = w[np.isfinite(w)]
                tau = np.quantile(w, 1 - alpha)
                wt = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in tst]); ct = np.concatenate([recs[i][rm][recs[i]["c"]] for i in tst])
                fa.append(np.mean(wt[np.isfinite(wt)] >= tau)); ta.append(np.mean(ct[np.isfinite(ct)] >= tau))
            res[f"alpha={alpha}"] = {"FA": float(np.mean(fa)), "TA": float(np.mean(ta))}
        out[task][rm] = res
        print(f"  {rm:28} AUROC {res['auroc']:.3f} (hard {res['auroc_hard'] if res['auroc_hard'] is None else round(res['auroc_hard'],3)}) | "
              + " | ".join(f"a={a}: FA {100*res[f'alpha={a}']['FA']:.1f}% TA {100*res[f'alpha={a}']['TA']:.1f}%" for a in (0.01, 0.05)), flush=True)
json.dump(out, open("paper4/e2/e2_real_verifier_screen.json", "w"), indent=1)
