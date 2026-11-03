# Human check: the remaining 12 strict-E2 papers

The earlier random sample of 10 (`human_check_E2_results.md`) covered 7 of the 19 strict-E2 papers. This sheet covers the other 12, so that all 19 are checked by a person.

**Instructions.** For each paper, open the link, go to the section listed, and check the four conditions. Mark each with Y, N or ?. Then give an overall verdict.

- **(a) Repeated attempts.** The allocated unit is independent attempts or samples on the same input. Refinement rounds, reasoning length and model routing do not count.
- **(b) Harder gets more.** A difficulty or confidence signal gives harder inputs more attempts, monotonically.
- **(c) No discount for hopeless inputs.** Nothing abstains on, skips or deprioritizes inputs that look unsolvable. A global cap that every input can reach is not a discount.
- **(d) Compared with uniform.** The method is evaluated against uniform or fixed allocation.

**Overall verdict:** "yes" if (a)–(d) all hold, "no" if any fails, and "unclear" otherwise.

**Time.** About 5 minutes per paper; the rule is usually in one equation or algorithm.

| # | paper | link | where to look | rule as coded (to confirm) | a | b | c | d | verdict | note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Make Every Penny Count (DSC) | https://arxiv.org/abs/2408.13457 | §2, §2.3 | Easy: 1 sample. Hard: resample until a stopping criterion, cap 40. | | | | | | |
| 2 | Think Right, Not More | https://arxiv.org/abs/2509.22101 | §3.2 | Level-0 claims: one shot. Level-1 claims: expanded best-of-N. | | | | | | |
| 3 | CoBa | https://arxiv.org/abs/2608.07424 | Alg. 1 (§4) | Add one candidate at a time until the top answer is stable and highly scored, up to max. | | | | | | |
| 4 | AttnRL (RL training) | https://arxiv.org/abs/2509.26628 | §3.2.1, Eq. 9 | Trees per problem = Round(exp(−pass rate) × 6); zero pass rate gets the maximum. | | | | | | |
| 5 | ODAR | https://arxiv.org/abs/2602.23681 | §3.1 | Hard: 1 fast + 5 slow best-of-N. Easy: 1 fast. Borderline: confounded with model routing. | | | | | | |
| 6 | Certaindex / Dynasor | https://arxiv.org/abs/2412.20993 | App. D.2 | Low certaindex keeps sampling up to the resource cap. Caveat: confidently wrong paths can stop early. | | | | | | |
| 7 | Text2Cypher adaptive inference | https://arxiv.org/abs/2609.02324 | §3.1, §4.2.2 | Easy/medium/hard tiers get 21/30/45 traces. | | | | | | |
| 8 | FSC | https://arxiv.org/abs/2608.24590 | §3.2, Eq. 4 | N_adj = ⌈1 + (N−1)·Ĥ/log₂N⌉, increasing in predicted entropy. | | | | | | |
| 9 | Distributional PRM | https://arxiv.org/abs/2605.06785 | §3 | Reuses the IAS rule (N from estimated success probability, capped at N_max). | | | | | | |
| 10 | LLM Already Knows | https://arxiv.org/abs/2509.12886 | §4 | Easy: 1 sample. Hard: K samples for self-consistency or best-of-N. | | | | | | |
| 11 | ACTSC | https://arxiv.org/abs/2602.09438 | §3.2, Alg. 2 | Hard items sample in windows until Conf ≥ γ, cap 40. | | | | | | |
| 12 | Gated GeoBoN | https://arxiv.org/abs/2607.17454 | Abstract, §3 | Best-of-N (N_max = 8) only when the first rollout looks inconsistent. Borderline: the gate is per step. | | | | | | |

## Points to check in particular

- **#4 AttnRL:** confirm that it allocates RL training rollouts. It is marked † (training-time) in Appendix D.
- **#5 ODAR and #12 Gated GeoBoN:** these are marked borderline. Confirm whether the extra compute is repeated attempts (a), rather than model routing (#5) or step-level search (#12).
- **#6 Dynasor:** check whether early stopping on confident answers applies only to confident inputs. If hopeless inputs can also be stopped early, (c) fails.
- **#9 Distributional PRM:** confirm that it reuses the IAS rule rather than defining a new one. It is marked ‡ (not an independent rule).

## After filling in

Send the filled sheet back. I will:
- compute agreement over all 19 papers;
- update §3 Reliability and Appendix D;
- recount the papers if any verdict is "no".
