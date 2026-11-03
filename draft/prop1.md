# Proposition 1 (binary regime) — statement and proof

## Setup

- Input i has pass rate p_i ∈ (0, 1).
- Define its rate as r_i = −ln(1 − p_i) > 0. Then the failure probability after k samples is (1 − p_i)^k = e^{−r_i k}.
- Maximise Σ_i [1 − e^{−r_i k_i}] subject to Σ_i k_i = S and k_i ≥ 0 (continuous relaxation; the integer version is handled by greedy allocation on marginals).

## Lemma (marginal value)

The discrete marginal of one more sample is Δ(p, k) = p(1 − p)^k. Its derivative in p is

  ∂Δ/∂p = (1 − p)^{k−1} (1 − (k + 1)p).

So Δ increases on [0, 1/(k+1)] and decreases on [1/(k+1), 1], with its peak at p* = 1/(k+1).

## Proposition 1 (the optimal allocation is inverted-U in difficulty)

The KKT conditions give r_i e^{−r_i k_i} = λ for every input with k_i > 0, which yields

  k*(r) = max(0, ln(r/λ) / r),

where λ > 0 is fixed by the budget.

**Properties:**
- (a) k*(r) = 0 for r ≤ λ. These inputs are not worth sampling at this budget.
- (b) Since d/dr [ln(r/λ)/r] = (1 − ln(r/λ)) / r², k* *increases* with r (easier inputs get more) for λ < r < eλ, and *decreases* with r (harder inputs get more) for r > eλ.
- (c) The peak is at r = eλ, where k* = 1/(eλ).
- (d) λ falls as the budget grows, so the peak moves toward harder inputs as the budget grows.

**Corollary (when "harder gets more" is right).**
- A monotone rule in which k decreases with p is optimal-direction only on the right branch, r > eλ.
- When most inputs have r_i < eλ, every monotone harder-gets-more rule moves budget the wrong way. At uniform allocation this means u·r_i is small, i.e. a hard workload or a small budget.

## Proof sketch

The objective is separable and strictly concave in each k_i. Writing the Lagrangian gives r_i e^{−r_i k_i} = λ wherever k_i > 0. Solving for k_i gives the formula above, with k_i = 0 when r_i ≤ λ (complementary slackness). Differentiating in r gives (b). Σ_i k*(r_i; λ) is continuous and strictly decreasing in λ, so λ is unique for each S > 0, which gives (d). ∎

## Diagnostic (replaces the mean-pass-rate rule)

Compute λ from a calibration set at the planned budget. The quantity to report is

  **share of inputs on the left branch** = #{i : r̂_i < eλ} / N.

Interpretation:
- **Large share:** "harder gets more" is wrong for most inputs. Reverse it, or use the greedy rule.
- **Near 0:** the monotone rule is near-optimal.

Unlike the mean pass rate, this works for skewed or bimodal difficulty distributions (Gemini review, weakness 3).

[TODO: verify numerically that the left-branch share predicts the captured share across the 11 workloads (`e2_cost*.json`).]
