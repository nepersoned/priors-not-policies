"""PRM800K scored test samples: MATH, 500 problems, up to ~1860 samples each.
Same samples, three objectives: binary correctness, ORM score, PRM score."""
import json
import sys
from collections import defaultdict
import numpy as np

sys.path.insert(0, "paper4/common")
import alloc

corr, orm, prm = defaultdict(list), defaultdict(list), defaultdict(list)
with open("paper4/data_ext/prm800k_scored-test-samples.jsonl", encoding="utf-8") as f:
    for line in f:
        o = json.loads(line)
        uid = o["unique_id"]
        corr[uid].append(1.0 if str(o["is_correct"]) == "True" else 0.0)
        orm[uid].append(float(o["orm_score"]))
        prm[uid].append(float(o["prm_score"]))
uids = [u for u in corr if len(corr[u]) >= 256]
print("problems", len(corr), "with >=256 samples", len(uids),
      "median samples", int(np.median([len(corr[u]) for u in uids])), flush=True)
np.savez_compressed("paper4/data_ext/prm800k_compact.npz",
                    **{f"{k}_{i}": np.asarray(d[u]) for i, u in enumerate(uids)
                       for k, d in (("c", corr), ("o", orm), ("p", prm))})

res = []
bc = [1 - np.asarray(corr[u]) for u in uids]
res.append(alloc.analyze(bc, "PRM800K/binary", budgets=(4, 16, 64), kmax=256, seed=4, binary=True)[0])
for name, d in (("orm", orm), ("prm", prm)):
    cs = [np.max(d[u]) - np.asarray(d[u]) for u in uids]
    res.append(alloc.analyze(cs, f"PRM800K/{name}", budgets=(4, 16, 64), kmax=256, seed=4)[0])
for r in res:
    print(json.dumps(r), flush=True)
json.dump(res, open("paper4/domains/prm800k_results.json", "w"), indent=1)
