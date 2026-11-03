"""Figures for draft v3.
fig_inverted_u.png      : optimal k*(p) for several budgets vs a 'harder gets more' rule
fig_online_ts.png       : solved-share gain over RR at u=16 (TS-history, TS-exch, UCB, myopic, E2 online)
fig_prior_quality.png   : gain vs prior rank-correlation across prior sources (hard workloads)
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E = "paper4/e2/"
plt.rcParams.update({"font.size": 9})

# ---------- 1. inverted-U ----------
p = np.linspace(0.001, 0.6, 400)
r = -np.log(1 - p)
fig, ax = plt.subplots(figsize=(4.2, 3.0))
for lam, lab in [(0.02, "large budget"), (0.08, "medium budget"), (0.25, "small budget")]:
    k = np.maximum(0, np.log(r / lam) / r)
    ax.plot(p, k / k.max(), label=f"optimal, {lab}")
ax.plot(p, (1 - p) / (1 - p).max(), "k--", label="'harder gets more' (k ∝ 1−p)")
ax.set_xlabel("pass rate p  (← harder   easier →)")
ax.set_ylabel("attempts (normalized)")
ax.set_title("Optimal allocation is inverted-U in difficulty")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig("paper4/figures/fig_inverted_u.png", dpi=200)

# ---------- 2. online gains ----------
B = json.load(open(E + "e2_bandits.json"))
O = json.load(open(E + "e2_online_v2.json"))
names = {"MATH_Pythia-1.4B": "MATH\nPythia-1.4B", "MATH_Pythia-6.9B": "MATH\nPythia-6.9B",
         "MATH_Gemma-2B": "MATH\nGemma-2B", "CodeContests_Llama-3-8B-Instruct": "CodeContests\nLlama-3-8B",
         "MiniF2F-MATH_Llama-3-8B-Instruct": "MiniF2F (Lean)\nLlama-3-8B",
         "MATH_Llama-3-8B-Instruct": "MATH\nLlama-3-8B"}
e2map = {k: next((v for kk, v in O.items() if kk.startswith(f"monkey {k} <-")), None) for k in names}
u = "16"
pols = [("TS (history)", "#c0392b"), ("UCB (history)", "#e67e22"), ("Bayes-myopic (history)", "#8e44ad"),
        ("TS (exchangeable)", "#7f8c8d")]
fig, ax = plt.subplots(figsize=(7.0, 3.0))
xs = np.arange(len(names))
w = 0.16
for j, (pk, c) in enumerate(pols):
    vals = [100 * (B[k][u][pk] - B[k][u]["RR"]) for k in names]
    ax.bar(xs + (j - 2) * w, vals, w, label=pk, color=c)
e2v = [100 * (e2map[k][u]["E2 online"][0] - e2map[k][u]["RR"][0]) if e2map[k] else np.nan for k in names]
ax.bar(xs + 2 * w, e2v, w, label="E2 online", color="#2c3e50")
ax.axhline(0, color="k", lw=0.7)
ax.set_xticks(xs)
ax.set_xticklabels([names[k] + f"\nRR {100*B[k][u]['RR']:.0f}%" for k in names], fontsize=7)
ax.set_ylabel("solved share vs RR (pts), u=16")
ax.set_title("With a verifier: the prior matters, not the policy")
ax.legend(fontsize=7, ncol=3)
fig.tight_layout()
fig.savefig("paper4/figures/fig_online_ts.png", dpi=200)

# ---------- 3. prior quality ----------
pts = []  # (rho, gain, source)
LLM = json.load(open(E + "e2_llm_prior.json"))
TXT = json.load(open(E + "e2_text_prior.json"))
for k in ["MATH_Pythia-1.4B", "MATH_Pythia-6.9B", "MATH_Gemma-2B", "CodeContests_Llama-3-8B-Instruct",
          "MiniF2F-MATH_Llama-3-8B-Instruct"]:
    if k in LLM:
        row = LLM[k]["16"]
        pts.append((row["pred_rho"], 100 * (row["Bayes-LLMfeat"] - row["RR"]), "LLM features"))
    tk = f"monkey {k}"
    if tk in TXT:
        row = TXT[tk]["16"]
        pts.append((row["text_rho"], 100 * (row["Bayes-text"] - row["RR"]), "TF-IDF text"))
# history signals: rank corr of the reference model's pass rate with the target's
import pyarrow.parquet as pq
def prate(cfg):
    return np.array([np.mean(v) for v in pq.read_table(f"paper4/data_ext/mb_{cfg}.parquet",
                                                        columns=["is_corrects"]).column(0).to_pylist()])
rk = lambda a: np.argsort(np.argsort(a))
for k, v in O.items():
    if not k.startswith(("monkey MATH", "monkey CodeContests", "monkey MiniF2F")):
        continue
    t, ref = k[len("monkey "):].split(" <- ")
    a, b = prate(t), prate(ref)
    if len(a) != len(b):
        continue
    rho = float(np.corrcoef(rk(a), rk(b))[0, 1])
    if a.mean() < 0.3:  # hard targets only
        pts.append((rho, 100 * (v["16"]["Bayes-history"][0] - v["16"]["RR"][0]), "related-model history"))
fig, ax = plt.subplots(figsize=(4.2, 3.0))
for src, mk, c in [("TF-IDF text", "s", "#7f8c8d"), ("LLM features", "^", "#2980b9"),
                   ("related-model history", "o", "#c0392b")]:
    q = [(x, y) for x, y, s in pts if s == src]
    if q:
        ax.scatter(*zip(*q), marker=mk, color=c, label=src, s=22)
ax.axhline(0, color="k", lw=0.7)
ax.axvline(0.6, color="gray", ls=":", lw=0.9)
ax.set_xlabel("prior quality (Spearman with true pass rate)")
ax.set_ylabel("solved share vs RR (pts), u=16")
ax.set_title("Gains need an informative prior (ρ ≳ 0.6)")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig("paper4/figures/fig_prior_quality.png", dpi=200)
print("saved 3 figures;", len(pts), "points in prior-quality plot")
