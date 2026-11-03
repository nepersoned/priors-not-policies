# Human check: 10 random E2 papers

For each paper: open it, find the allocation rule, and mark whether harder inputs get MORE budget with no discount for hopeless ones (E2 = yes).

| # | id | title | coder evidence | your verdict (yes/no/unclear) | note |
|---|---|---|---|---|---|
| 1 | 2609.08650 | Difficulty-Adaptive Tree-Structured Policy Optimization for Expanding  | Sec 3.1: scale the tree expansion proportionally to this difficulty |  |  |
| 2 | 2603.08251 | Not All Queries Need Deep Thought: CoFiCot for Adaptive Coarse-to-fine | Sec 3.2: Hard problems get 3 iterations; Easy bypass refinement loop |  |  |
| 3 | 2605.08057 | CA-SQL: Complexity-Aware Inference Time Reasoning for Text-to-SQL via  | Sec.3.7: generation and refinement repeated C times, C = LLM difficulty level 1-5 |  |  |
| 4 | 2608.03961 | Interpretable Adaptive Sampling for LLM Test-Time Scaling | Sec 3.2: High complexity or low confidence pushes the output toward larger budgets |  |  |
| 5 | 2607.01612 | Scaling with Confidence: Calibrating Confidence of LLMs for Adaptive T | Method: stop "If Prob(c1,c2) >= P_stop"; P_stop varied on test sets |  |  |
| 6 | 2608.03222 | Fail-Fast, Restart-Smart: Early Failure Prediction and Restart for SWE | Method: monitor predicts failure from prefixes; alarm launches fresh rollout |  |  |
| 7 | 2503.00031 | Efficient Test-Time Scaling via Self-Calibration | Method: continue sampling until a response meets the confidence threshold tau |  |  |
| 8 | 2604.21018 | Adaptive Test-Time Compute Allocation with Evolving In-Context Demonst | Sec 4.2.1: "We use ground-truth as our reward model"; unresolved queries get uniform extra rounds |  |  |
| 9 | 2506.09338 | Know What You Don't Know: Uncertainty Calibration of Process Reward Mo | IAS: N = ceil(log(1-C)/log(1-p)), capped at N_max; low p gets max budget |  |  |
| 10 | 2504.16760 | Lightweight Latent Verifiers for Efficient Meta-Generation Strategies | Abstract: "conditional self-correction or conditional majority voting" |  |  |
