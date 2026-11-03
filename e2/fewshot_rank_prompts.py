"""Model-calibrated ranking prompts: show the rater 20 example problems the TARGET model (Pythia-1.4B) solved or
failed (from one half of the problems), then ask it to rank the other half for that model. Cross-fitted halves."""
import json, os
import numpy as np
import pyarrow.parquet as pq

TARGET = "MATH_Pythia-1.4B"
t = pq.read_table(f"paper4/data_ext/mb_{TARGET}.parquet", columns=["question", "orig_dset_idx", "is_corrects"])
ids = t.column("orig_dset_idx").to_pylist()
qs = dict(zip(ids, t.column("question").to_pylist()))
p = {i: float(np.mean(c)) for i, c in zip(ids, t.column("is_corrects").to_pylist())}
rng = np.random.default_rng(83)
perm = list(rng.permutation(ids))
halves = [perm[:64], perm[64:]]
os.makedirs("paper4/e2/fewshot_rank", exist_ok=True)
manifest = []
for h in (0, 1):
    cal, tst = halves[h], halves[1 - h]
    cal_sorted = sorted(cal, key=lambda i: -p[i])
    solved = [i for i in cal_sorted if p[i] > 0][:10]
    failed = list(rng.permutation([i for i in cal if p[i] == 0]))[:10]
    ex = ("Here is how one specific small model (call it Model X) did on some other math problems. "
          "'SOLVED' means Model X sometimes got it right; 'FAILED' means it essentially never did.\n\n")
    ex += "\n\n".join(f"SOLVED: {qs[i].strip()}" for i in solved) + "\n\n"
    ex += "\n\n".join(f"FAILED: {qs[int(i)].strip()}" for i in failed) + "\n\n"
    head = (ex + "Using what these examples reveal about Model X's strengths and weaknesses, rank the following new "
            "problems from HARDEST to EASIEST for Model X (most likely to fail first). Do not solve them. Output "
            "exactly one line: RANKING: followed by all the ids, hardest first, separated by commas.\n\n")
    for r in range(3):
        sh = list(rng.permutation(tst))
        for g in range(4):
            grp = [int(x) for x in sh[g * 16:(g + 1) * 16]]
            name = f"h{h}r{r}g{g}"
            open(f"paper4/e2/fewshot_rank/{name}.txt", "w", encoding="utf-8").write(
                head + "\n\n".join(f"[id={i}] {qs[i].strip()}" for i in grp))
            manifest.append({"name": name, "ids": grp})
json.dump(manifest, open("paper4/e2/fewshot_rank/manifest.json", "w"))
print(len(manifest), "prompts; example counts", len(solved), len(failed))
