"""(1) Exhaustion threshold: the oracle gain vanishes once S >= sum_i 1/a_i(alpha). Report x* = u*alpha* per workload.
(2) Predict Table 6 (real reward models) from measured FA/TA rates, using the same RR mean-field and oracle formulas
    with beta = 1 - TA. Compare predicted ratio (noisy gain / perfect gain) with the simulated TS ratio."""
import json
import numpy as np
from scipy.optimize import brentq
import pyarrow.parquet as pq
import sys
sys.path.insert(0, "paper4/e2")
src = open("paper4/e2/noisy_theory.py", encoding="utf-8").read().split("out = {}")[0]
exec(src)


def values(p, al, be, S):
    a = p * (1 - be) + (1 - p) * al
    pi = np.where(a > 0, p * (1 - be) / np.maximum(a, 1e-12), 0)
    return oracle_value(p, a, pi, S), rr_value(p, a, pi, S)


res = {"threshold": {}, "table6": {}}
print("(1) exhaustion threshold x* = u*alpha* at u = 16 (gain is zero beyond it), and hopeless share h (p < 1/(10u))")
for w in ["MATH_Pythia-1.4B", "MATH_Pythia-6.9B", "MATH_Gemma-2B", "CodeContests_Llama-3-8B-Instruct", "MATH_Llama-3-8B-Instruct"]:
    p = np.array([np.mean(c) for c in pq.read_table(f"paper4/data_ext/mb_{w}.parquet", columns=["is_corrects"]).column(0).to_pylist()])
    N = len(p); u = 16
    need = lambda al: np.mean(1 / (p + (1 - p) * al)) - u
    al_star = brentq(need, 1e-6, 1.0)
    h = float(np.mean(p < 1 / (10 * u)))
    res["threshold"][w] = {"x_star": u * al_star, "hopeless_share": h}
    print(f"   {w:34} x* = {u * al_star:.2f}   hopeless share {h:.2f}")

# (2) Table 6 prediction
import importlib.util
spec = importlib.util.spec_from_file_location("R", "paper4/e2/e2_real_verifier.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
obs = json.load(open("paper4/e2/e2_real_verifier_run_u2.json"))
print("\n(2) Table 6, u = 2: predicted vs simulated (TS) ratio to the perfect-verifier gain")
for task, rms in {"MATH500": ["QwenPRM_min_scores", "InternLM2Reward7B_scores"], "GPQA": ["ArmorRM_scores", "QwenPRM_min_scores"]}.items():
    T8 = R.load(task, "8B", rms)
    recs = [r for r in T8.values() if all(rm in r for rm in rms) and r["c"].mean() < 0.3]
    p = np.array([r["c"].mean() for r in recs]); N = len(p); S = 2 * N
    o0, r0 = values(p, 0.0, 0.0, S); g0 = o0 - r0
    for rm in rms:
        for alpha in (0.01, 0.05):
            w_ = np.concatenate([r[rm][~r["c"]] for r in recs]); w_ = w_[np.isfinite(w_)]
            tau = np.quantile(w_, 1 - alpha)
            c_ = np.concatenate([r[rm][r["c"]] for r in recs]); c_ = c_[np.isfinite(c_)]
            fa, ta = float(np.mean(w_ >= tau)), float(np.mean(c_ >= tau))
            o, r = values(p, fa, 1 - ta, S)
            sim = obs[task][f"{rm}|alpha={alpha}"]["gain"] / obs[task]["perfect"]["gain"] if obs[task]["perfect"]["gain"] != 0 else float("nan")
            key = f"{task}|{rm}|{alpha}"
            res["table6"][key] = {"FA": fa, "TA": ta, "pred_ratio": (o - r) / g0, "oracle_gain_pts": 100 * (o - r) / N, "sim_ratio": sim}
            print(f"   {key:42} FA {fa:.3f} TA {ta:.2f} | predicted ratio {(o - r) / g0:+.2f} | simulated TS ratio {sim:+.2f}")
json.dump(res, open("paper4/e2/noisy_theory2.json", "w"), indent=1)
