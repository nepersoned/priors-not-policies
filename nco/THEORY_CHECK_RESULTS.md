# Theory check on NCO — 2026-10-01

Script: `theory_check.py`; raw output: `theory_check.json`; summary printer: `theory_check_print.py`.

**Setup.** The truth is each instance's exact curve over its 1000-sample population. Each row below is based on 60 windowed sets of 40 instances, for each file.

## 1. Best-of-k curves are power laws

A per-instance fit of f(k) = a + b·k^(−α) gives R² median 0.996–0.999, with p10 ≥ 0.973, across all 6 files.

The greedy optimum computed on the *fitted* curves reproduces the true headroom with r = 0.90–0.998. So the triple (a, b, α) is a sufficient description of the curves.

## 2. Closed form (Prop. 2, common α = median) predicts the headroom

| file | r(true, closed) at u = 25 / 100 | MAE (points) |
|---|---|---|
| cluster AM | 0.971 / 0.924 | 1.35 / 1.87 |
| cluster SymNCO | 0.976 / 0.916 | 1.24 / 1.43 |
| cluster POMO | 0.851 / 0.751 | 0.05 / 0.17 |
| size AM | 0.799 / 0.763 | 0.41 / 0.34 |
| size SymNCO | 0.771 / 0.787 | 0.24 / 0.28 |
| size POMO | 0.937 / 0.912 | 0.02 / 0.11 |

The closed form is weaker under the size knob. The reason is that α varies per instance there, while the closed form assumes a common α (see §4).

## 3. P1: is the reducible headroom independent of budget?

- **Cluster AM:** d_red goes 18.98 → 18.32 → 17.88 → 17.44 as u goes 10 → 100. It is nearly flat. ✓
- **Cluster SymNCO:** 20.1 → 18.9. Nearly flat. ✓
- **Size knob and POMO:** d_red rises with u (e.g. size AM 1.29 → 1.93). This is expected once α is heterogeneous, and it is channel (b) of Prop. 1.

## 4. P2: the theory's spread variable rescues the size knob

Spearman correlation of the true headroom with each spread variable, at u = 25:

| file | spread of log severity at k=1 (paper2) | **spread of log b (theory)** |
|---|---|---|
| size AM | +0.48 | **+0.86** |
| size SymNCO | +0.68 | **+0.87** |
| size POMO | +0.60 | **+0.78** |
| cluster (all three) | +0.84..+0.93 | +0.88..+0.93 |

Paper2's size-knob "failure to replicate" is largely an artifact of the wrong spread variable. With spread of log b, spread predicts the headroom under both knobs.

## 5. Where level enters: through shape (α), as channel (b) predicts

Across windows, Spearman(level, median α) is −0.66, −0.82 and −0.93 for size AM, SymNCO and POMO. Larger instances have a different curve exponent.

Partial Spearman of the true headroom with level, adding controls one at a time (u = 25 / u = 100):

| file | level \| spread_b | + ρ | + α |
|---|---|---|---|
| cluster AM | +0.45 / +0.46 | +0.45 / +0.57 | **+0.03** / +0.37 |
| size AM | −0.71 / −0.87 | −0.72 / −0.88 | **−0.61 / −0.80** |
| size SymNCO | −0.64 / −0.69 | −0.63 / −0.64 | −0.38 / −0.46 |
| size POMO | −0.88 / −0.79 | −0.59 / −0.51 | **−0.19 / −0.28** |

Reading:
- Controlling the shape (median α) removes most of level's effect in several cells: cluster AM at u = 25, and size POMO.
- A residual remains in size AM (−0.6 to −0.8). A likely cause is that the set-median α does not capture α *heterogeneity within* the set.

**Next step:** add the within-set SD of α as a covariate, and use the heterogeneous-α prediction (d_fit) in place of the closed form.

## 6. Paper1 OOD result re-checked with exact curves (50 uniform + 50 clustered, S/N = 100)

| solver, axis | exact-curve plug-in | d_split | paper1 reported |
|---|---|---|---|
| AM, Axis A | 14.07 | 13.94 | 11.55 |
| SymNCO, Axis A | 12.65 | 12.00 | 12.02 |
| POMO, Axis A | 0.50 | 0.01 | −0.29 |
| AM / SymNCO / POMO, Axis B | 1.78 / 1.27 / 2.25 | 0.83 / 0.69 / 1.48 | n/a |

The OOD headline survives (Axis A). Only the in-distribution "phantom" claim fails; see `GATE1_RESULTS.md`.

## 7. Adding within-set alpha heterogeneity (rerun)

Two partial Spearman correlations of the true headroom are reported for each file and budget:

- **spread_b | level, ρ, α_med, α_sd**: the spread effect after controlling for level, reducible share and curve shape. It stays between **+0.72 and +0.94 in all 12 cells** (6 files × 2 budgets). Spread survives every control.
- **level | spread_b, ρ, α_med, α_sd**: the level effect after controlling for spread, reducible share and curve shape. It shrinks from about −0.6..−0.9 to a range of −0.55..+0.28, and its sign is inconsistent across cells. The level effect conditional on the fitted-curve prediction is −0.54..+0.43, and mostly |·| ≤ 0.2.

Conclusion: once spread is measured correctly (log b) and curve shape is described (α), level carries no consistent independent information. What remains is mostly the shape channel of Prop. 1(b).
