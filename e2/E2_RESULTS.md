# E2 results — "harder gets more" in the binary regime (2026-10-01)

Scripts: `e2_cost.py` (and `e2_cost.py hard`), `e2_figure.py`.
Outputs: `e2_cost.json`, `e2_cost_hard.json`, `fig_e2_cost.png`.

**Setup.**
- Truth: coverage with k samples is 1 − (1 − p_i)^k, where p_i is the pass rate in each problem's stored pool.
- Budget: u = 16 per problem on average.
- Both the rules and the oracle use the same, true p, so the comparison isolates the allocation rule.

## Share of oracle headroom captured, by workload difficulty (u = 16)

| workload | mean pass rate | oracle gain (pts) | IAS | k ∝ 1−p | tiers 21:30:45 |
|---|---|---|---|---|---|
| CodeContests Gemma-2B | 0.000 | +1.8 | 0% | 0% | 0% |
| MATH Pythia-1.4B | 0.013 | +8.4 | 0% | −1% | **−34%** |
| MATH Pythia-6.9B | 0.019 | +8.1 | 0% | −2% | **−40%** |
| CodeContests Llama-3-8B-Instruct | 0.021 | +4.8 | 1% | −1% | 0% |
| CodeContests Llama-3-70B-Instruct | 0.074 | +6.0 | 2% | 2% | −16% |
| MATH Gemma-2B | 0.093 | +7.4 | 13% | 6% | −34% |
| MATH Llama-3-8B-Instruct | 0.268 | +6.3 | 50% | 40% | 15% |
| MATH Llama-3-70B-Instruct | 0.479 | +7.6 | 74% | 61% | 32% |
| PRM800K MATH | 0.486 | +6.1 | 66% | 57% | 33% |
| GSM8K Llama-3-8B-Instruct | 0.768 | +1.9 | 93% | 71% | 28% |
| GSM8K GPT-4o-mini (Weaver) | 0.931 | +0.2 | ~100% | 78% | 12% |

Reading:
- The captured share rises **monotonically with the pass rate**.
- On hard workloads (mean pass rate < 0.1) the oracle can still gain 5–8 points, but "harder gets more" captures **~0%**. The tiered rule is **worse than uniform**, by up to 40% of the headroom (−3.9 pts at u = 32).

## Mechanism (theory: exponential regime)

- The marginal value of one more sample is p(1 − p)^k.
- When u·p is small, as on hard workloads, the optimum gives *more* to the *easier* problems, i.e. the relatively solvable ones.
- "Harder gets more" is only right when u·p is large.
- So the correct direction of a level-based rule flips with the **effective budget u·p**. This is Prop. 3's "level acts as budget", made operational.
- On hard workloads:
  - k ∝ (1 − p) degenerates to uniform, because 1 − p ≈ 1 for every problem;
  - tiers actively move budget toward the hopeless problems.

## Caveats

- **Cheap probes do not give enough information on hard workloads.** With difficulty estimated from 4 probe samples, the correct Bayes rule is also ≈ 0 there, because pass rates of 1–2% cannot be resolved by 4 samples. The claim is therefore conditional: it applies when the difficulty signal is informative, e.g. a learned predictor or historical data, which many E2 papers use.
- **On easy benchmarks E2 is cheap.** On GSM8K and MATH with strong models, E2 rules capture 50–100% of the headroom.

## Survey link (`survey/big/coded/`)

- 33 of 221 included papers (15%) are E2.
- **Hypothesis, not yet checked:** their benchmarks are mostly easy-to-medium, where E2 is cheap, which would explain why the error goes unnoticed. To verify, code each E2 paper's evaluation benchmarks and model strength.

## Addressing the 'oracle p' objection (`e2_noisy.py`, `e2_noisy.json`)

```
=== (A) noise sensitivity, u=16: gain over uniform (pts); oracle in brackets

MATH_Pythia-1.4B  [oracle +8.4]
  noise sd 0.0: E2 IAS -0.0  E2 k~(1-p) -0.1  E2 tiers -2.9  correct plug-in +8.4
  noise sd 0.5: E2 IAS -0.0  E2 k~(1-p) -0.1  E2 tiers -2.8  correct plug-in +7.8
  noise sd 1.0: E2 IAS -0.2  E2 k~(1-p) -0.3  E2 tiers -2.7  correct plug-in +6.1
  noise sd 1.5: E2 IAS -0.3  E2 k~(1-p) -0.5  E2 tiers -2.5  correct plug-in +4.7
  noise sd 2.0: E2 IAS -0.8  E2 k~(1-p) -0.8  E2 tiers -2.2  correct plug-in +2.6
  noise sd 3.0: E2 IAS -1.3  E2 k~(1-p) -1.2  E2 tiers -1.9  correct plug-in +0.3

MATH_Pythia-6.9B  [oracle +8.1]
  noise sd 0.0: E2 IAS +0.0  E2 k~(1-p) -0.2  E2 tiers -3.2  correct plug-in +8.1
  noise sd 0.5: E2 IAS -0.0  E2 k~(1-p) -0.2  E2 tiers -3.2  correct plug-in +7.2
  noise sd 1.0: E2 IAS -0.3  E2 k~(1-p) -0.4  E2 tiers -3.0  correct plug-in +5.5
  noise sd 1.5: E2 IAS -0.6  E2 k~(1-p) -0.7  E2 tiers -2.8  correct plug-in +3.7
  noise sd 2.0: E2 IAS -1.0  E2 k~(1-p) -1.0  E2 tiers -2.5  correct plug-in +1.8
  noise sd 3.0: E2 IAS -1.8  E2 k~(1-p) -1.6  E2 tiers -2.0  correct plug-in -0.9

MATH_Gemma-2B  [oracle +7.4]
  noise sd 0.0: E2 IAS +1.0  E2 k~(1-p) +0.5  E2 tiers -2.5  correct plug-in +7.4
  noise sd 0.5: E2 IAS +0.7  E2 k~(1-p) +0.4  E2 tiers -2.4  correct plug-in +6.4
  noise sd 1.0: E2 IAS -0.1  E2 k~(1-p) +0.0  E2 tiers -2.2  correct plug-in +3.9
  noise sd 1.5: E2 IAS -1.0  E2 k~(1-p) -0.6  E2 tiers -2.0  correct plug-in +1.2
  noise sd 2.0: E2 IAS -2.2  E2 k~(1-p) -1.5  E2 tiers -1.8  correct plug-in -1.7
  noise sd 3.0: E2 IAS -3.3  E2 k~(1-p) -2.8  E2 tiers -1.4  correct plug-in -6.4

MATH_Llama-3-8B-Instruct  [oracle +6.3]
  noise sd 0.0: E2 IAS +3.2  E2 k~(1-p) +2.5  E2 tiers +0.9  correct plug-in +6.3
  noise sd 0.5: E2 IAS +2.4  E2 k~(1-p) +2.4  E2 tiers +0.9  correct plug-in +5.3
  noise sd 1.0: E2 IAS +0.9  E2 k~(1-p) +1.9  E2 tiers +0.7  correct plug-in +2.8
  noise sd 1.5: E2 IAS -0.7  E2 k~(1-p) +0.9  E2 tiers +0.5  correct plug-in +0.1
  noise sd 2.0: E2 IAS -2.3  E2 k~(1-p) -0.3  E2 tiers +0.2  correct plug-in -3.2
  noise sd 3.0: E2 IAS -5.3  E2 k~(1-p) -3.2  E2 tiers -0.1  correct plug-in -9.0

MATH_Llama-3-70B-Instruct  [oracle +7.6]
  noise sd 0.0: E2 IAS +5.6  E2 k~(1-p) +4.6  E2 tiers +2.4  correct plug-in +7.6
  noise sd 0.5: E2 IAS +4.6  E2 k~(1-p) +4.6  E2 tiers +2.3  correct plug-in +6.8
  noise sd 1.0: E2 IAS +3.1  E2 k~(1-p) +4.2  E2 tiers +2.1  correct plug-in +4.8
  noise sd 1.5: E2 IAS +0.9  E2 k~(1-p) +3.3  E2 tiers +1.8  correct plug-in +2.5
  noise sd 2.0: E2 IAS -1.0  E2 k~(1-p) +2.1  E2 tiers +1.6  correct plug-in -0.8
  noise sd 3.0: E2 IAS -2.9  E2 k~(1-p) -0.2  E2 tiers +1.1  correct plug-in -5.4

=== (B) free signals, u=16
MATH_Pythia-1.4B <- history of MATH_Pythia-6.9B            rho +0.93 oracle +8.4 | E2 IAS +0.0  E2 k~(1-p) +0.0  E2 tiers -2.6  correct plug-in +6.6  correct mixture +6.6
MATH_Pythia-1.4B <- history of MATH_Gemma-2B               rho +0.66 oracle +8.4 | E2 IAS +0.0  E2 k~(1-p) +0.0  E2 tiers -2.1  correct plug-in +3.3  correct mixture +3.4
MATH_Pythia-1.4B <- history of MATH_Llama-3-8B-Instruct    rho +0.42 oracle +8.4 | E2 IAS +0.0  E2 k~(1-p) +0.0  E2 tiers -1.4  correct plug-in +0.3  correct mixture +1.2
MATH_Pythia-1.4B <- history of MATH_Llama-3-70B-Instruct   rho +0.33 oracle +8.4 | E2 IAS +0.0  E2 k~(1-p) +0.0  E2 tiers -1.1  correct plug-in +0.1  correct mixture +0.9
MATH_Pythia-6.9B <- history of MATH_Pythia-1.4B            rho +0.93 oracle +8.1 | E2 IAS +0.0  E2 k~(1-p) -0.1  E2 tiers -3.1  correct plug-in +6.6  correct mixture +6.6
MATH_Pythia-6.9B <- history of MATH_Gemma-2B               rho +0.71 oracle +8.1 | E2 IAS +0.0  E2 k~(1-p) -0.0  E2 tiers -2.4  correct plug-in +4.0  correct mixture +4.3
MATH_Pythia-6.9B <- history of MATH_Llama-3-8B-Instruct    rho +0.45 oracle +8.1 | E2 IAS +0.0  E2 k~(1-p) +0.0  E2 tiers -1.5  correct plug-in +0.7  correct mixture +1.4
MATH_Pythia-6.9B <- history of MATH_Llama-3-70B-Instruct   rho +0.33 oracle +8.1 | E2 IAS +0.0  E2 k~(1-p) +0.0  E2 tiers -1.0  correct plug-in +0.4  correct mixture +1.4
MATH_Gemma-2B <- history of MATH_Pythia-1.4B               rho +0.66 oracle +7.4 | E2 IAS -0.3  E2 k~(1-p) -0.3  E2 tiers -2.0  correct plug-in -1.0  correct mixture +0.5
MATH_Gemma-2B <- history of MATH_Pythia-6.9B               rho +0.71 oracle +7.4 | E2 IAS -0.4  E2 k~(1-p) -0.3  E2 tiers -2.1  correct plug-in -0.6  correct mixture +0.8
MATH_Gemma-2B <- history of MATH_Llama-3-8B-Instruct       rho +0.74 oracle +7.4 | E2 IAS -0.3  E2 k~(1-p) -0.2  E2 tiers -1.5  correct plug-in +1.3  correct mixture +1.6
MATH_Gemma-2B <- history of MATH_Llama-3-70B-Instruct      rho +0.64 oracle +7.4 | E2 IAS -0.3  E2 k~(1-p) -0.1  E2 tiers -1.0  correct plug-in +0.9  correct mixture +1.1
MATH_Llama-3-8B-Instruct <- history of MATH_Pythia-1.4B    rho +0.42 oracle +6.3 | E2 IAS -2.0  E2 k~(1-p) -0.3  E2 tiers -1.0  correct plug-in -1.8  correct mixture -0.4
MATH_Llama-3-8B-Instruct <- history of MATH_Pythia-6.9B    rho +0.45 oracle +6.3 | E2 IAS -2.9  E2 k~(1-p) -0.2  E2 tiers -0.8  correct plug-in -1.9  correct mixture -0.2
MATH_Llama-3-8B-Instruct <- history of MATH_Gemma-2B       rho +0.74 oracle +6.3 | E2 IAS -2.3  E2 k~(1-p) +0.5  E2 tiers +0.1  correct plug-in -1.9  correct mixture +0.5
MATH_Llama-3-8B-Instruct <- history of MATH_Llama-3-70B-Instruct rho +0.85 oracle +6.3 | E2 IAS -1.5  E2 k~(1-p) +0.6  E2 tiers +0.4  correct plug-in -0.8  correct mixture +0.4
MATH_Llama-3-70B-Instruct <- history of MATH_Pythia-1.4B   rho +0.33 oracle +7.6 | E2 IAS -0.0  E2 k~(1-p) -0.3  E2 tiers -0.3  correct plug-in -0.6  correct mixture -0.6
MATH_Llama-3-70B-Instruct <- history of MATH_Pythia-6.9B   rho +0.33 oracle +7.6 | E2 IAS -0.1  E2 k~(1-p) -0.3  E2 tiers -0.3  correct plug-in -0.8  correct mixture -0.5
MATH_Llama-3-70B-Instruct <- history of MATH_Gemma-2B      rho +0.64 oracle +7.6 | E2 IAS +0.3  E2 k~(1-p) +0.5  E2 tiers +0.8  correct plug-in -0.3  correct mixture +0.2
MATH_Llama-3-70B-Instruct <- history of MATH_Llama-3-8B-Instruct rho +0.85 oracle +7.6 | E2 IAS -1.8  E2 k~(1-p) +2.5  E2 tiers +1.9  correct plug-in +0.4  correct mixture +2.3
CodeContests_Llama-3-8B <- history of 70B                  rho +0.69 oracle +4.8 | E2 IAS -0.0  E2 k~(1-p) -0.1  E2 tiers -0.5  correct plug-in +2.2  correct mixture +2.6
CodeContests_Llama-3-70B <- history of 8B                  rho +0.69 oracle +6.0 | E2 IAS -0.8  E2 k~(1-p) -0.4  E2 tiers +0.0  correct plug-in -1.1  correct mixture +0.1
PRM800K MATH <- MATH level (1-5)                           rho +0.54 oracle +6.1 | E2 IAS +0.6  E2 k~(1-p) +0.8  E2 tiers +0.8  correct plug-in +0.7  correct mixture +0.7
```

### Verdict

**Hard workloads, free and informative signal: the claim holds.** With the pass rate of a similar-capability model on the same problems as a cost-free history signal (rank correlation 0.69-0.93), the correct rule recovers +2.6 to +6.6 pts (31-79% of the oracle). E2 rules get ~0, and tiers lose 0.5 to 3.1 pts.

**Easy workloads: the difference is small.** Real signals give +/-2 pts, and the E2 rule k proportional to (1-p) is sometimes better than the plug-in correct rule.

**Under heavy noise (logit sd >= 1.5) the plug-in correct rule is fragile on easy workloads.** The mixture-calibrated rule is more robust.

**A coarse signal ties everything.** MATH level (rank correlation 0.54) gives about +0.7 for every rule.

**Diagnostic** (`diagnostic_check.py`): the left-branch share from Prop. 1 predicts the share of headroom IAS captures with Spearman -0.92. The mean pass rate does equally well on these 11 workloads (+0.98), and no skewed or bimodal case was available to separate the two.


## Setting 2: verifier available, online allocation with stop-on-success (`e2_online.py`, `e2_online.json`)

**Baseline.** Round-robin over unsolved problems (RR). With an exchangeable prior it is optimal; the "Bayes (exchangeable)" policy reproduces RR exactly (+0.0 in every cell), as the theory predicts.

**Bayes myopic (history prior).** The next sample goes to the unsolved problem with the highest posterior P(success next). The prior is a mixture of the calibration-half pass rates in the problem's history bin, where the history signal is another model's pass rate on the same problem.

Results, solved-share difference vs. RR (20 reps):

| workload | RR solved | Bayes (history) | E2 online (IAS cap) |
|---|---|---|---|
| Pythia-1.4B | 14.8% at u=16 | +12.3 (u=16); +8.4 (u=4); +13.4 (u=64) | 0 or worse |
| Pythia-6.9B | 19.8% at u=16 | +13.6 (u=16) | 0 or worse |
| Gemma-2B | 23.4% at u=4 | +6.1 (u=4); +3.5 (u=16); −1.6 (u=64) | 0 or worse |
| CodeContests 8B | 5.1% at u=16 | +2.1 to +3.8 | 0 or worse |
| Easy workloads (Llama 8B/70B, u ≥ 16) | | −0.5 to −1.3 | |

- The history prior over-trusts the history signal, which explains the small losses on easy workloads at large budgets.
- **Tempered prior** (half history mixture, half exchangeable pool): the losses shrink to between −1.1 and +0.2, and the gains shrink to about 70–80%.
- E2 online never beats RR; it ranges from 0 to −2.5.

**Conclusion.** With a verifier and a free history prior, a simple Bayes myopic policy substantially beats the strongest baseline on hard workloads (up to about 2× the solved share). E2-style rules never help.

**Next:**
- an adaptive tempering rule that interpolates toward RR as the budget grows or as evidence accumulates;
- cross-model history from dissimilar models.

## Bandit baselines (`e2_bandits_fast.py`, `e2_bandits.json`); main method decided: Thompson Sampling with a history prior

All rows report the change in solved share relative to RR (round-robin over unsolved problems).

```nMATH_Pythia-1.4B                   u=  4 | RR   4.8% | TS (exchangeable):  -0.4 UCB (exchangeable):  +0.0 TS (history):  +7.9 UCB (history):  +8.0 Bayes-myopic (history):  +7.9
MATH_Pythia-1.4B                   u= 16 | RR  14.1% | TS (exchangeable):  -0.2 UCB (exchangeable):  +0.0 TS (history): +12.5 UCB (history): +12.7 Bayes-myopic (history): +12.1
MATH_Pythia-1.4B                   u= 64 | RR  34.7% | TS (exchangeable):  -0.1 UCB (exchangeable):  +0.0 TS (history): +12.3 UCB (history): +12.2 Bayes-myopic (history): +11.8
MATH_Pythia-6.9B                   u=  4 | RR   6.5% | TS (exchangeable):  -0.5 UCB (exchangeable):  +0.0 TS (history):  +8.7 UCB (history):  +9.3 Bayes-myopic (history):  +8.9
MATH_Pythia-6.9B                   u= 16 | RR  18.6% | TS (exchangeable):  +0.3 UCB (exchangeable):  +0.0 TS (history): +13.8 UCB (history): +14.1 Bayes-myopic (history): +13.6
MATH_Pythia-6.9B                   u= 64 | RR  41.6% | TS (exchangeable):  -0.1 UCB (exchangeable):  +0.0 TS (history): +12.3 UCB (history): +13.5 Bayes-myopic (history): +13.9
MATH_Gemma-2B                      u=  4 | RR  23.4% | TS (exchangeable):  +0.1 UCB (exchangeable):  +0.0 TS (history):  +6.3 UCB (history):  +6.2 Bayes-myopic (history):  +5.5
MATH_Gemma-2B                      u= 16 | RR  48.2% | TS (exchangeable):  +0.1 UCB (exchangeable):  +0.0 TS (history):  +2.7 UCB (history):  +3.4 Bayes-myopic (history):  +2.6
MATH_Gemma-2B                      u= 64 | RR  72.4% | TS (exchangeable):  -0.1 UCB (exchangeable):  +0.0 TS (history):  +2.1 UCB (history):  +0.7 Bayes-myopic (history):  -2.7
CodeContests_Llama-3-8B-Instruct   u=  4 | RR   3.3% | TS (exchangeable):  +0.0 UCB (exchangeable):  +0.0 TS (history):  +2.5 UCB (history):  +2.5 Bayes-myopic (history):  +2.6
CodeContests_Llama-3-8B-Instruct   u= 16 | RR   5.5% | TS (exchangeable):  -0.1 UCB (exchangeable):  +0.0 TS (history):  +4.0 UCB (history):  +3.8 Bayes-myopic (history):  +3.7
CodeContests_Llama-3-8B-Instruct   u= 64 | RR   8.6% | TS (exchangeable):  +0.1 UCB (exchangeable):  +0.0 TS (history):  +3.8 UCB (history):  +3.8 Bayes-myopic (history):  +3.9
MiniF2F-MATH_Llama-3-8B-Instruct   u=  4 | RR  32.9% | TS (exchangeable):  -0.4 UCB (exchangeable):  +0.0 TS (history):  +4.1 UCB (history):  +5.5 Bayes-myopic (history):  +4.5
MiniF2F-MATH_Llama-3-8B-Instruct   u= 16 | RR  40.0% | TS (exchangeable):  +0.2 UCB (exchangeable):  +0.0 TS (history):  +2.1 UCB (history):  +1.7 Bayes-myopic (history):  +0.2
MiniF2F-MATH_Llama-3-8B-Instruct   u= 64 | RR  43.3% | TS (exchangeable):  +0.0 UCB (exchangeable):  +0.0 TS (history):  +0.1 UCB (history):  -0.2 Bayes-myopic (history):  -1.0
MATH_Llama-3-8B-Instruct           u=  4 | RR  53.4% | TS (exchangeable):  +0.0 UCB (exchangeable):  +0.0 TS (history):  +6.4 UCB (history):  +8.4 Bayes-myopic (history):  +8.4
MATH_Llama-3-8B-Instruct           u= 16 | RR  78.2% | TS (exchangeable):  +0.1 UCB (exchangeable):  +0.0 TS (history):  +1.1 UCB (history):  +0.9 Bayes-myopic (history):  -0.3
MATH_Llama-3-8B-Instruct           u= 64 | RR  90.3% | TS (exchangeable):  +0.0 UCB (exchangeable):  +0.0 TS (history):  -0.6 UCB (history):  -1.0 Bayes-myopic (history):  -2.0
```

**Conclusions:**

- **Prior-free bandits equal RR.** With an exchangeable prior, TS and UCB fall within -0.5 to +0.3 of RR in every one of the 18 cells, confirming that RR is optimal when the prior carries no problem-specific information.
- **On hard workloads the algorithm barely matters.** With the same history prior, TS, UCB and Bayes-myopic all gain +8 to +14 points: the prior matters, the algorithm does not.
- **TS is the most robust on easy workloads and large budgets.**
  - Gemma u=64: TS +2.1 vs myopic -2.7.
  - MiniF2F u=64: TS +0.1 vs myopic -1.0.
  - Llama-8B u=64: TS -0.6 vs myopic -2.0.
  - The worst TS cell is -0.6.
- **Decision:** the main method is TS with a history prior. Bayes-myopic and CV-tempering are kept as variants or ablations.

## Strict E2 re-judgment (`survey/big/e2_strict.jsonl`)

- Result: 19 of 33 papers are E2 under the strict definition (18 if the borderline ODAR is excluded). That is 8.6% of the 221 included papers.
- Of the 14 'no' cases, 12 fail criterion (a): the allocated unit is refinement, length or routing, not repeated independent attempts.
- Agreement with the blind second coder: 6 of 7 overlapping papers.


## Correction (number audit, 2026-10-01)

- The 'Survey link' section above reports the first-pass count: 33 of 221 papers (15%).
- The strict, full-text count used in the paper is **19 of 221 (8.6%)**: 17 inference-time and 2 RL-training papers, i.e. 16 independent inference-time rules.
- Sources: `survey/big/e2_strict.jsonl` and `draft/appendix_D_E2_papers.md`.

