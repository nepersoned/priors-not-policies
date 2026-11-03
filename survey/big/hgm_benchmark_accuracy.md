# HGM papers: baseline single-attempt accuracy on main benchmarks

Scope: the 13 "confirmed" HGM papers in `draft/appendix_D_E2_papers.md`. All 13 opened via arxiv.org/html/<id>.
The text was read through WebFetch, which extracts it with a small model. Every number below is as the paper prints it. Accuracies are in %, unless the paper prints decimals; those are converted to % in the median column. Recheck any load-bearing number against the PDF before citing it.

Labels: **P1** = single-attempt accuracy (pass@1, greedy, Best-of-1, or the model's direct answer). **SC@N** = uniform self-consistency at fixed N, used where no single-attempt number exists. SC@N is at least as high as pass@1 on these tasks, so an SC-based "not mostly solved" verdict is conservative and an SC-based "mostly solved" verdict is optimistic.
"Mostly solved" means that more than half of the pairs are at or above 50%.

| # | paper | benchmarks | models | single-attempt acc (per pair, short) | median | mostly solved? | source location |
|---|---|---|---|---|---|---|---|
| 1 | 2408.13457 DSC | MATH, GSM8K, CSQA, StrategyQA, LastLetter, CoinFlip | GPT-4, GPT-3.5-Turbo | **SC@40** (no P1 in main exp). GPT-4: 58.52 / 95.81 / 85.82 / 81.89 / 94.51 / 100. GPT-3.5: 49.43 / 83.22 / 76.80 / 71.47 / 80.44 / 76.60 | 81.2 (SC@40) | Yes (11/12), SC-based | Table 2. The only P1 is MATH500 GPT-3.5 N=1 (27.01 zero-shot, 33.08 few-shot) in App. A.6, Table 11, outside the main experiment |
| 2 | 2604.21018 Evolving ICL demos | MATH-500, LiveCodeBench, MinervaMath, GPQA-D, ReasonGym | Gemini-2.5-flash-lite (think / no-think), GPT-4.1-mini, GPT-5-nano | not reported. Accuracy appears only in figures (Figs. 2–8). Tables report coverage, not accuracy: Table 3 MATH500 GPT-4.1-mini round-0 coverage 88.8; Table 2 MinervaMath Gemini-think R0 coverage 41.5; Table 1 GPQA-D 1-sample coverage 65.2 (model unnamed) | n/a | Cannot determine | Tables 1–3, 5–6; Figs. 2–8 |
| 3 | 2509.22101 Think Right, Not More | QuanTemp, ClaimDecomp | DeepSeek-R1-7B*, Llama-3.1-8B, gpt-4o-mini | **Macro-F1, not accuracy** (top-1 decoding). QuanTemp: R1 42.3*, Llama 44.8, 4o-mini 47.27. ClaimDecomp: R1 38.25*, Llama 36.07, 4o-mini 43.36. Weighted-F1 is 37.15–52.84. *R1 "internally does TTS" | 44.1 (M-F1, top-1 rows); 42.8 with R1 included | No (0/6), F1 metric | Table 1 |
| 4 | 2607.01612 CAS / C3RL | CAS experiment (Sec. 4.2.1): in-domain, MMLU-val, FOLIO, GSM8K, plus multimodal sets (not named in the section; App. A.1.2 lists MathVision, MathVista, LogicVista, MMStar) | Qwen2.5VL-7B-Instruct after C3RL training | P1 of the C3RL model: D_test 64.4, MMLU 71.4, MathVista 0.622, LogicVista 0.446. FOLIO, GSM8K, MMStar: not reported. (The untrained Base gives D_test 45.3, MMLU 68.3, MathVista 0.543, LogicVista 0.368.) The CAS table reports only MV@64: in-domain 67.3, OOD-text 78.1, OOD-MM 57.8 | 63.3 (C3RL P1). Base: 49.8 | Yes (3/4) for the C3RL model. Base: 2/4, a tie, so no | Tables 1–2 (P1), Table 3 (CAS, MV@64), Sec. 4.2.1 |
| 5 | 2504.16760 LiLaVe | GSM-Symbolic (p1 / p2), algebra_linear_1d, MATH500 | Llama 3.1 8B (Gemma-2-2B and Phi-3.5-mini in appendix) | not reported. Accuracy appears only in figures (Figs. 3–5, 12). Tables give verifier AUC only | n/a | Cannot determine | Sec. 4.4, Figs. 3–5 |
| 6 | 2506.09338 IAS (PRM calibration) | MATH500, AIME24-25 | Llama-3.2-1B, Llama-3.1-8B, Qwen2.5-1.5B, Qwen2.5-7B, R1-Llama-8B, R1-Qwen-7B | P1. MATH500: 0.2255 / 0.4659 / 0.6970 / 0.7994 / 0.6734 / 0.7556. AIME: 0.0042 / 0.0268 / 0.0932 / 0.0885 / 0.0784 / 0.1411 | 18.3 | No (4/12) | Table 2 (Pass@1 column; also in Table 3) |
| 7 | 2503.00031 Self-Calibration | Object Counting, MathQA, ARC-Challenge | Llama-3.1-8B-Instruct, Qwen2.5-7B-Instruct, R1-Distill-Qwen-1.5B | P1. Llama: 67.6 / 71.5 / 82.8. Qwen: 76.8 / 82.9 / 88.5. R1-1.5B: 61.2 / 89.9 / 58.2 | 76.8 | Yes (9/9) | Table 2 (Pass@1 row; repeated in Table 7) |
| 8 | 2609.02324 Text2Cypher | Text2Cypher subset (789 questions) | Gemma-2-9B, Qwen-2.5-7B | not reported (no single trace, no greedy run). Uniform 45-trace run, Gemma: "Exec. Success" 84.0, which seems to mean the query runs without error, not that it is correct. Execution-ROUGE-L is 0.2929. Qwen: no fixed-budget run without refinement | n/a | Cannot determine (no correctness accuracy) | Tables 3–4, Sec. 4.1 |
| 9 | 2608.24590 FSC | MATH500, AMC23, AIME24, AIME25, GPQA-D | Qwen2.5-3B / 7B / 14B-Instruct, Gemma-3-4B-it | **SC@40** (no P1). 3B: 74.6 / 52.5 / 16.7 / 3.3 / 30.3. 7B: 80.6 / 62.5 / 13.3 / 20.0 / 36.9. 14B: 81.6 / 70.0 / 20.0 / 23.3 / 46.2. G4B: 79.2 / 50.0 / 13.3 / 13.3 / 28.2 | 33.6 (SC@40) | No (8/20), SC-based, so robust | Table 1 |
| 10 | 2608.03961 Interpretable adaptive sampling | GSM8K, MATH, SciQ | Phi-3-mini-4k, Qwen2.5-1.5B-Instruct | P1 (Best-of-1). Phi: 0.601 / 0.451 / 0.153. Qwen: 0.355 / 0.249 / 0.365. (Table 3 "fixed N=1" for Phi gives 0.725 GSM8K and 0.457 MATH; the paper does not explain the gap) | 36.0 (36.0 with Table 3 values too) | No (1/6) | Tables 2, 6 (Table 3) |
| 11 | 2509.12886 LLM Already Knows | MMBench, ScienceQA, MathVista | Qwen2.5-VL-7B-Instruct | not reported. SC / BoN / Self-Refine results appear only in Figs. 3–4. Tables report difficulty-estimation metrics only | n/a | Cannot determine | Sec. 5.3, Figs. 3–4 |
| 12 | 2602.09438 ACTSC | MATH-500, AIME24, AIME25; GPQA-D and MMLU-Pro (7B only) | Qwen2.5-3B / 7B-Instruct, Gemma3-4B-it | **SC@40** (no P1). 3B: 61.80 / 11.20 / 6.67. 7B: 66.71 / 16.67 / 16.67, GPQA 36.67, MMLU-Pro 56.62. G4B: 67.64 / 13.33 / 16.67 | 16.7 (SC@40) | No (4/11), SC-based, so robust | Tables 1–2 |
| 13 | 2609.08650 DATPO (RL training) | MATH500, AIME26, AIME25, AIME24, AMC23 | Qwen2.5-3B-Base, Qwen3-4B-Base | Base-model avg@k (temperature 1; MATH500 avg@8, others avg@64). 2.5-3B: 26.3 / 0.4 / 0.2 / 1.0 / 10.0. Q3-4B: 39.9 / 1.7 / 1.1 / 2.8 / 17.2. (After DATPO: MATH500 63.5 / 76.4) | 2.25 | No (0/10) | Table 2 |

## Summary

- **Mostly solved: 3 of 13** (2408.13457 [SC@40 only], 2607.01612 [C3RL-trained model; the untrained Base splits 2/4], 2503.00031).
- **Not mostly solved: 6 of 13** (2509.22101 [F1], 2506.09338, 2608.24590, 2608.03961, 2602.09438, 2609.08650).
- **Cannot determine: 4 of 13** (2604.21018, 2504.16760, 2509.12886: accuracy appears only in figures; 2609.02324: no correctness accuracy).
- **Median of the per-paper medians** (9 papers with numbers): **36.0%**. It is 34.8% without the F1 paper (2509.22101). Using only true single-attempt numbers (5 papers: 2607.01612, 2506.09338, 2503.00031, 2608.03961, 2609.08650), it is also 36.0%.
- **Implication for the draft:** the evidence does **not** support "mostly evaluated on benchmarks their models largely solve." It is a minority pattern: 3 of the 9 papers with numbers. Several papers deliberately include hard sets (AIME, GPQA-D), where single-attempt or SC accuracy is well below 50%.

## PDF check (2026-11-03)

All accuracies used in Table D1 were checked against the arXiv PDFs. They match:
- 2503.00031 Table 2;
- 2506.09338 Tables 2–3;
- 2408.13457 Table 2;
- 2607.01612 Tables 1–3;
- 2608.24590 Table 1;
- 2602.09438 Tables 1–2;
- 2608.03961 Tables 2 and 6;
- 2609.08650 Table 2.

Changes made after the check:
- **Budget (u).** Each paper's own adaptive rule's mean budget is now used instead of the cap:
  - IAS: budget ratio × 64 (Table 2, calibrated PRM);
  - CAS: Avg. N (Table 3);
  - ACTSC: Sample column;
  - DSC: approximated as cost ratio × 40;
  - FSC: approximated as token ratio × 40.
- **DATPO (2609.08650).** It allocates on the MATH training set. The AIME numbers are evaluation sets, so they no longer stand in for the allocation regime. The regime now uses N=4, K_max=3, B_max=4 (≤ 16 rollouts; App. F) and base MATH500 avg@8 26.3 / 39.9.
