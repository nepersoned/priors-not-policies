# LLM-assisted, author-reviewed verification of 10 random E2 papers (2026-10-01)

**Procedure (corrected 2026-10-02 by the author).** The check was LLM-assisted. An LLM read each paper and proposed the verdict, and the author reviewed the verdicts and judged the ambiguous cases personally. An earlier version of this note said the author opened every paper; that was inaccurate.

**Question asked:** do harder inputs get MORE budget, with no discount for hopeless ones?

## Verdicts

| # | id | author verdict | strict re-judgment (e2_strict.jsonl) | note |
|---|---|---|---|---|
| 1 | 2609.08650 DATPO | yes | yes | K̂ = ⌈K_max(1−V)⌉; V = 0 gets the maximum. **Train-time RLVR rollouts, not test-time** (scope caveat). |
| 2 | 2603.08251 CoFiCot | yes | no (a) | Iteration counts 0/2/3 by tier (Sec 4.1, App. E). The unit is refinement rounds, so this is a definitional difference. |
| 3 | 2605.08057 CA-SQL | yes | no (a) | C rounds of generation + refinement, from a prior LLM rating. Refinement unit, so definitional. |
| 4 | 2608.03961 | yes | yes | App. C.1 rule 9; floor N ≥ min(6, N_max) when c > 0.6. |
| 5 | 2607.01612 | yes | yes | Sample until P_stop or N. **P_stop tuned on the evaluation sets (E4).** |
| 6 | 2608.03222 FailFast | unclear (leans no) | no (c) | Aborting predicted failures is itself a discount; there is one retry per alarm. |
| 7 | 2503.00031 | yes | yes | k ← k+1 while c < τ; the cap comes from the experiment budget. |
| 8 | 2604.21018 | yes | yes | Unresolved queries keep K per round. **The signal is the ground-truth label.** Findings of ACL 2026. |
| 9 | 2506.09338 IAS | yes | yes | N grows without bound as p → 0 and hits N_max. |
| 10 | 2504.16760 LiLaVe | yes | yes | Binary trigger below threshold s (Sec 4). ICLR 2025 Workshop (VerifAI). |

## Agreement

- **Strict "yes":** 7 of 7 are confirmed by the author.
- **Strict "no":** 3 papers. For 2 of them the author said "yes" under the broader wording (refinement rounds count). The third (FailFast) the author marked "unclear, leans no".
- **No factual disagreements.** Every difference concerns scope: refinement rounds vs. repeated attempts.

## Actions for the paper

1. Report author verification as above.
2. State explicitly that the strict definition excludes refinement and length allocation. Under the broader definition, 2603.08251 and 2605.08057 would be added.
3. Mark 2609.08650 as train-time. If the paper restricts the scope to test-time, report "18 test-time + 1 train-time".
4. Note E4 for 2607.01612, and the ground-truth signal for 2604.21018.
