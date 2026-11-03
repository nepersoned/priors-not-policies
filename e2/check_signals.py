"""Can we build free difficulty signals? (1) same problems across monkey MATH configs;
(2) MATH difficulty level from PRM800K joined by problem text."""
import json
import re
import pyarrow.parquet as pq

D = "paper4/data_ext/"
CFGS = ["MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct", "MATH_Pythia-1.4B",
        "MATH_Pythia-6.9B", "MATH_Gemma-2B"]
idx = {}
qtext = {}
for c in CFGS:
    t = pq.read_table(D + f"mb_{c}.parquet", columns=["question", "orig_dset_idx"])
    idx[c] = t.column("orig_dset_idx").to_pylist()
    qtext[c] = t.column("question").to_pylist()
base = idx["MATH_Llama-3-70B-Instruct"]
for c in CFGS:
    print(f"{c:28} n={len(idx[c])} same order as 70B: {idx[c] == base}  same set: {set(idx[c]) == set(base)}")


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


levels = {}
with open(D + "prm800k_scored-test-samples.jsonl", encoding="utf-8") as f:
    for line in f:
        o = json.loads(line)
        levels.setdefault(norm(o["problem"]), (o["level"], o["subject"]))
hit = sum(1 for q in qtext["MATH_Llama-3-70B-Instruct"] if norm(q) in levels)
print("PRM800K problems with level:", len(levels), "| monkey MATH questions matched by exact text:", hit, "/", len(base))
