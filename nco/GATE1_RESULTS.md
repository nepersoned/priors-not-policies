# Gate 1 results — 2026-10-01

Scripts: `gate1_estimators.py`, `gate1_null.py`, `gate1_summary.py`, `recheck_paper1.py`, `recheck_paper1_estimator.py`.
Data: paper2 arrays (Axis A, K=1000; cluster knob `rq1lv`, size knob `rq1sz`) and paper1 `release/data/expand_*`.

## Terms

- **U-statistic curve**: the exact expected best-of-k computed over all orderings of the samples. It is unbiased, and it is the Rao–Blackwellized version of paper1's 200-permutation Monte Carlo curve.
- **d_in / d_split / eb / eblog**: the headroom estimators. They are defined in the docstring of `gate1_estimators.py`.

## 1. Paper1's in-distribution audit does not hold up as stated (Axis B, uniform TSP-100, N=50, S/N=100)

Axis B is a deterministic pool of 800. The exact (U-statistic) curve over the full pool is therefore the *true* curve of the protocol, and the full-pool optimum is the true headroom.

| solver | paper1 d_in (reproduced exactly) | paper1's allocation on exact curves | **exact true headroom** | d_split (mean of 20 splits) |
|---|---|---|---|---|
| POMO   | 2.227 | 1.337 | **1.568** | 0.493 |
| AM     | 2.567 | 0.715 | **1.122** | 0.168 |
| SymNCO | 2.206 | 0.699 | **1.193** | 0.215 |

Findings:
- Paper1's d_in overstated the headroom by about 0.7–1.4 points. The source is Monte Carlo noise in the 200-permutation curve estimator: the mean max curve error is 0.46 / 3.68 / 6.93 gap points for POMO / AM / SymNCO. The convex-minorant step and the greedy allocation exploit that noise. This part is a real phantom, but it comes from the *estimator*, not from sampling.
- The true headroom is **not zero**: it is 1.1–1.6%. d_split (0.17–0.49) is biased downward, because half-pool curves are not the full-pool curves. Paper1's reading "d_split ≈ 0, so there is no detectable gain" is therefore a **false negative produced by the fix**.

## 2. Exact null (true spread = 0), Axis A, with U-statistic curves

All N=40 instances share one population. d_in is reported as mean / p95.

| regime | AM | SymNCO | POMO |
|---|---|---|---|
| m=400, S/N=25 | +0.16 / +0.37 | +0.21 / +0.71 | +0.08 / +0.18 |
| m=800, S/N=100 | +0.21 / +0.38 | +0.33 / +1.07 | +0.17 / +0.43 |

Findings:
- With a Rao–Blackwellized curve the sampling phantom is small, about 0.1–0.3 points on average. d_split at this null is −0.2 to −0.7.
- eb and eblog are about 0 at the null (p95 ≤ 0.35), so they work as a "don't allocate" detector.

## 3. Estimator accuracy vs known truth (1200 studies per regime)

Pooled bias / RMSE, in points:

| regime | d_in | d_split | eb (linear) | eblog |
|---|---|---|---|---|
| m=400, S/N=25 | +0.09 / 0.47 | −0.18 / 0.71 | −0.58 / 1.21 | −0.13 / 0.50 |
| m=800, S/N=100 | +0.13 / 0.34 | −0.27 / 0.61 | −0.46 / 0.84 | −0.16 / 0.38 |

Findings:
- eblog beats d_split in RMSE, by 30–40%.
- eblog does **not** beat plain d_in in RMSE, because with U-statistic curves d_in's bias is already small.
- Linear eb over-shrinks and should be dropped.

## 4. Level vs spread (true headroom, windowed sets, Spearman)

| knob | solver | ρ(true, spread) | ρ(true, level) |
|---|---|---|---|
| cluster | AM / SymNCO / POMO | +0.78..+0.85 / +0.91..+0.92 / +0.75..+0.77 | ≈ 0 (−0.27..+0.33) |
| size    | AM / SymNCO / POMO | +0.12..+0.23 / +0.53..+0.63 / +0.32..+0.42 | **−0.83..−0.88 / −0.38..−0.83 / −0.59..−0.65** |

Findings:
- Under the cluster knob, spread dominates.
- Under the size knob, **level dominates (negatively)**. So "level << spread" is not universal even within NCO. The theory needs channel (a), the irreducible share, or channel (b), shape changing with n, to account for this. This must be checked by fitting a_i, b_i, α_i.
