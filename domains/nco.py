"""NCO domain through the common pipeline (sanity check against theory_check.py)."""
import json
import sys
import numpy as np

sys.path.insert(0, "paper4/common")
import alloc

res = {}
for fn in ["rq1lv_AM", "rq1lv_SYMNCO", "rq1lv_POMO", "rq1sz_AM", "rq1sz_SYMNCO", "rq1sz_POMO"]:
    d = np.load(f"paper4/nco/p2/data/{fn}.npz")
    meta = json.loads(str(d["meta"]))
    costs = [100 * (d[f"c{i}"] / m["ref"] - 1) for i, m in enumerate(meta)]
    out, _ = alloc.analyze(costs, f"NCO/{fn}", budgets=(10, 25, 100), kmax=400, seed=1)
    res[fn] = out
    print(json.dumps(out), flush=True)
json.dump(res, open("paper4/domains/nco_results.json", "w"), indent=1)
