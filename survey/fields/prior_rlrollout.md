# Prior work: per-prompt rollout allocation in RL fine-tuning of LLMs (field slug `rlrollout`)

Written 2026-10-01 under CODEBOOK_v3. "[verified]" means I read the abstract or full text in this pass. "[unverified]" means the item comes from memory or a secondary summary and needs checking before citation.

## 1. Is there a classical or optimal allocation result?

Yes, from two sources.

**(a) Curriculum RL: "learnability" and intermediate success.** Goal-RL and UED select tasks whose success probability is neither 0 nor 1, often scored as p(1-p).
- Goals of intermediate difficulty (GOID) were selected by success rate in [0.1, 0.9] (Florensa et al., 2018).
- "Sampling for learnability" (SFL) samples tasks by p(1-p) (Rutherford et al., 2024).
- LLM RL adopted SFL directly: LILO (arXiv 2502.12272) says it adapts "sampling for learnability" from the RL literature [verified].

**(b) Variance-optimal stochastic-gradient sampling (Neyman-type).**
- To minimize gradient-estimator variance under a sample budget, allocate n_i ∝ σ_i. This is Neyman (1934) stratified allocation.
- The SGD importance-sampling literature does the same: sample ∝ per-example gradient norm.
- LLM-RL papers derive and use this rule explicitly:
  - GVM-RAFT: n_i ∝ G_i / sqrt(p_i + reg) [verified].
  - CurES: n_i ∝ σ_i [verified].
  - DUET: "cost-weighted Neyman rule", n_q ∝ σ_q / sqrt(L_q) [verified].

## 2. Does the field say level or dispersion/marginal gain decides? Does it warn against "harder gets more" or hopeless items?

Mostly yes. The dominant view in LLM RL is that prompts with p ≈ 0 and p ≈ 1 carry no GRPO signal, because the group-relative advantage is identically zero. Intermediate p maximizes signal.
- Online Difficulty Filtering proves expected policy improvement is lower-bounded by Var of success p(1-p). It concludes intermediate difficulty "maximizes learning efficiency" [verified, 2504.03380].
- DAPO's dynamic sampling filters groups with accuracy 0 or 1 [verified from abstract and known algorithm; the filter detail is from the paper body, unverified in this pass].
- VIGOR, Pilot-Commit, CERO, SARA, KGPS, PCL, MoPPS, Prompt Replay and PACED-RL all target p ≈ 0.5 or high group variance. They discount both easy and hopeless prompts [verified abstracts].
- Explicit marginal / diminishing-returns formulations:
  - CERO: concave saturating utility from expected Bernoulli variance; online dual allocation with regret bound [verified abstract].
  - XRPO: allocates by the expected reduction of the CI half-width [verified].
  - Knapsack RL (arXiv 2509.25849) and VIP (arXiv 2602.01601) are already in the 221-paper survey.

There is a counter-current that "harder gets more", with no discount for hopeless prompts:
- Reinforce-Ada: budget ∝ 1/sqrt(p̂), with a prior that keeps zero-success prompts alive [verified].
- AR3PO: sample until the first success, up to a cap [verified].
- DARS: extra rollouts scale with 1 − acc [verified].
- Kimi k1.5: prioritized sampling ∝ 1 − s_i [verified].
- "Hard Examples Are All You Need" (2508.14094) [verified abstract].

These papers justify it as recovering signal on hard prompts. That is exactly the regime-B question of whether u·p is large enough. None of them derives the p = 1/(k+1) peak or a hopelessness discount; GVM-RAFT's regularizer is an ad-hoc exception.

## 3. Key references

1. **Florensa, Held, Geng, Abbeel (2018).** *Automatic Goal Generation for Reinforcement Learning Agents.* ICML 2018 [unverified details].
   - Result: train on goals with intermediate success (GOID).
   - Relation: analogous to the NON-MONO regime-B rule.
2. **Rutherford et al. (2024).** *No Regrets: Investigating and Improving Regret Approximations for Curriculum Discovery.* NeurIPS 2024 [unverified venue; the SFL attribution is verified via LILO's abstract wording].
   - Result: sample levels by learnability p(1-p).
   - Relation: special case. It is the k = 1 learning-signal version of the regime-B marginal.
3. **Neyman, J. (1934).** *On the two different aspects of the representative method.* JRSS 97:558–606.
   - Result: n_h ∝ N_h σ_h.
   - Relation: identical to the codebook's α = 1 rule. Used explicitly by DUET and CurES.
4. **Razin et al. (2024).** *Vanishing Gradients in Reinforcement Finetuning of Language Models.* ICLR 2024 [unverified venue].
   - Result: the expected gradient vanishes when the reward std of an input is small.
   - Relation: analogous; gives the mechanism for discounting p ∈ {0, 1}.
5. **Bae et al. (2025).** *Online Difficulty Filtering for Reasoning Oriented RL.* arXiv 2504.03380 [verified].
   - Result: the policy-improvement lower bound is ∝ variance of task success; balanced filtering is optimal for that bound.
   - Relation: special case (LEVEL NON-MONO).
6. **Yao et al. (2025).** *Optimizing Chain-of-Thought Reasoners via Gradient Variance Minimization (GVM-RAFT).* arXiv 2505.02391 [verified; authors unverified].
   - Result: n_i ∝ G_i / sqrt(p_i + α/p_i^(β−1)).
   - Relation: Neyman-type. The regularizer is an ad-hoc hopelessness discount.
7. **CERO (2026).** *Cross-Epoch Adaptive Rollout Optimization for RL Post-Training.* arXiv 2606.05606 [verified abstract].
   - Result: concave per-prompt utility from Beta-posterior Bernoulli variance; online water-filling via the dual.
   - Relation: closest to identical (marginal allocation).
8. **DAPO (Yu et al., 2025).** arXiv 2503.14476 [verified abstract].
   - Result: dynamic sampling drops groups with accuracy 0 or 1.
   - Relation: special case (hard threshold).

## 4. Verdict

**Little is new for this field on the qualitative point.** LLM-RL already knows that intermediate-p prompts maximize signal, and that zero-variance (hopeless or solved) prompts should get nothing. It also already uses Neyman (DUET, CurES) and marginal or water-filling allocators (CERO, Knapsack RL, VIP).

What our paper can add:
1. **A unified criterion that depends on k.** The marginal value of the j-th rollout under binary reward depends on how many rollouts the prompt already has. Most papers use a k-free score p(1-p).
2. **An explanation of when MONO-UP rules work, with a correction for when they don't.** Reinforce-Ada, AR3PO, DARS, Kimi k1.5 and "Hard Examples" allocate more to low-p prompts with no hopelessness discount (5 E2 flags out of 27 included). Our regime-B result says when this helps (u·p large) and when it wastes budget (u·p small).
3. **A charging audit.** DAPO-style oversampling and step-matched comparisons leave signal cost uncharged (3 E5 flags).

The core claim, that "difficulty level is the wrong signal; dispersion or marginal gain decides", is **not new** for RL rollouts.
