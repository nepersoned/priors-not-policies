# Priors, not policies: test-time compute allocation

Code, results, newly generated samples and survey coding for the paper "Give Up to Get More: Priors, Not Policies, Govern Test-Time Compute Allocation" (Jinhyung Bae).

The paper studies how to divide a budget of repeated LLM attempts across a fixed set of inputs. It makes three points:
- "Harder gets more" allocation recovers almost none of the attainable gain on hard workloads.
- With a verifier, the gain over round-robin comes from a prior built from past runs on the same inputs, not from the choice of policy.
- The gain depends on the prior's quality and on the verifier's false acceptance rate.

## Setup

The scripts expect this folder to be named `paper4` and to be run from its parent directory, for example:

```bash
git clone https://github.com/nepersoned/priors-not-policies paper4
python paper4/e2/e2_cost.py
```

Python 3.11+ with `numpy`, `scipy`, `pandas`, `pyarrow` and `matplotlib` is enough for every replay. Generating new samples (`colab/`) additionally needs `vllm` and a GPU.

## Data

The public stored samples are not redistributed here. Put them in `paper4/data_ext/`:

| file(s) | source |
|---|---|
| `mb_<task>_<model>.parquet` | Large Language Monkeys, `ScalingIntelligence/monkey_business` on Hugging Face (one parquet per config) |
| `weaver_*.parquet` | Weaver, `hazyresearch/*_with_Llama_3.1_*_Instruct_v1` and the GSM8K GPT-4o-mini release on Hugging Face |
| `prm800k_scored-test-samples.jsonl` | PRM800K (github.com/openai/prm800k); `domains/prm800k.py` builds `prm800k_compact.npz` from it |
| `hpob-data.zip` | HPO-B (github.com/releaunifreiburg/HPO-B), used only in Appendix A |

`data_ext/download_expansion.ps1` downloads the Weaver and the extra monkey_business configs.

## Where each result comes from

| paper item | script | result file |
|---|---|---|
| Table 1, Figure 2 (static rules vs. oracle) | `e2/e2_cost.py` (`hard` for the hard set), `e2/e2_figure.py` | `e2/e2_cost.json`, `e2/e2_cost_hard.json` |
| §2 left-branch diagnostic, Appendix E | `e2/diagnostic_check.py` | `e2/diagnostic_points.json` |
| Table 2 (history prior, online) | `e2/e2_online_v2.py` | `e2/e2_online_v2.json`, `e2/e2_online_v2_weaver.json` |
| Table 3 (cheap priors) | `e2/e2_text_prior.py`, `e2/e2_llm_prior.py` (features from `e2/colab/`), `e2/e2_gemini_prior.py`, `e2/gemini_rank/`, `e2/claude_rank/`, `e2/fewshot_rank/`; proxy samplers via `e2/e2_online_v2.py` | `e2/e2_text_prior.json`, `e2/e2_llm_prior.json`, `e2/e2_gemini_prior.json`, `e2/rank_scores_*.json`, `e2/e2_online_v2_pythiaproxy.json` |
| Policy comparison (TS, UCB, myopic) | `e2/e2_bandits.py` | `e2/e2_bandits.json` |
| Table 4 (controlled prior degradation) | `e2/robustness_v4.py` | `e2/robust_F.json` (other variants: `robust_A`–`E`) |
| Table 5 (verifier errors, length-charged cost) | `e2/e2_noisy_verifier.py`, `e2/e2_token_cost.py` | `e2/e2_noisy_verifier.json`, `e2/e2_token_cost.json` |
| Table 6 (stored reward models) | `e2/e2_real_verifier_screen.py`, `e2/e2_real_verifier_run.py` | `e2/e2_real_verifier_screen.json`, `e2/e2_real_verifier_run_u2.json`, `..._u16.json` |
| Tables 7–8 (verifier-error model) | `e2/noisy_theory.py`, `e2/noisy_theory2.py` | `e2/noisy_theory.json`, `e2/noisy_theory2.json` |
| Tables 9–10 (new Qwen2.5 samples) | `colab/gen_live.py`, `colab/gen_live_7b.py` (generation); `e2/e2_live.py`, `e2/e2_live_temper.py` (replay) | `colab/live_samples_small.json`, `colab/live_samples_7b.json`, `e2/e2_live.json`, `e2/e2_live_temper.json` |
| Figures | `figures/make_figures_v3.py`, `figures/make_flowchart.py` | `figures/*.png` |
| Appendix A (continuous objectives) | `domains/` | `domains/atkinson_check.json`, `domains/robustness.json` |
| Appendix B (correction to Bae 2026a) | code in github.com/nepersoned/best-of-k-allocation | `nco/GATE1_RESULTS.md` |
| §3, Appendix D (survey) | `survey/` (below) | |
| Appendix C (proof) | | `draft/prop1.md` |

Shared allocation code (exact coverage curves, greedy oracle) is in `common/alloc.py`.

## Survey

| file | content |
|---|---|
| `survey/big/CODEBOOK_v2.md` | codebook for the 221 LLM papers |
| `survey/big/candidates.jsonl` | the 1,269 records kept by the recall filter (ids and titles; abstracts removed) |
| `survey/big/coded/` | first-pass coding of the included papers |
| `survey/big/e2_strict.jsonl` | strict full-text re-judgment of the candidates |
| `survey/big/human_check_E2*_results.md` | condition-level full-text checks of the 19 papers (LLM-assisted, author-reviewed) |
| `survey/big/validation_*.jsonl`, `agreement.py` | double-coding of a random 50 |
| `survey/big/hgm_benchmark_accuracy.md` | accuracies and budgets of the 13 confirmed papers (Table D1), checked against their PDFs |
| `survey/fields/` | the twelve-field map: codebook v3, coded papers and per-field notes |
| `draft/appendix_D_E2_papers.md` | the list of confirmed and borderline papers |

The first pass of the survey coding was done by LLM agents under a fixed codebook. Later checks were LLM-assisted and reviewed by the author, as described in the paper.

## License

MIT (see `LICENSE`). Third-party datasets keep their own licenses.
