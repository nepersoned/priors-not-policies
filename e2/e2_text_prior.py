"""Zero-cost prior from problem TEXT (no history, no proxy samples at test time).

A ridge regressor on TF-IDF features predicts logit(pass rate) of the TARGET model. It is trained
on the calibration half (target labels); calibration problems get out-of-fold scores, test problems
get scores from the full calibration fit. The score then plays the role of the history signal:
prior for a test problem = pass rates of calibration problems in the same score bin.
Compared: RR, E2 online (phat from score bins), Bayes-text, Bayes-text-tempered (w = 0.5).
"""
import glob
import json
import os
import re
import sys
import numpy as np
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import first_success, rr, e2_online, bayes, bins_mix, tempered

D = "paper4/data_ext/"
rng = np.random.default_rng(13)
U = [4, 16, 64]
REPS = 20


def mb_text(cfg):
    t = pq.read_table(D + f"mb_{cfg}.parquet", columns=["question", "is_corrects"])
    return t.column(0).to_pylist(), [np.asarray(v, bool) for v in t.column(1).to_pylist()]


def weaver_text(task, size):
    texts, samples = [], []
    for f in sorted(glob.glob(D + f"weaver_{task}_{size}_*.parquet")):
        names = pq.ParquetFile(f).schema_arrow.names
        key = "problem" if "problem" in names else "instruction"
        t = pq.read_table(f, columns=[key, "answer_correct"])
        for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist()):
            if v:
                texts.append(str(k))
                samples.append(np.asarray([bool(x) for x in v], bool))
    return texts, samples


def logit(p, n):
    q = np.clip(p, 0.5 / n, 1 - 0.5 / n)
    return np.log(q / (1 - q))


def text_scores(texts, y, cal, tst):
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=20000)
    X = vec.fit_transform([texts[i] for i in cal] + [texts[i] for i in tst])
    Xc, Xt = X[: len(cal)], X[len(cal):]
    oof = np.empty(len(cal))
    for tr, va in KFold(5, shuffle=True, random_state=int(rng.integers(1e9))).split(Xc):
        oof[va] = Ridge(alpha=3.0).fit(Xc[tr], y[cal][tr]).predict(Xc[va])
    pred = Ridge(alpha=3.0).fit(Xc, y[cal]).predict(Xt)
    return oof, pred


def evaluate(name, texts, samples):
    p = np.array([s.mean() for s in samples])
    n = int(np.median([len(s) for s in samples]))
    y = logit(p, n)
    N = len(p)
    res = {}
    for u in U:
        S, K = u * N, 16 * u
        acc = {}
        rho_list = []
        for _ in range(REPS):
            perm = rng.permutation(N)
            halves = [perm[: N // 2], perm[N // 2:]]
            mix, phat = [None] * N, np.empty(N)
            for a, b in ((0, 1), (1, 0)):
                cal, tst = halves[a], halves[b]
                oof, pred = text_scores(texts, y, cal, tst)
                rho_list.append(np.corrcoef(np.argsort(np.argsort(pred)), np.argsort(np.argsort(p[tst])))[0, 1])
                for i, m in zip(tst, bins_mix(p[cal], oof, pred)):
                    mix[i], phat[i] = m, m.mean()
            T = first_success(samples, rng)
            r = {"RR": rr(T, S), "E2 online": e2_online(T, S, phat, K), "Bayes-text": bayes(T, S, mix)}
            mt, wt = tempered(mix, p, 0.5)
            r["Bayes-text-tempered"] = bayes(T, S, mt, wt)
            for k, v in r.items():
                acc.setdefault(k, []).append(v)
        res[u] = {k: float(np.mean(v)) for k, v in acc.items()}
        res[u]["text_rho"] = float(np.mean(rho_list))
        base = res[u]["RR"]
        print(f"{name:40} N={N:4d} u={u:3d} text-rho {res[u]['text_rho']:+.2f} | RR {100*base:5.1f}% | " +
              " ".join(f"{k}: {100*(v-base):+5.1f}" for k, v in res[u].items() if k not in ("RR", "text_rho")),
              flush=True)
    return res


def main():
    jobs = [(f"monkey {c}", lambda c=c: mb_text(c)) for c in
            ["MATH_Pythia-1.4B", "MATH_Pythia-6.9B", "MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct",
             "CodeContests_Llama-3-8B-Instruct", "MiniF2F-MATH_Llama-3-8B-Instruct"]]
    jobs += [(f"weaver {t} {s}", lambda t=t, s=s: weaver_text(t, s)) for t in ["MATH500", "GPQA", "MMLU", "MMLU-Pro"]
             for s in ["8B", "70B"]]
    out = {}
    for name, loader in jobs:
        texts, samples = loader()
        out[name] = evaluate(name, texts, samples)
        json.dump(out, open("paper4/e2/e2_text_prior.json", "w"), indent=1)


if __name__ == "__main__":
    main()
