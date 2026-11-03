"""Answering the 'oracle p' objection.

(A) Noise sensitivity: every rule sees p_hat = sigmoid(logit(p) + N(0, s^2)).
(B) Free real signals, 2-fold cross-fitted calibration (signal -> pass rate learned on a
    calibration half with the target model's labels, applied to the other half):
      - cross-model history: another model's pass rate on the same problem (monkey MATH,
        5 models, same 128 problems; CodeContests, 3 models)
      - MATH difficulty level 1-5 (PRM800K, 495 problems)
Rules (all evaluated on TRUE coverage): uniform, oracle (true p),
  E2: IAS, k ~ (1-p_hat), tiers 21:30:45 by signal;
  correct: greedy on p_hat (1-p_hat)^k   [plug-in]
           greedy on the calibration-bin MIXTURE of curves mean_j (1-p_j)^k   [mixture]
"""
import json
import sys
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/e2")
from e2_cost import ias, fix_sum, greedy_curves, coverage

D = "paper4/data_ext/"
rng = np.random.default_rng(7)
U = [4, 16, 64]
NOISE = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0]
REPS = 20


def p_of(cfg):
    x = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects", "orig_dset_idx"])
    return (np.array([np.mean(v) for v in x.column(0).to_pylist()]),
            x.column(1).to_pylist())


def curves(p, K):
    return (1 - p[:, None]) ** np.arange(1, K + 1)[None, :]


def policies(p_true, phat, S, K, signal_rank=None, mixture_curves=None):
    N = len(p_true)
    out = {}
    out["E2 IAS"] = ias(phat, S, K)
    out["E2 k~(1-p)"] = fix_sum(1 - phat, S)
    r = signal_rank if signal_rank is not None else phat
    t1, t2 = np.quantile(r, [1 / 3, 2 / 3])
    out["E2 tiers"] = fix_sum(np.where(r >= t2, 21, np.where(r >= t1, 30, 45)), S)
    out["correct plug-in"] = greedy_curves(curves(np.clip(phat, 0, 1), K), S)
    if mixture_curves is not None:
        out["correct mixture"] = greedy_curves(mixture_curves, S)
    return out


def evaluate(p, rules_k, u):
    cu = coverage(p, u)
    return {k: 100 * (coverage(p, v) - cu) for k, v in rules_k.items()}


def noise_study(name, p):
    res = {}
    n_pool = 10000
    pc = np.clip(p, 0.5 / n_pool, 1 - 0.5 / n_pool)
    lg = np.log(pc / (1 - pc))
    for u in U:
        S, K = u * len(p), 16 * u
        orc = 100 * (coverage(p, greedy_curves(curves(p, K), S)) - coverage(p, u))
        res[u] = {"oracle": orc}
        for s in NOISE:
            acc = {}
            for _ in range(REPS if s > 0 else 1):
                ph = 1 / (1 + np.exp(-(lg + rng.normal(0, s, len(p)))))
                for k, v in evaluate(p, policies(p, ph, S, K), u).items():
                    acc.setdefault(k, []).append(v)
            res[u][s] = {k: float(np.mean(v)) for k, v in acc.items()}
    return res


def calibrated(p_target, signal, n_bins=5, splits=20):
    """2-fold cross-fit: bin the signal by calibration-half quantiles (or its own levels),
    learn bin -> mean p and bin -> mixture curve. Returns list of (phat, mixture_fn) per split."""
    N = len(p_target)
    outs = []
    for _ in range(splits):
        perm = rng.permutation(N)
        halves = [perm[: N // 2], perm[N // 2:]]
        phat = np.empty(N)
        member = {}
        for a, b in ((0, 1), (1, 0)):
            cal, tst = halves[a], halves[b]
            levels = np.unique(signal)
            if len(levels) <= 6:
                edges = None
                bc, bt = signal[cal], signal[tst]
            else:
                edges = np.unique(np.quantile(signal[cal], np.linspace(0, 1, n_bins + 1)[1:-1]))
                bc, bt = np.digitize(signal[cal], edges), np.digitize(signal[tst], edges)
            for i, t in zip(tst, bt):
                pool = cal[bc == t] if np.any(bc == t) else cal
                phat[i] = p_target[pool].mean()
                member[i] = pool
        outs.append((phat, member))
    return outs


def signal_study(name, p, signal):
    res = {}
    cal = calibrated(p, signal)
    for u in U:
        S, K = u * len(p), 16 * u
        orc = 100 * (coverage(p, greedy_curves(curves(p, K), S)) - coverage(p, u))
        acc = {}
        for phat, member in cal:
            mix = np.stack([curves(p[member[i]], K).mean(0) for i in range(len(p))])
            pol = policies(p, phat, S, K, signal_rank=signal, mixture_curves=mix)
            for k, v in evaluate(p, pol, u).items():
                acc.setdefault(k, []).append(v)
        res[u] = {"oracle": orc, **{k: float(np.mean(v)) for k, v in acc.items()}}
        res[u]["signal_spearman_with_p"] = float(np.corrcoef(np.argsort(np.argsort(signal)),
                                                             np.argsort(np.argsort(p)))[0, 1])
    return res


def main():
    out = {"noise": {}, "signals": {}}
    math = ["MATH_Pythia-1.4B", "MATH_Pythia-6.9B", "MATH_Gemma-2B", "MATH_Llama-3-8B-Instruct",
            "MATH_Llama-3-70B-Instruct"]
    P = {c: p_of(c) for c in math}
    cc = ["CodeContests_Llama-3-8B-Instruct", "CodeContests_Llama-3-70B-Instruct", "CodeContests_Gemma-2B"]
    PC = {c: p_of(c) for c in cc}
    for c in math:
        out["noise"][c] = noise_study(c, P[c][0])
        print("noise done", c, flush=True)
    # cross-model history signals
    for tgt in math:
        for ref in math:
            if ref == tgt:
                continue
            out["signals"][f"{tgt} <- history of {ref}"] = signal_study(tgt, P[tgt][0], P[ref][0])
        print("signals done", tgt, flush=True)
    assert PC[cc[0]][1] == PC[cc[1]][1]
    out["signals"]["CodeContests_Llama-3-8B <- history of 70B"] = signal_study("cc8", PC[cc[0]][0], PC[cc[1]][0])
    out["signals"]["CodeContests_Llama-3-70B <- history of 8B"] = signal_study("cc70", PC[cc[1]][0], PC[cc[0]][0])
    # MATH level on PRM800K
    lv = {}
    with open(D + "prm800k_scored-test-samples.jsonl", encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            lv.setdefault(o["unique_id"], []).append((o["level"], 1.0 if str(o["is_correct"]) == "True" else 0.0))
    ids = [k for k, v in lv.items() if len(v) >= 256]
    p = np.array([np.mean([c for _, c in lv[k]]) for k in ids])
    level = np.array([int(lv[k][0][0]) if str(lv[k][0][0]).isdigit() else 3 for k in ids], float)
    out["signals"]["PRM800K MATH <- MATH level (1-5)"] = signal_study("prm", p, -level)
    json.dump(out, open("paper4/e2/e2_noisy.json", "w"), indent=1)
    print("saved")


if __name__ == "__main__":
    main()
