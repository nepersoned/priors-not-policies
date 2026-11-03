"""PRISMA-style survey flowchart: 4,029 -> 3,016 -> 1,269 -> 221 -> 33 -> 19."""
import json
import re
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

rows = []
for k in range(6):
    rows += [json.loads(l) for l in open(f"paper4/survey/big/coded/chunk_{k}.jsonl", encoding="utf-8") if l.strip()]
exc = [r for r in rows if r.get("include") != "yes"]
cats = Counter()
rules = [("training-only method", r"train|rl |reinforcement|fine-tun|sft|post-train"),
         ("allocation within a single input", r"within|single input|step|token|branch|node|search"),
         ("no allocation method (analysis, benchmark, survey)", r"analysis|benchmark|survey|evaluat|theor|study"),
         ("off-topic / no comparison to uniform", r".")]
for r in exc:
    txt = (r.get("exclude_reason") or "").lower()
    for name, pat in rules:
        if re.search(pat, txt):
            cats[name] += 1
            break
strict = [json.loads(l) for l in open("paper4/survey/big/e2_strict.jsonl", encoding="utf-8") if l.strip()]
n_yes = sum(1 for s in strict if s.get("e2_strict") == "yes")
print("excluded", len(exc), dict(cats), "strict yes", n_yes)

fig, ax = plt.subplots(figsize=(7.2, 6.6))
ax.axis("off")
boxes = [
    (0.30, 0.92, "Forward citations of 10 seed papers\n+ 1 keyword search (Semantic Scholar)\n4,029 records"),
    (0.30, 0.77, "Deduplicated\n3,016 unique records"),
    (0.30, 0.62, "Recall-oriented keyword prefilter\n1,269 candidates"),
    (0.30, 0.47, "Title/abstract screening + coding (codebook v2)\n221 included\n(145 coded from full text)"),
    (0.30, 0.31, "First-pass E2 flag\n33 candidates"),
    (0.30, 0.14, f"Strict E2 after full-text re-judgment: {n_yes}\nConfirmed by condition-level full-text check:\n13 (5.9%): 12 inference-time + 1 RL training\n(+4 borderline; 2 rejected)"),
]
side = [
    (0.78, 0.695, "Removed by prefilter\n1,747"),
    (0.78, 0.545, "Excluded at screening\n" + f"{len(exc)}\n" +
     "\n".join(f"{v}  {k}" for k, v in cats.most_common())),
    (0.78, 0.225, f"Not E2 under strict definition\n{33 - n_yes}\n(12: unit is refinement, length\nor routing; 2: other criteria)"),
    (0.78, 0.04, "Checks: blind second coder on 50\n(6 of 7 overlapping E2 agree);\nall 19 checked against full text\n(LLM-assisted, author-reviewed):\n13 confirmed, 4 borderline, 2 rejected"),
]
for x, y, t in boxes:
    ax.add_patch(FancyBboxPatch((x - 0.27, y - 0.055), 0.54, 0.11, boxstyle="round,pad=0.01",
                                fc="#eef3f8", ec="#2c3e50", lw=0.9))
    ax.text(x, y, t, ha="center", va="center", fontsize=7.5)
for (x, y, _), (_, y2, _) in zip(boxes[:-1], boxes[1:]):
    ax.annotate("", xy=(x, y2 + 0.058), xytext=(x, y - 0.058), arrowprops=dict(arrowstyle="->", lw=0.8))
for x, y, t in side:
    h = 0.13 if "\n" in t and t.count("\n") > 3 else 0.09
    ax.add_patch(FancyBboxPatch((x - 0.2, y - h / 2), 0.4, h, boxstyle="round,pad=0.01",
                                fc="#fbeeee", ec="#c0392b", lw=0.8))
    ax.text(x, y, t, ha="center", va="center", fontsize=6.6)
for yb, ys in [(0.695, 0.695), (0.545, 0.545), (0.225, 0.225)]:
    ax.annotate("", xy=(0.58, ys), xytext=(0.57, yb), arrowprops=dict(arrowstyle="-", lw=0))
ax.set_xlim(0, 1)
ax.set_ylim(-0.04, 1)
ax.set_title("Survey of per-input compute allocation papers (2022–2026)", fontsize=9)
fig.tight_layout()
fig.savefig("paper4/figures/fig_survey_flow.png", dpi=200)
print("saved")
