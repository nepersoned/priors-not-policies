"""Figure: share of the oracle headroom captured by 'harder gets more' (E2) rules
vs. how hard the workload is (mean pass rate), u = 16, true difficulty known."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

res = {**json.load(open("paper4/e2/e2_cost.json")), **json.load(open("paper4/e2/e2_cost_hard.json"))}
U = "u16"
RULES = [("E2 IAS [true p]", "IAS  N=log(1-C)/log(1-p)", "#c0392b"),
         ("E2 linear (1-p) [true p]", "k ∝ 1-p", "#e67e22"),
         ("E2 tiers 21:30:45 [true p]", "tiers easy:mid:hard = 21:30:45", "#8e44ad")]
fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
rows = []
for name, r in res.items():
    x = r["mean_p"]
    o = r[U]["oracle"]["gain_pts"]
    rows.append((name, x, r["share_hopeless(p=0)"], o,
                 {k: r[U][k]["gain_pts"] for k, _, _ in RULES}))
rows.sort(key=lambda t: t[1])
for k, lab, c in RULES:
    xs = [t[1] for t in rows]
    ys = [100 * t[4][k] / t[3] if t[3] > 0.5 else np.nan for t in rows]
    ax[0].plot(xs, ys, "o-", color=c, label=lab, alpha=0.85)
ax[0].axhline(0, color="k", lw=0.8)
ax[0].axhline(100, color="gray", lw=0.8, ls="--")
ax[0].set_xscale("log")
ax[0].set_xlabel("mean pass rate of the workload (log scale)")
ax[0].set_ylabel("% of oracle headroom captured")
ax[0].set_title("'Harder gets more' captures nothing on hard workloads")
ax[0].legend(fontsize=8)
xs = np.arange(len(rows))
ax[1].bar(xs - 0.2, [t[3] for t in rows], 0.4, label="oracle (same information)", color="#2c3e50")
ax[1].bar(xs + 0.2, [t[4]["E2 IAS [true p]"] for t in rows], 0.4, label="E2 IAS", color="#c0392b")
ax[1].set_xticks(xs)
ax[1].set_xticklabels([t[0].replace("monkey ", "").replace("_", " ")[:22] for t in rows], rotation=60,
                      ha="right", fontsize=7)
ax[1].set_ylabel("coverage gain over uniform (pts), u=16")
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig("paper4/e2/fig_e2_cost.png", dpi=160)
fig.savefig("paper4/figures/fig_e2_cost.png", dpi=160)
for t in rows:
    print(f"{t[0]:40} mean p {t[1]:.3f} hopeless {t[2]:.2f} oracle {t[3]:+.1f} | " +
          " ".join(f"{k.split(' [')[0]} {v:+.1f} ({100*v/t[3]:.0f}%)" for k, v in t[4].items()))
