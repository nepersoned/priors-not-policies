"""All domains, 10 window seeds each: median and IQR of the key statistics.
Output: paper4/domains/robustness.json and a printed table."""
import json
import sys
import zipfile
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/common")
import alloc

SEEDS = range(10)
D = "paper4/data_ext/"


def nco(fn):
    d = np.load(f"paper4/nco/p2/data/{fn}.npz")
    meta = json.loads(str(d["meta"]))
    return [100 * (d[f"c{i}"] / m["ref"] - 1) for i, m in enumerate(meta)]


def weaver(col):
    x = pq.read_table(D + "weaver_gsm8k_4omini.parquet", columns=[col]).column(0).to_pylist()
    if col == "answer_correct":
        return [1 - np.asarray(v, float) for v in x]
    return [np.max(v) - np.asarray(v, float) for v in x]


def monkey(cfg):
    x = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()
    return [1 - np.asarray(v, float) for v in x]


def prm(kind):
    z = np.load(D + "prm800k_compact.npz")
    ids = sorted({k.split("_")[1] for k in z.files}, key=int)
    if kind == "c":
        return [1 - z[f"c_{i}"] for i in ids]
    return [z[f"{kind}_{i}"].max() - z[f"{kind}_{i}"] for i in ids]


def hpo():
    data = json.loads(zipfile.ZipFile(D + "hpob-data.zip").read("hpob-data/meta-train-dataset.json"))
    out = []
    for sp in data.values():
        for v in sp.values():
            y = np.asarray(v["y"], float).ravel()
            y = y[np.isfinite(y)]
            if len(y) >= 300 and np.ptp(y) > 0:
                out.append(y.max() - y)
    return out


# (name, loader, binary, budget u, kmax)
DOMAINS = [
    ("NCO cluster AM", lambda: nco("rq1lv_AM"), False, 25, 400),
    ("NCO cluster SymNCO", lambda: nco("rq1lv_SYMNCO"), False, 25, 400),
    ("NCO size AM", lambda: nco("rq1sz_AM"), False, 25, 400),
    ("NCO size SymNCO", lambda: nco("rq1sz_SYMNCO"), False, 25, 400),
    ("HPO-B all pairs", hpo, False, 16, 256),
    ("LLM GSM8K 4o-mini RM internlm", lambda: weaver("internlm_scores"), False, 16, 256),
    ("LLM GSM8K 4o-mini RM skyworks", lambda: weaver("skyworks_scores"), False, 16, 256),
    ("LLM MATH PRM800K ORM", lambda: prm("o"), False, 16, 256),
    ("LLM MATH PRM800K PRM", lambda: prm("p"), False, 16, 256),
    ("LLM MATH PRM800K binary", lambda: prm("c"), True, 16, 256),
    ("LLM GSM8K Llama8B binary", lambda: monkey("GSM8K_Llama-3-8B-Instruct"), True, 16, 1024),
    ("LLM MATH Llama8B binary", lambda: monkey("MATH_Llama-3-8B-Instruct"), True, 16, 1024),
    ("LLM MATH Llama70B binary", lambda: monkey("MATH_Llama-3-70B-Instruct"), True, 16, 1024),
]

KEYS = ["spread", "level", "spread|level", "level|spread", "spread|level,shape", "level|spread,shape"]


def main():
    out = {}
    print(f"{'domain':32}{'obj':7}{'n':>5}{'powR2':>7}{'expR2':>7}{'head%':>7}" + "".join(f"{k:>20}" for k in KEYS))
    for name, load, binary, u, kmax in DOMAINS:
        prep = alloc.prepare(load(), kmax, binary)
        reps = [alloc.window_stats(prep, u, s) for s in SEEDS]
        stats = {k: [float(np.percentile([r[k] for r in reps], q)) for q in (25, 50, 75)]
                 for k in KEYS + ["headroom"]}
        out[name] = {"binary": binary, "u": u, "n": len(prep["F"]),
                     "power_r2": float(np.median(prep["r2"])),
                     "exp_r2": float(np.nanmedian(prep["ex_r2"])), "stats": stats}
        print(f"{name:32}{'bin' if binary else 'cont':7}{len(prep['F']):5d}{out[name]['power_r2']:7.3f}"
              f"{out[name]['exp_r2']:7.3f}{stats['headroom'][1]:7.1f}" +
              "".join(f"{stats[k][1]:+8.2f} [{stats[k][0]:+.2f},{stats[k][2]:+.2f}]"[:20].rjust(20) for k in KEYS),
              flush=True)
    json.dump(out, open("paper4/domains/robustness.json", "w"), indent=1)


if __name__ == "__main__":
    main()
