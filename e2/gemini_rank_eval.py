"""Aggregate listwise rankings into a difficulty score (Bradley-Terry on implied pairs, plus Borda),
then correlate with true pass rates and compare with the absolute ratings."""
import glob, json, re, sys
import numpy as np
import pyarrow.parquet as pq
from scipy.stats import spearmanr

man = {m["name"]: m["ids"] for m in json.load(open("paper4/e2/gemini_rank/manifest.json"))}
ids = sorted({i for v in man.values() for i in v})
ix = {i: k for k, i in enumerate(ids)}
wins = np.zeros((len(ids), len(ids)))  # wins[a,b]: a judged harder than b
borda, cnt = np.zeros(len(ids)), np.zeros(len(ids))
ok = 0
DIRS = sys.argv[1:] or ["paper4/e2/gemini_rank"]
files = [f for d in DIRS for f in sorted(glob.glob(d + "/*.out"))]
for f in files:
    name = f.split("\\")[-1].split("/")[-1][:-4]
    txt = open(f, encoding="utf-8-sig").read()
    m = re.search(r"RANKING:\s*([\d,\s]+)", txt)
    if not m:
        continue
    order = [int(x) for x in re.findall(r"\d+", m.group(1)) if int(x) in set(man[name])]
    seen = []
    for x in order:
        if x not in seen:
            seen.append(x)
    if len(seen) < 12:
        continue
    ok += 1
    n = len(seen)
    for r, x in enumerate(seen):
        borda[ix[x]] += 1 - r / (n - 1); cnt[ix[x]] += 1
        for y in seen[r + 1:]:
            wins[ix[x], ix[y]] += 1
print("parsed rankings:", ok)

# Bradley-Terry via MM iterations
w = np.ones(len(ids))
for _ in range(500):
    tot = wins + wins.T
    num = wins.sum(1) + 0.1
    den = np.array([(tot[i] / (w[i] + w)).sum() for i in range(len(ids))]) + 0.2 / (w + 1)
    w = num / den
    w /= np.exp(np.mean(np.log(w)))
hard_bt = np.log(w)
hard_borda = borda / np.maximum(cnt, 1)

rat = {}
for f in sorted(glob.glob("paper4/e2/gemini_rating_*.jsonl")):
    for line in open(f, encoding="utf-8-sig"):
        mm = re.search(r"\{.*\}", line)
        if mm:
            try:
                d = json.loads(mm.group(0).replace("'", '"')); rat[int(d["id"])] = float(d["p_small"])
            except Exception:
                pass
res = {}
for model in ["Pythia-1.4B", "Pythia-6.9B", "Gemma-2B", "Llama-3-8B-Instruct", "Llama-3-70B-Instruct"]:
    t = pq.read_table(f"paper4/data_ext/mb_MATH_{model}.parquet", columns=["orig_dset_idx", "is_corrects"])
    p = {k: np.mean(v) for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist())}
    y = np.array([p[i] for i in ids])
    a = np.array([rat.get(i, np.nan) for i in ids])
    res[model] = {"rank_BT": float(-spearmanr(hard_bt, y).correlation), "rank_Borda": float(-spearmanr(hard_borda, y).correlation),
                  "absolute": float(spearmanr(a, y, nan_policy="omit").correlation)}
    print(f"{model:22} | BT {res[model]['rank_BT']:+.2f} | Borda {res[model]['rank_Borda']:+.2f} | absolute {res[model]['absolute']:+.2f}")
json.dump({"ids": ids, "bt_hardness": hard_bt.tolist(), "borda_hardness": hard_borda.tolist(), "corr": res},
          open("paper4/e2/rank_scores_" + "_".join(d.rstrip("/").split("/")[-1] for d in DIRS) + ".json", "w"), indent=1)
