"""Correlate Gemini difficulty ratings with true pass rates of several models on the 128 MATH problems."""
import glob
import json
import re
import numpy as np
import pyarrow.parquet as pq
from scipy.stats import spearmanr

rat = {}
for f in sorted(glob.glob("paper4/e2/gemini_rating_*.jsonl")):
    for line in open(f, encoding="utf-8-sig"):
        m = re.search(r"\{.*\}", line)
        if not m:
            continue
        try:
            d = json.loads(m.group(0).replace("'", '"'))
            rat[int(d["id"])] = d
        except Exception:
            pass
print("ratings:", len(rat))
for model in ["Pythia-1.4B", "Pythia-6.9B", "Gemma-2B", "Llama-3-8B-Instruct", "Llama-3-70B-Instruct"]:
    t = pq.read_table(f"paper4/data_ext/mb_MATH_{model}.parquet", columns=["orig_dset_idx", "is_corrects"])
    p = {k: np.mean(v) for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist())}
    ids = [i for i in rat if i in p]
    y = np.array([p[i] for i in ids])
    out = []
    for key, sign in (("difficulty", -1), ("p_small", 1), ("p_medium", 1)):
        x = np.array([float(rat[i][key]) for i in ids])
        out.append(f"{key} rho {sign * spearmanr(x, y).correlation:+.2f}")
    print(f"{model:22} n={len(ids)} mean p={y.mean():.3f} | " + " | ".join(out))
