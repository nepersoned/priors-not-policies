# Search protocol and log — adaptive test-time compute allocation survey

Search date: 2026-10-01. Date range: 2022-01-01 to 2026-09-30.

## Research question
Among papers that propose or evaluate instance-/query-adaptive allocation of inference-time compute, how often
(i) is the allocation decided and evaluated on the same data (in-sample), and (ii) is the compute spent on the
allocation signal left out of the reported budget?

## Inclusion criteria
- Proposes or evaluates an allocation of inference-time compute (samples for best-of-n / self-consistency, search
  width/depth, restarts, verifier calls, reasoning tokens, model+sample routing) that differs per instance/query.
- Reports a gain vs a uniform/fixed allocation (accuracy, reward, cost/tokens saved at matched quality, etc.).
- 2022–2026, arXiv preprint or peer-reviewed venue, full text accessible.

## Exclusion criteria
- Fixed per-instance budgets (e.g., weighted voting at fixed N; fixed early-decoding window).
- Allocation only at the task/dataset level (one allocation shared by all instances of a task).
- Training-time rollout allocation (RL fine-tuning) with no inference-time allocation claim.
- Surveys, position papers, pure analyses without an allocation-gain claim (kept as "related" if they discuss
  selection bias).

## Sources and queries

### S1. Forward citations (Semantic Scholar Graph API, `/paper/arXiv:<id>/citations`, fields title+abstract+year)
| Seed | Citing papers retrieved |
|---|---|
| Snell et al. 2024, arXiv:2408.03314 | 2,219 |
| Damani et al. 2024, arXiv:2410.04707 | 78 |
| Aggarwal et al. 2023 (Adaptive-Consistency), arXiv:2305.11860 | 162 |
| Union (deduplicated) | 2,366 |

Automated title+abstract screen (Python regex, case-insensitive), 2022+:
`allocat\w*\s+(\w+\s+){0,4}(compute|budget|samples|tokens|inference|test-time)` OR `(compute|budget|sample)s?\s+allocation`
OR `per-(query|instance|prompt|question|problem)\s+(\w+\s+){0,2}(budget|compute|allocation|sampl)` OR
`difficulty[- ](aware|adaptive)` OR `adaptive(ly)?\s+(\w+\s+){0,2}(sampl|allocat|budget|compute|self-consisten|best-of|test-time|inference)`
OR `early[- ]stopping\s+(\w+\s+){0,2}(sampl|self-consisten)`
-> 220 records passed. These 220 titles were manually screened by title/abstract (list: `_work/screen.txt`,
); candidates were sent to full-text coding.

### S2. Keyword search (Semantic Scholar /paper/search, year=2022-2026, top 100 per query)
(queries and hit counts are filled in below)

### S3. Web search (Google-style engine via WebSearch tool; used as a Google Scholar proxy)
1. `adaptive test-time compute allocation selection bias evaluation same samples optimistic best-of-n per-query budget`
2. `arXiv 2025 difficulty-adaptive sampling budget allocation LLM reasoning per-query best-of-N`
3. `"optimizer's curse" OR "winner's curse" test-time compute LLM adaptive allocation`
4. `neural combinatorial optimization adaptive test-time sampling budget per-instance allocation augmentation`
5. `arXiv adaptive best-of-N allocation across prompts reward model budget "allocation" 2025 LLM inference`
6. `adaptive self-consistency early stopping sampling LLM arXiv 2024 2025`
7. `instance-adaptive inference compute allocation per-instance sampling budget arXiv 2025 2026 test-time scaling`
8. `"selection bias" adaptive compute allocation LLM test-time evaluation held-out "same samples"`
(+ non-LLM queries run by coder E; see partials/batch_E.md "Search log")

### S4. arXiv API
Attempted (export.arxiv.org, 12 abstract queries) but all requests failed with HTTP 429/503 rate limiting on
2026-10-01; not used. Recorded for transparency.

### S5. Seeds supplied by the requester
Snell 2408.03314; Damani 2410.04707; Brown 2407.21787; Aggarwal 2305.11860.

### S2 results (Semantic Scholar keyword search, run 2026-10-01)
| Query | Total reported | Retrieved |
|---|---|---|
| difficulty-aware test-time compute allocation | 5,021 | 100 |
| test-time compute budget allocation per query | 422 | 100 |
| compute-optimal test-time scaling difficulty | 21,185 | 100 |
| early exit reasoning model thinking adaptive | 2,163 | 100 |
| adaptive self-consistency early stopping; adaptive best-of-n sampling budget; adaptive sampling budget LLM reasoning; instance-wise test-time budget allocation neural combinatorial optimization; adaptive token budget reasoning difficulty; input-adaptive allocation language model computation | — | FAILED (HTTP 429 rate limit; a second pass with up to 8 attempts per query and 30 s backoff also failed) |

The 400 retrieved records were deduplicated against S1; titles matching `adaptiv|allocat|budget|early|difficult|per-|instance|stop`
were screened manually -> 10 new candidates (coded in partials/batch_G.md).

## Screening flow (PRISMA-style)
| Stage | Records |
|---|---|
| S1 forward citations (union of 3 seeds) | 2,366 |
| after automated title/abstract regex screen | 220 |
| after manual title/abstract screen (S1) | ~75 candidates |
| + S2 keyword search new candidates | 10 |
| + S3 web search / coder E non-LLM search / requester seeds (not in S1) | ~22 |
| Full-text assessed (unique papers) | 107 |
| Excluded at full text (reasons in allocation_survey.md) | 13 |
| **Included and coded** | **94** |
| Related-work notes (selection bias, not coded) | 3 (2605.05973, 2511.00751, 2608.07303) |

Coding: 8 coder batches (partials/batch_0, A–G) using partials/CODEBOOK.md. Batch 0 by lead coder; A–G by separate
coder agents. Batches A, E, F, G verified quotes against downloaded full text (PDF/HTML string search); batches 0, B, C, D
relied on WebFetch extractions that were asked for verbatim text but not string-verified — spot-check before quoting.
Normalization of free-text codes to categories: scripted (`_work/_parsed.json` -> `_work/_norm2.json`) plus manual overrides listed in
allocation_survey.md ("Normalization overrides").

## Known limitations of the protocol
- arXiv API unavailable (rate limited); Google Scholar not queried directly (web search used as proxy).
- Semantic Scholar keyword search partly failed (6/10 queries).
- Forward-citation coverage is strongest for papers citing Snell et al.; papers citing neither seed nor matching the
  keyword queries may be missed.
- Manual title screen of the 220 S1 hits was done by one screener (no double screening).
- Many 2026 arXiv IDs are recent preprints; versions may change (e.g., 2607.08665 v1 vs v3).
