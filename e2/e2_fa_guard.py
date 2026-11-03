"""Guarding against false acceptances with answer agreement (real Weaver reward models).

An input is declared solved under rule
  single : at the first attempt the verifier accepts (as in Table 6);
  agree2 : when two accepted attempts give the same (normalized) final answer;
  gated  : agree2 only for inputs whose history prior marks them as hard (prior mean below tau), single otherwise.
The declared answer is correct if the confirming sample is correct. Policies see only "not yet solved"
until the declaration, as in e2_noisy_verifier.py. Workloads: Llama-3.1-8B, problems it solves < 30% of the time.
"""
import glob
import json
import re
import sys
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import bins_mix
from e2_noisy_verifier import rr, ts

D = "paper4/data_ext/"
rng = np.random.default_rng(53)
REPS = 10
TAU = 0.10
CFG = {"MATH500": ["QwenPRM_min_scores", "InternLM2Reward7B_scores"], "GPQA": ["ArmorRM_scores", "QwenPRM_min_scores"]}
norm_q = lambda s: re.sub(r"\s+", " ", str(s or "")).strip()


def norm_a(a):
    a = str(a or "")
    for x in ("\\left", "\\right", "\\!", "\\,", "$", "\\dfrac", "\\tfrac", "\\displaystyle", " "):
        a = a.replace(x, "\\frac" if x in ("\\dfrac", "\\tfrac") else "")
    return a.rstrip(".").lower()


def load(task, size, cols):
    out = {}
    for f in sorted(glob.glob(D + f"weaver_{task}_{size}_*.parquet")):
        names = pq.ParquetFile(f).schema_arrow.names
        key = "problem" if "problem" in names else "instruction"
        have = [c for c in cols if c in names]
        t = pq.read_table(f, columns=[key, "answer_correct"] + (["extracted_answers"] if cols else []) + have)
        for j, k in enumerate(t.column(key).to_pylist()):
            ac = t.column("answer_correct")[j].as_py()
            if not ac:
                continue
            rec = {"c": np.asarray(ac, bool)}
            if cols:
                ans = t.column("extracted_answers")[j].as_py() or [None] * len(ac)
                rec["a"] = np.asarray([norm_a(x) for x in ans], object)
            for c in have:
                v = t.column(c)[j].as_py()
                if v is not None and len(v) == len(ac):
                    rec[c] = np.asarray([np.nan if x is None else x for x in v], float)
            out[norm_q(k)] = rec
    return out


def declare(recs, rm, tau, need2, r):
    """need2[i]: whether input i requires two agreeing acceptances. Returns (A, ok)."""
    A = np.full(len(recs), np.inf)
    ok = np.zeros(len(recs), bool)
    for i, rec in enumerate(recs):
        o = r.permutation(len(rec["c"]))
        acc = (np.ones(len(o), bool) if rm is None else np.nan_to_num(rec[rm][o], nan=-np.inf) >= tau)
        if rm is None:
            acc = rec["c"][o]  # perfect verifier
        seen = {}
        for t_, j in enumerate(o):
            if not acc[t_]:
                continue
            if not need2[i]:
                A[i], ok[i] = t_ + 1, rec["c"][j]
                break
            a = rec["a"][j]
            if a in seen and a != "":
                A[i], ok[i] = t_ + 1, rec["c"][j]
                break
            seen[a] = True
    return A, ok


def main():
    out = {}
    for task, rms in CFG.items():
        T8, T70 = load(task, "8B", rms), load(task, "70B", [])
        keys = [k for k in T8 if k in T70 and all(rm in T8[k] for rm in rms) and T8[k]["c"].mean() < 0.3]
        recs = [T8[k] for k in keys]
        p = np.array([r["c"].mean() for r in recs]); sig = np.array([T70[k]["c"].mean() for k in keys])
        N = len(p)
        out[task] = {"N": N, "mean_p": float(p.mean())}
        for u in (4, 8):
            S = u * N
            for rm in [None] + rms:
                for alpha in ([None] if rm is None else [0.05, 0.10]):
                    acc = {}
                    for _ in range(REPS):
                        perm = rng.permutation(N); cal, tst = perm[: N // 2], perm[N // 2:]
                        mix = [None] * N
                        for a, b in ((cal, tst), (tst, cal)):
                            for i, m in zip(b, bins_mix(p[a], sig[a], sig[b])):
                                mix[i] = m
                        prior_mean = np.array([m.mean() for m in mix])
                        if rm is not None:
                            w = np.concatenate([recs[i][rm][~recs[i]["c"]] for i in cal]); w = w[np.isfinite(w)]
                            tau = np.quantile(w, 1 - alpha)
                        else:
                            tau = None
                        for rule, need2 in (("single", np.zeros(N, bool)), ("agree2", np.ones(N, bool)),
                                            ("gated", prior_mean < TAU)):
                            A, ok = declare(recs, rm, tau, need2, rng)
                            for pol, done in (("RR", rr(A, S)), ("TS", ts(A, S, mix))):
                                acc.setdefault(f"{rule}|{pol}", []).append((done & ok).mean())
                                acc.setdefault(f"{rule}|{pol}|false", []).append((done & ~ok).mean())
                    res = {k: float(np.mean(v)) for k, v in acc.items()}
                    key = f"u={u}|{'perfect' if rm is None else rm}|FA={alpha}"
                    out[task][key] = res
                    print(f"{task:8} {key:42} " + " | ".join(
                        f"{rule}: RR {100*res[rule+'|RR']:4.1f} (F {100*res[rule+'|RR|false']:4.1f}) TS {100*res[rule+'|TS']:4.1f} (F {100*res[rule+'|TS|false']:4.1f})"
                        for rule in ("single", "agree2", "gated")), flush=True)
                    json.dump(out, open("paper4/e2/e2_fa_guard.json", "w"), indent=1)


if __name__ == "__main__":
    main()
