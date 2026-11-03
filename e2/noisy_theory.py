"""Closed-form prediction of the allocation gain under verifier errors, compared with Table 5 (simulated TS gains).

Known pass rates p_i; false-acceptance rate alpha, false-rejection rate beta; an accepted input leaves the pool.
Per attempt: acceptance prob a_i = p_i(1-beta) + (1-p_i)alpha; precision pi_i = p_i(1-beta)/a_i.
 - RR (mean-field): every input gets up to k attempts, k set by sum_i (1-(1-a_i)^k)/a_i = uN;
   true solves = sum_i pi_i (1-(1-a_i)^k).
 - Oracle index policy (greedy by p_i, optimal by the constant-hazard Gittins/c-mu argument): process inputs in
   decreasing p_i; each consumes 1/a_i attempts in expectation; true solves = sum of pi_i over inputs covered.
Prediction: G(alpha) = oracle - RR. We compare the ratio G(alpha)/G(0) with the simulated TS-history ratios."""
import json
import numpy as np
from scipy.optimize import brentq
import pyarrow.parquet as pq

U = 16
TABLE5 = {  # TS-history gain over RR, Table 5 (no errors, FA 1%, 2%, 5%)
    "MATH_Pythia-1.4B": [11.1, 10.1, 6.7, 0.6], "MATH_Pythia-6.9B": [11.7, 8.8, 7.3, 0.3],
    "MATH_Gemma-2B": [3.4, 3.4, 1.9, 0.0], "CodeContests_Llama-3-8B-Instruct": [3.3, 2.7, 1.9, 0.3]}
ALPHAS = [0.0, 0.01, 0.02, 0.05, 0.10]


def rr_value(p, a, pi, S):
    a = np.maximum(a, 1e-12)
    used = lambda k: np.sum((1 - (1 - a) ** k) / a) - S
    kmax = 1e7
    if used(kmax) < 0:  # budget exhausts the pool
        return float(np.sum(pi * (1 - (1 - a) ** kmax)))
    k = brentq(used, 0, kmax)
    return float(np.sum(pi * (1 - (1 - a) ** k)))


def oracle_value(p, a, pi, S):
    order = np.argsort(-p)
    left, val = S, 0.0
    for i in order:
        cost = 1 / max(a[i], 1e-12)
        if cost <= left:
            val += pi[i]; left -= cost
        else:
            val += pi[i] * (1 - (1 - a[i]) ** left)  # partial: run out of budget mid-input
            left = 0
            break
    return val


out = {}
for w, obs in TABLE5.items():
    t = pq.read_table(f"paper4/data_ext/mb_{w}.parquet", columns=["is_corrects"])
    p = np.array([np.mean(c) for c in t.column(0).to_pylist()])
    N = len(p); S = U * N
    gains = []
    for al in ALPHAS:
        a = p + (1 - p) * al
        pi = np.where(a > 0, p / np.maximum(a, 1e-12), 0)
        gains.append(100 * (oracle_value(p, a, pi, S) - rr_value(p, a, pi, S)) / N)
    pred = [g / gains[0] for g in gains[:4]]
    obsr = [o / obs[0] for o in obs]
    out[w] = {"oracle_gain_pts": gains, "pred_ratio": pred, "obs_ratio": obsr}
    print(f"{w:34} oracle gain {['%.1f' % g for g in gains]} | predicted ratio {['%.2f' % r for r in pred]} | TS ratio {['%.2f' % r for r in obsr]}")
json.dump(out, open("paper4/e2/noisy_theory.json", "w"), indent=1)
