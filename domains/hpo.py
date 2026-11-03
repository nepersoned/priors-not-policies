"""HPO-B: random-search best-of-k over stored hyperparameter evaluations.
Instance = (search space, dataset) pair; cost = best y in the table - y (regret).
Continuous objective -> theory predicts power-law curves, level cancels."""
import json
import sys
import zipfile
import numpy as np

sys.path.insert(0, "paper4/common")
import alloc

MIN_EVALS = 300
z = zipfile.ZipFile("paper4/data_ext/hpob-data.zip")
data = json.loads(z.read("hpob-data/meta-train-dataset.json"))
pairs, by_space = [], {}
for sp, dsets in data.items():
    for ds, v in dsets.items():
        y = np.asarray(v["y"], float).ravel()
        y = y[np.isfinite(y)]
        if len(y) >= MIN_EVALS and np.ptp(y) > 0:
            c = y.max() - y
            pairs.append(c)
            by_space.setdefault(sp, []).append(c)
print("spaces", len(data), "pairs kept", len(pairs),
      "median evals", int(np.median([len(c) for c in pairs])), flush=True)

res = []
out, _ = alloc.analyze(pairs, "HPO-B/all-pairs", budgets=(4, 16, 64), kmax=256, seed=3)
res.append(out)
print(json.dumps(out), flush=True)
for sp, cs in sorted(by_space.items(), key=lambda kv: -len(kv[1]))[:4]:
    if len(cs) < 40:
        break
    out, _ = alloc.analyze(cs, f"HPO-B/space{sp}", budgets=(4, 16, 64), kmax=256,
                           nset=min(30, len(cs) // 2), seed=3)
    res.append(out)
    print(json.dumps(out), flush=True)
json.dump(res, open("paper4/domains/hpo_results.json", "w"), indent=1)
