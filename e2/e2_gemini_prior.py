"""Online allocation with a zero-shot prior from Gemini difficulty ratings (no runs of the target model).

The signal is Gemini's p_small rating; the prior is built exactly like the history prior (quintile bins on a
calibration half, cross-fitted). Compared with RR and with the related-model history prior on the same replays.
Also compares with the official MATH level where it can be matched (Weaver MATH500 'level' column)."""
import glob, json, re, sys
import numpy as np
import pyarrow.parquet as pq
from scipy.stats import spearmanr

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import mb, first_success, rr, bins_mix
from e2_bandits_fast import run as bandit

rng = np.random.default_rng(61)
REPS = 30
rat = {}
for f in sorted(glob.glob("paper4/e2/gemini_rating_*.jsonl")):
    for line in open(f, encoding="utf-8-sig"):
        m = re.search(r"\{.*\}", line)
        if m:
            try:
                d = json.loads(m.group(0).replace("'", '"')); rat[int(d["id"])] = d
            except Exception:
                pass

# official MATH level via text match with Weaver MATH500
norm = lambda s: re.sub(r"\s+", " ", str(s or "")).strip()
lvl = {}
for f in glob.glob("paper4/data_ext/weaver_MATH500_*.parquet"):
    names = pq.ParquetFile(f).schema_arrow.names
    if "level" in names:
        key = "problem" if "problem" in names else "instruction"
        t = pq.read_table(f, columns=[key, "level"])
        for q, l in zip(t.column(0).to_pylist(), t.column(1).to_pylist()):
            lvl[norm(q)] = l
qt = pq.read_table("paper4/data_ext/mb_MATH_Pythia-1.4B.parquet", columns=["orig_dset_idx", "question"])
qtext = dict(zip(qt.column(0).to_pylist(), qt.column(1).to_pylist()))
matched = {i: lvl[norm(q)] for i, q in qtext.items() if norm(q) in lvl}
print("ratings", len(rat), "| official level matched for", len(matched), "of", len(qtext))

PAIRS = [("MATH_Pythia-1.4B", "MATH_Pythia-6.9B", 16), ("MATH_Pythia-6.9B", "MATH_Pythia-1.4B", 16),
         ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct", 16), ("MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct", 4),
         ("MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct", 16)]
out = {}
for t, r_, u in PAIRS:
    A, B = mb(t), mb(r_)
    keys = [k for k in A if k in B and k in rat]
    tgt = [A[k] for k in keys]
    p = np.array([s.mean() for s in tgt]); hist = np.array([B[k].mean() for k in keys])
    gem = np.array([float(rat[k]["p_small"]) for k in keys])
    N = len(p); S = u * N
    res = {"rho_gemini": float(spearmanr(gem, p).correlation), "rho_history": float(spearmanr(hist, p).correlation)}
    acc = {}
    for _ in range(REPS):
        perm = rng.permutation(N); halves = [perm[: N // 2], perm[N // 2:]]
        mixes = {}
        for name, sig in (("gemini", gem), ("history", hist)):
            mix = [None] * N
            for a, b in ((0, 1), (1, 0)):
                for i, m in zip(halves[b], bins_mix(p[halves[a]], sig[halves[a]], sig[halves[b]])):
                    mix[i] = m
            mixes[name] = mix
        T = first_success(tgt, rng); base = rr(T, S)
        for name, mix in mixes.items():
            acc.setdefault(f"TS {name}", []).append(bandit(T, S, mix, "ts") - base)
            acc.setdefault(f"UCB {name}", []).append(bandit(T, S, mix, "ucb") - base)
        acc.setdefault("RR", []).append(base)
    for k, v in acc.items():
        v = np.array(v)
        boots = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(2000)]
        res[k] = {"mean": 100 * float(v.mean()), "ci95": [100 * float(np.percentile(boots, 2.5)), 100 * float(np.percentile(boots, 97.5))]}
    key = f"{t}|u={u}"
    out[key] = res
    print(f"{key:34} rho gem {res['rho_gemini']:+.2f} hist {res['rho_history']:+.2f} | RR {res['RR']['mean']:.1f}% | " +
          " | ".join(f"{k} {res[k]['mean']:+.1f} [{res[k]['ci95'][0]:+.1f},{res[k]['ci95'][1]:+.1f}]" for k in acc if k != "RR"), flush=True)
    json.dump(out, open("paper4/e2/e2_gemini_prior.json", "w"), indent=1)
