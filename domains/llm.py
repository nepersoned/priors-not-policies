"""LLM domains: binary (verifier) vs continuous (reward-model score) on the same samples.

Theory prediction:
  binary (pass@k)    : per-instance curves exponential -> level matters (acts as budget)
  continuous (RM)    : per-instance curves power-law   -> level cancels, spread governs
"""
import json
import sys
import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, "paper4/common")
import alloc

D = "paper4/data_ext/"
RM_COLS = ["armor_rm_score", "gpm_scores", "grm_scores", "internlm_scores",
           "qrm_scores", "skyworks_scores", "urm_scores", "offset_bias_scores"]


def binary_costs(lists):
    return [1.0 - np.asarray(x, float) for x in lists]


def cont_costs(lists):
    out = []
    for x in lists:
        x = np.asarray([v for v in x if v is not None and np.isfinite(v)], float)
        out.append(x.max() - x)
    return out


def run(costs, name, binary, budgets, kmax):
    out, _ = alloc.analyze(costs, name, budgets=budgets, kmax=kmax, nset=40, nwin=80,
                           seed=2, binary=binary)
    print(json.dumps(out), flush=True)
    return out


res = []
# monkey_business: binary only, 10k samples/problem
for cfg in ["GSM8K_Llama-3-8B-Instruct", "MATH_Llama-3-8B-Instruct", "MATH_Llama-3-70B-Instruct"]:
    t = pq.read_table(D + f"mb_{cfg}.parquet", columns=["is_corrects"]).column(0).to_pylist()
    res.append(run(binary_costs(t), f"monkey/{cfg}/binary", True, (4, 16, 64, 256), 1024))

# weaver GSM8K GPT-4o-mini: same 1000 samples, binary + 8 reward models
tab = pq.read_table(D + "weaver_gsm8k_4omini.parquet", columns=["answer_correct"] + RM_COLS)
res.append(run(binary_costs(tab.column("answer_correct").to_pylist()),
               "weaver-gsm8k/binary", True, (4, 16, 64), 256))
for c in RM_COLS:
    res.append(run(cont_costs(tab.column(c).to_pylist()), f"weaver-gsm8k/{c}", False, (4, 16, 64), 256))

json.dump(res, open("paper4/domains/llm_results.json", "w"), indent=1)
