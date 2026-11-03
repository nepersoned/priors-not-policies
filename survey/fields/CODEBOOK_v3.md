# Codebook v3 — multi-field survey + prior work (2026-10-01)

## Principle being tested

A fixed budget of repeated attempts or measurements is split across items: instances, tasks, targets, workers, experiments, test-takers. The value of one more unit on item i depends on the shape of its improvement curve.

**Regime C — continuous, power-law.**
- Improvement follows f_i(k) ≈ a_i + b_i k^(−α). Examples:
  - best-of-k of a continuous score (gap, regret, reward, binding score);
  - estimation error that shrinks like 1/n (α = 1: A/B tests, crowdsourced label accuracy via averaging, simulation estimates, adaptive testing).
- Optimal allocation is k_i ∝ b_i^(1/(1+α)) (water-filling).
  - For estimation with variance σ_i²/n this is **Neyman allocation**, n_i ∝ σ_i.
- The level of difficulty cancels. Spread (dispersion of b_i) governs the gain.

**Regime B — binary first-success, exponential.**
- Failure after k attempts is (1 − p_i)^k. Examples:
  - pass@k;
  - "bug found";
  - robot task success;
  - RL rollouts with binary reward.
- The marginal value of one more attempt is p(1 − p)^k, which peaks at p = 1/(k+1).
  - "Harder gets more" is right only when u·p is large.
  - At small u·p, the easier (solvable) items should get more and hopeless ones little.

**Regime H — heavy-tailed runtime.**
- Example: SAT/solver time-to-solve with restarts. It may fit neither regime. Code it, and note the curve shape if reported.

**Regime N/A.** The theory does not apply: no repeated attempts on fixed items, or a different objective such as pure cost at a fixed target.

## Per-paper fields (JSON, one object per line)

| field | content |
|---|---|
| id | arXiv id, DOI or URL |
| title, year, venue | |
| field | which field this paper belongs to |
| include | yes or no |
| exclude_reason | |
| unit | what is allocated |
| items | across what |
| objective | |
| regime | C, B, H or N/A |
| signal | LEVEL, SPREAD, MARGINAL, LEARNED or OTHER (multi-label) |
| direction | for LEVEL: MONO-UP, MONO-DOWN, NON-MONO or unclear |
| spread_rule | for SPREAD: the exponent used (e.g. proportional to SD, to variance, or water-filling) |
| separation | disjoint, online, same-data or unclear |
| signal_cost | charged, partial, not-charged, n/a or unclear |
| flags | list |
| evidence | section + quote of 15 words or fewer |
| fulltext_checked | |
| confidence | |

### Flags

| flag | condition |
|---|---|
| E1 | regime C and LEVEL-only signal |
| E2 | regime B and MONO-UP ("harder gets more", no discount for hopeless items) |
| E3 | SPREAD rule whose exponent does not match the regime's optimum. Proportional to SD is CORRECT for α = 1 estimation (Neyman). It is wrong for best-of-k rewards with α ≠ 1. Proportional to variance is wrong for estimation. |
| E4 | allocation decided or tuned on the evaluation data |
| E5 | signal cost not charged |
| OK | MARGINAL / water-filling / Neyman-correct / NON-MONO in regime B |
| NA | the theory does not apply |

## Prior-work task (per field)

Write `prior_<field>.md`. It must answer whether the field already knows the principle, with citations:
- Is there a classical or optimal allocation result? Examples: Neyman/optimal allocation, Gittins indices, Luby restarts, AFLFast power schedules, OCBA, Opt-KG for crowdsourcing, item selection in computerized adaptive testing.
- Does it say "difficulty level" or "dispersion / marginal gain" decides allocation? Does it warn against "harder gets more" or against spending on hopeless items?
- Give 3–8 key references: full citation, a one-line statement of the result, and whether it is identical to, a special case of, or analogous to our principle.
- Give a verdict: what our paper adds for this field, or "nothing new for this field".
