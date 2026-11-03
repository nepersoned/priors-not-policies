# LLM-assisted check of the remaining 12 strict-E2 papers: results (2026-10-02)

**Procedure (author's statement, 2026-10-02).** This was an LLM-assisted check. An LLM read each paper and filled in the verdicts and notes, and the author reviewed the results and agreed with them. The author judged the ambiguous cases themselves, and their verdicts agree with those in the table. The earlier random 10 followed the same procedure. In the paper, report these 12 as "LLM-assisted, reviewed by the authors", not as a manual check.

| # | paper | a | b | c | d | verdict | reason |
|---|---|---|---|---|---|---|---|
| 1 | DSC, 2408.13457 | Y | Y | Y | Y | yes | Easy part gets 1 CoT sample; the hard part resamples until a Dirichlet stop or max L. |
| 2 | Think Right, Not More, 2509.22101 | Y | Y | Y | Y | yes | Level 0 is one-shot; level 1 gets BoN (m = 10). Persistently misclassified claims go to level 1. |
| 3 | CoBa, 2608.07424 | ? | Y | Y | Y | unclear | The extra compute is more candidates plus routing the top-K to a strong verifier. |
| 4 | AttnRL, 2509.26628 † | ? | Y | Y | Y | unclear | The unit is MC tree branches from shared prefixes, not independent attempts. Training-time. |
| 5 | ODAR, 2602.23681 | ? | Y | Y | Y | unclear | Hard attempts come from a different, stronger model, so attempts are confounded with routing. |
| 6 | Dynasor, 2412.20993 | Y | Y | **N** | Y | **no** | Explicitly terminates out-of-reach or unpromising queries early, which is a hopeless discount. |
| 7 | Text2Cypher, 2609.02324 | Y | Y | Y | Y | yes | Prior tiers get 21/30/45 traces; the baseline is fixed 45. |
| 8 | FSC, 2608.24590 | Y | Y | Y | Y | yes | N_adj grows with predicted entropy, from 1 to N. |
| 9 | Distributional PRM, 2605.06785 ‡ | Y | Y | Y | ? | unclear | Reuses the IAS rule. No fixed-N comparison was found. Not an independent rule. |
| 10 | LLM Already Knows, 2509.12886 | Y | Y | Y | Y | yes | Above τ: a direct answer. Otherwise: K CoT samples (SC or BoN). |
| 11 | ACTSC, 2602.09438 | Y | Y | Y | Y | yes | Hard inputs get SC with dynamic windows. τ is set transductively per dataset. |
| 12 | Gated GeoBoN, 2607.17454 | **N** | Y | Y | Y | **no** | Step-level BoN over actions inside an episode, not repeated attempts on an input. |

## Combined with the earlier random 10 (7 of the 19 strict-E2 papers, all confirmed)

| | count | papers |
|---|---|---|
| Confirmed: all four conditions hold | **13** | the earlier 7, plus #1, 2, 7, 8, 10 and 11 above |
| Borderline: one condition unclear | 4 | CoBa, AttnRL†, ODAR, Distributional PRM‡ |
| Rejected | 2 | Dynasor (c), Gated GeoBoN (a) |

**Confirmed set.**
- 13 of 221 papers (5.9%).
- 12 of them allocate at inference time; 1 allocates RL training rollouts (DATPO).
- All 12 inference-time rules are independent.

**Counting the borderline papers as well.** That gives 17 of 221 (7.7%).

**Agreement with the strict re-judgment.** Over the 19 papers, the human check agrees on 13. The 2 rejections and 4 borderline cases all concern conditions (a) or (c): what counts as a repeated attempt, and whether early termination is a discount.
