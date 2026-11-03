# Codebook v2 — large survey of per-input compute allocation (2026-10-01)

## Unit of analysis

The unit is one paper that allocates inference-time or search compute **non-uniformly across inputs** (queries, prompts, instances, tasks, datasets) and reports a comparison against uniform or fixed allocation.

Compute includes:
- samples (best-of-N)
- search width or depth
- reasoning length
- restarts
- denoising steps
- verifier calls
- rollouts during RL training
- evaluations in HPO/AutoML

Include per-input early stopping when the paper frames it as saving or reallocating budget.

## Fields — code each from the abstract first; escalate to full text if any field is unclear

| field | values |
|---|---|
| id | arXiv id or DOI |
| title, year, venue | |
| domain | LLM-reasoning, LLM-chat/alignment, code, NCO/routing, continuous-opt, HPO/AutoML, SAT/MIP/portfolio, diffusion/image, molecule/protein, RL-training, other |
| unit | what is allocated (samples, length, steps, restarts, calls, rollouts, evals, model choice) |
| constraint | fixed-total (redistribution), cost-at-target, per-input-stopping, other |
| objective | binary (pass/fail, verifier), continuous-bestof (max/min over samples of a continuous score: reward, cost, gap, regret, speedup), continuous-smooth (quality improves smoothly), cost-only, other |
| regime | exponential (binary best-of-k), power-law (continuous best-of-k), n/a |
| signal | LEVEL (predicted difficulty, expected score, pass rate, first-sample score), SPREAD (variance, uncertainty, dispersion, disagreement), MARGINAL (estimated gain from one more unit, bandit/UCB on improvement, water-filling), LEARNED (black-box predictor of budget), OTHER. More than one value is allowed. |
| direction | only if signal includes LEVEL: MONO-UP (harder gets more), MONO-DOWN (easier gets more), NON-MONO (e.g. inverted-U, hopeless inputs get little), unclear |
| spread_rule | only if signal includes SPREAD: PROPORTIONAL (budget proportional to SD/variance), WATERFILL (equalise marginal gains), THRESHOLD, other |
| separation | disjoint / online / same-data / unclear |
| signal_cost | charged / partial / not-charged / n/a / unclear |
| gain | the headline number (quote, ≤15 words) |
| evidence | section + short quote for signal and direction |
| confidence | high / medium / low |

## Verdict flags, derived from the fields

| flag | condition | what it means |
|---|---|---|
| E1 | regime = power-law AND signal = LEVEL only | Level used where the theory says spread governs. |
| E2 | regime = exponential AND direction = MONO-UP | "Harder gets more" in the binary regime, which ignores that hopeless inputs have near-zero marginal gain. |
| E3 | spread_rule = PROPORTIONAL | Spread is used proportionally rather than by water-filling. AdaBoN App. H shows this can equal uniform. |
| OK | signal includes MARGINAL, or (exponential AND NON-MONO), or (power-law AND SPREAD with WATERFILL) | Consistent with the theory. |
| NA | the theory does not apply (cost-only, structural, or within a single input) | |
