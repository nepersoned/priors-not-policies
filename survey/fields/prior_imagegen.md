# Prior work: per-prompt sample / denoising-compute allocation in image and video generation (field slug `imagegen`)

Written 2026-10-01 under CODEBOOK_v3. "[verified]" means I read the abstract or full text in this pass. "[unverified]" means the item comes from memory or a secondary summary.

## 1. Is there a classical or optimal allocation result?

**Not within the field.** Image/video inference-time scaling mostly fixes N per prompt:
- best-of-N over noise seeds;
- search over noise;
- Ma et al. 2025, arXiv 2501.09732 [verified abstract].

The relevant classical results are imported from elsewhere:
- **Order statistics of best-of-N.** Expected max of N draws from a continuous reward distribution. Its gain grows with the spread of the per-prompt reward distribution, not with its level. This is the regime-C argument.
- **Optimal stopping.** Weitzman's Pandora's box (1979) gives reservation-value stopping per item. Kalayci et al. (arXiv 2510.01394, already in the 221-paper survey) adapt it to best-of-N for LLMs.
- **LLM compute-optimal allocation:**
  - Snell et al. 2024 (arXiv 2408.03314) allocate by difficulty bin.
  - Damani et al. 2024 (arXiv 2410.04707) allocate by predicted marginal reward gain of best-of-k.
  - Both are already in the 221-paper survey.
  - Damani et al. is the closest identical analog: marginal-gain allocation of samples with a continuous reward.

## 2. Does the field say level or dispersion/marginal gain decides? Does it warn against "harder gets more"?

**Inference-time methods allocate by level or threshold, always harder-gets-more.**
- DFS search (arXiv 2505.23614) [verified]: harder prompts get more compute via verifier-threshold backtracking. Section 5.2 presents this as a virtue.
- RAISE (arXiv 2603.00483) [verified]: keeps refining until the checklist is satisfied, capped at K_max.
- ADE-CoT (arXiv 2603.00141) [verified]: N_a = N_min + ⌈(N−N_min)(1−S/S_max)^γ⌉. The budget grows with the first-sample score deficit, which is a continuous level signal.
- Video early-failure intervention (arXiv 2603.14320) [verified abstract]: spends compute only on predicted failures.

No inference-time image/video paper found uses dispersion or marginal gain. None warns against spending on hopeless prompts.

**RL fine-tuning of diffusion/flow models imports LLM-RL heuristics:**
- AdaGRPO (arXiv 2606.06828) [verified]: picks prompts whose reward is closest to an EMA capability anchor (level, NON-MONO). It reports that both easiest and hardest prompts underperform random selection.
- CGPO (arXiv 2605.17807, CVPR 2026) [verified]: sampling probability linear in group reward variance.
- SuperFlow (arXiv 2512.17951) [verified]: gives *more* rollouts to *low*-uncertainty prompts, the inverse of Neyman, to stabilize group normalization.

**Denoising-step and capacity allocation is cost-at-target (regime N/A):**
- AdaDiff (AAAI 2025) [verified via AAAI listing]
- AdaptiveDiffusion (NeurIPS 2024)
- APTP
- DiffServe, HADIS

## 3. Key references

1. **Ma et al. (2025).** *Inference-Time Scaling for Diffusion Models beyond Scaling Denoising Steps.* arXiv 2501.09732 (CVPR 2025, unverified).
   - Result: search over noises with verifiers scales quality; the budget is uniform per prompt.
   - Relation: baseline. Shows per-prompt best-of-N curves exist but are not exploited across prompts.
2. **Damani, Shenfeld, Peng, Bobu, Andreas (2024).** *Learning How Hard to Think: Input-Adaptive Allocation of LM Computation.* arXiv 2410.04707 [in 221 set; authors unverified].
   - Result: predict the marginal reward of more samples per input; allocate greedily.
   - Relation: identical principle, but in LLMs.
3. **Snell et al. (2024).** arXiv 2408.03314 [in 221 set].
   - Result: compute-optimal allocation by difficulty bin.
   - Relation: analogous (level-based).
4. **Weitzman (1979).** *Optimal Search for the Best Alternative.* Econometrica 47(3).
   - Result: reservation-value index for sequential search.
   - Relation: analogous (per-item stopping; marginal).
5. **Kalayci et al. (2025).** *Optimal Stopping vs Best-of-N for Inference Time Optimization.* arXiv 2510.01394 [in 221 set].
   - Result: Pandora's-box stopping for best-of-N needs 15–35% fewer generations.
   - Relation: analogous. LLM only, though the method is modality-agnostic.
6. **Li, Ma et al. (2025).** *Inference-time Scaling of Diffusion Models through Classical Search.* arXiv 2505.23614 [verified; author list unverified].
   - Result: threshold DFS gives more compute to harder prompts.
   - Relation: level/threshold counter-example (E2).
7. **ADE-CoT (2026).** arXiv 2603.00141 [verified].
   - Result: budget ∝ (1 − S/S_max)^γ.
   - Relation: level-based counter-example in regime C (E1).

## 4. Verdict

**The principle is new for image/video generation.** No paper found allocates best-of-N samples across prompts by dispersion or marginal gain of a continuous reward. All adaptive inference methods use level or threshold "harder gets more" rules (E1/E2). The closest methods with the right principle are LLM papers (Damani et al.; Kalayci et al.).

Our contributions here:
- **The water-filling rule (k_i ∝ b_i^(1/(1+α))).** Under it, difficulty level cancels and per-prompt reward spread drives the gain.
- **A diagnosis of SuperFlow's inverse-SD rule and CGPO's variance rule** relative to the regime optimum (E3).

Caveat: the field is small. 14 included papers, half of them N/A step/capacity routing.
