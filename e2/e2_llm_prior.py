"""Zero-test-time-sample prior from LLM features of the problem text (computed once on Colab).

Features per problem: bge-large embedding (1024-d), Qwen2.5-1.5B difficulty rating, P(Yes, solvable),
mean token NLL. Ridge (embedding) and a small linear model on the 3 scalar features predict the
target model's logit pass rate; trained on the calibration half with out-of-fold scores, as before.
"""
import json
import sys
import numpy as np
import pyarrow.parquet as pq
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold

sys.path.insert(0, "paper4/e2")
from e2_online_v2 import first_success, rr, e2_online, bayes, bins_mix, tempered

D = "paper4/data_ext/"
F = np.load("paper4/e2/colab/features.npz")
rng = np.random.default_rng(14)
U = [4, 16, 64]
REPS = 20


def feats(ds):
    sc = np.column_stack([F[f"{ds}_rate"], F[f"{ds}_pyes"], F[f"{ds}_nll"]])
    sc = (sc - sc.mean(0)) / (sc.std(0) + 1e-9)
    return np.hstack([F[f"{ds}_emb"], sc * 3.0])


def mb_samples(cfg):
    return [np.asarray(v, bool) for v in pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()]


def weaver_samples_by_text(size):
    import glob
    import re
    norm = lambda s: re.sub(r"\s+", " ", str(s)).strip()
    d = {}
    for f in sorted(glob.glob(D + f"weaver_MATH500_{size}_*.parquet")):
        names = pq.ParquetFile(f).schema_arrow.names
        key = "problem" if "problem" in names else "instruction"
        t = pq.read_table(f, columns=[key, "answer_correct"])
        for k, v in zip(t.column(0).to_pylist(), t.column(1).to_pylist()):
            if v:
                d[norm(k)] = np.asarray([bool(x) for x in v], bool)
    texts = json.load(open("paper4/e2/colab/texts.json", encoding="utf-8"))["MATH500"]
    keep = [i for i, t in enumerate(texts) if norm(t) in d]
    return keep, [d[norm(texts[i])] for i in keep]


def logit(p, n):
    q = np.clip(p, 0.5 / n, 1 - 0.5 / n)
    return np.log(q / (1 - q))


def scores(X, y, cal, tst):
    oof = np.empty(len(cal))
    for tr, va in KFold(5, shuffle=True, random_state=int(rng.integers(1e9))).split(cal):
        oof[va] = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(X[cal][tr], y[cal][tr]).predict(X[cal][va])
    pred = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(X[cal], y[cal]).predict(X[tst])
    return oof, pred


def evaluate(name, X, samples):
    p = np.array([s.mean() for s in samples])
    n = int(np.median([len(s) for s in samples]))
    y = logit(p, n)
    N = len(p)
    raw = {k: float(np.corrcoef(np.argsort(np.argsort(v)), np.argsort(np.argsort(p)))[0, 1])
           for k, v in (("rate", X[:, -3]), ("pyes", X[:, -2]), ("nll", X[:, -1]))}
    res = {"raw_spearman": raw}
    for u in U:
        S, K = u * N, 16 * u
        acc, rhos = {}, []
        for _ in range(REPS):
            perm = rng.permutation(N)
            halves = [perm[: N // 2], perm[N // 2:]]
            mix, phat = [None] * N, np.empty(N)
            for a, b in ((0, 1), (1, 0)):
                cal, tst = halves[a], halves[b]
                oof, pred = scores(X, y, cal, tst)
                rhos.append(np.corrcoef(np.argsort(np.argsort(pred)), np.argsort(np.argsort(p[tst])))[0, 1])
                for i, m in zip(tst, bins_mix(p[cal], oof, pred)):
                    mix[i], phat[i] = m, m.mean()
            T = first_success(samples, rng)
            r = {"RR": rr(T, S), "E2 online": e2_online(T, S, phat, K), "Bayes-LLMfeat": bayes(T, S, mix)}
            mt, wt = tempered(mix, p, 0.5)
            r["Bayes-LLMfeat-tempered"] = bayes(T, S, mt, wt)
            for k, v in r.items():
                acc.setdefault(k, []).append(v)
        res[u] = {k: float(np.mean(v)) for k, v in acc.items()}
        res[u]["pred_rho"] = float(np.mean(rhos))
        base = res[u]["RR"]
        print(f"{name:34} N={N:4d} u={u:3d} pred-rho {res[u]['pred_rho']:+.2f} raw {raw} | RR {100*base:5.1f}% | " +
              " ".join(f"{k}: {100*(v-base):+5.1f}" for k, v in res[u].items() if k not in ("RR", "pred_rho")),
              flush=True)
    return res


def main():
    out = {}
    for ds, cfgs in [("MATH", ["MATH_Pythia-1.4B", "MATH_Pythia-6.9B", "MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct"]),
                     ("CodeContests", ["CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct"]),
                     ("MiniF2F", ["MiniF2F-MATH_Llama-3-8B-Instruct", "MiniF2F-MATH_Llama-3-70B-Instruct"])]:
        X = feats(ds)
        for c in cfgs:
            out[c] = evaluate(c, X, mb_samples(c))
            json.dump(out, open("paper4/e2/e2_llm_prior.json", "w"), indent=1)
    X = feats("MATH500")
    for size in ["8B", "70B"]:
        keep, smp = weaver_samples_by_text(size)
        out[f"weaver MATH500 {size}"] = evaluate(f"weaver MATH500 {size}", X[keep], smp)
        json.dump(out, open("paper4/e2/e2_llm_prior.json", "w"), indent=1)


if __name__ == "__main__":
    main()
