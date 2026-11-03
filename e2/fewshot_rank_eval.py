"""Evaluate model-calibrated (few-shot) rankings against zero-shot rankings on the same test halves."""
import glob, json, re
import numpy as np
import pyarrow.parquet as pq
from scipy.stats import spearmanr, rankdata

man = {m["name"]: m["ids"] for m in json.load(open("paper4/e2/fewshot_rank/manifest.json"))}


def bt_scores(files, valid):
    ids = sorted(valid); ix = {i: k for k, i in enumerate(ids)}
    W = np.zeros((len(ids), len(ids)))
    for f, allowed in files:
        txt = open(f, encoding="utf-8-sig").read()
        m = re.search(r"RANKING:\s*([\d,\s]+)", txt)
        if not m:
            continue
        seen = []
        for x in (int(v) for v in re.findall(r"\d+", m.group(1))):
            if x in allowed and x in ix and x not in seen:
                seen.append(x)
        for r, x in enumerate(seen):
            for y in seen[r + 1:]:
                W[ix[x], ix[y]] += 1
    w = np.ones(len(ids))
    for _ in range(500):
        tot = W + W.T
        w = (W.sum(1) + 0.1) / (np.array([(tot[i] / (w[i] + w)).sum() for i in range(len(ids))]) + 0.2 / (w + 1))
        w /= np.exp(np.mean(np.log(w)))
    return dict(zip(ids, np.log(w)))


zs_man = {m["name"]: m["ids"] for m in json.load(open("paper4/e2/gemini_rank/manifest.json"))}
zs_files = [(f, set(zs_man[f.split("\\")[-1].split("/")[-1][:-4]])) for f in glob.glob("paper4/e2/claude_rank/*.out")]
zs_all = bt_scores(zs_files, {i for v in zs_man.values() for i in v})

out = {}
for model in ["Pythia-1.4B", "Pythia-6.9B", "Gemma-2B", "Llama-3-8B-Instruct"]:
    t = pq.read_table(f"paper4/data_ext/mb_MATH_{model}.parquet", columns=["orig_dset_idx", "is_corrects"])
    p = {k: np.mean(v) for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist())}
    fs_pct, zs_pct, y = [], [], []
    for h in (0, 1):
        names = [n for n in man if n.startswith(f"h{h}")]
        test = {i for n in names for i in man[n]}
        files = [(f"paper4/e2/fewshot_rank/{n}.out", set(man[n])) for n in names if glob.glob(f"paper4/e2/fewshot_rank/{n}.out")]
        if not files:
            continue
        fs = bt_scores(files, test)
        ids = sorted(test)
        fs_pct += list(rankdata([fs[i] for i in ids]) / len(ids))
        zs_pct += list(rankdata([zs_all[i] for i in ids]) / len(ids))
        y += [p[i] for i in ids]
    y = np.array(y)
    out[model] = {"n": len(y), "fewshot": float(-spearmanr(fs_pct, y).correlation), "zeroshot_same_items": float(-spearmanr(zs_pct, y).correlation)}
    print(f"{model:22} n={len(y)} | few-shot (calibrated to Pythia-1.4B) {out[model]['fewshot']:+.2f} | zero-shot {out[model]['zeroshot_same_items']:+.2f}")
json.dump(out, open("paper4/e2/fewshot_rank_eval.json", "w"), indent=1)
