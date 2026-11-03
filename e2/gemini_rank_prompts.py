"""Listwise difficulty ranking prompts: 128 MATH problems, 6 random shuffles x 8 groups of 16."""
import json
import os
import numpy as np
import pyarrow.parquet as pq

t = pq.read_table("paper4/data_ext/mb_MATH_Pythia-1.4B.parquet", columns=["question", "orig_dset_idx"])
qs = dict(zip(t.column("orig_dset_idx").to_pylist(), t.column("question").to_pylist()))
ids = list(qs)
rng = np.random.default_rng(71)
os.makedirs("paper4/e2/gemini_rank", exist_ok=True)
head = ("You are an expert competition-math coach. Rank the following problems from HARDEST to EASIEST for small "
        "open language models (around 1B-7B parameters) answering in a single attempt. Consider the number of "
        "reasoning steps, the chance of an arithmetic slip, and how unusual the required idea is. Do not solve them. "
        "Output exactly one line: RANKING: followed by all the ids, hardest first, separated by commas.\n\n")
manifest = []
for r in range(6):
    perm = rng.permutation(ids)
    for g in range(8):
        grp = [int(x) for x in perm[g * 16:(g + 1) * 16]]
        body = "\n\n".join(f"[id={i}] {qs[i].strip()}" for i in grp)
        name = f"r{r}g{g}"
        open(f"paper4/e2/gemini_rank/{name}.txt", "w", encoding="utf-8").write(head + body)
        manifest.append({"name": name, "ids": grp})
json.dump(manifest, open("paper4/e2/gemini_rank/manifest.json", "w"))
print(len(manifest), "prompts")
