# Prior work: AutoML / HPO budget allocation across tasks (field slug `automl`)

Written 2026-10-01 (group B). Items marked **[unverified]** were not checked against the paper text in this session. They come from memory or from a search snippet.

## 1. Is there a classical or optimal allocation result?

There is no single closed-form "optimal allocation across tasks" result in AutoML comparable to Neyman or OCBA. The field has three separate traditions.

1. **Within-task allocation across configurations, with a selection objective.**
   - Examples: successive halving and Hyperband (Jamieson & Talwalkar 2016; Li et al. 2018), BOHB, ASHA.
   - Budget goes to the configurations that currently look best (LEVEL, MONO-DOWN). This is correct for a max/best-arm objective.
   - These methods are not our setting: the objective is the best single item, not a sum over items.
2. **Across-task (multi-tenant / contextual) allocation with a sum-of-regret objective.** This is our setting, regime C (best-of-k of a continuous score).
   - Ease.ml (Li et al., PVLDB 2018), GP-EI multi-device multi-tenant (2018/19) and Offline Contextual BO (Char et al., NeurIPS 2019) all pick the next task by **estimated marginal improvement**: UCB minus best-so-far, EI per unit cost, or Thompson-sampled improvement.
   - Ease.ml explicitly says that mean quality (the level) is not comparable across easy and hard datasets. So in practice the field already uses MARGINAL rather than LEVEL here.
3. **Learning-curve modelling.**
   - Examples: Domhan et al. 2015 (parametric curve ensemble that includes power-law forms) **[unverified detail]**, Freeze-Thaw BO (exponential-decay kernel), rising bandits.
   - So the field models the shape of improvement curves, but uses it for early stopping within a task, not for closed-form allocation across tasks.
4. **Heavy-tailed runtime (regime H).**
   - Algorithm configuration with capped runs: Structured Procrastination, LeapsAndBounds, SPC.
   - Portfolio time allocation: GambleTA (Gagliolo & Schmidhuber 2011).
   - These build on restart theory (Luby, Sinclair & Zuckerman 1993) **[unverified as cited by each paper]**.

## 2. Level versus spread/marginal, and warnings about "harder gets more"

- **Multi-tenant HPO / contextual BO: MARGINAL, with a warning about raw difficulty.**
  - Ease.ml, Sec. 4: "we choose to omit the mean quality in the UCB criterion". The level is dropped because it confounds easy and hard datasets.
  - Char et al. 2019 warn that poor modelling of task difficulty can make active task selection counterproductive.
- **Meta-learning and multi-task training: often "harder gets more" (LEVEL, MONO-UP), with no marginal discount.**
  - Sharma et al. (arXiv 1702.06053): "sampling the harder tasks more than the easier ones".
  - Liu et al. (ECCV 2020): "selects difficult tasks according to class-pair potentials".
- **Learning-progress (marginal) curricula exist as a counter-tradition.** Graves et al. (ICML 2017) allocate by the rate of improvement.
- **Learned schedulers** move away from pure difficulty. Yao et al. (NeurIPS 2021, ATS) and Wang et al. (IJCV 2024) argue there is "no universal task sampling strategy".
- I found no AutoML paper that states the water-filling rule k_i ∝ b_i^{1/(1+α)}, or that says the level cancels and spread of b_i drives the gain. **[absence claim — based on this search only]**

## 3. Key references

| # | Citation | Result (one line) | Relation to our principle |
|---|---|---|---|
| 1 | L. Li, K. Jamieson, G. DeSalvo, A. Rostamizadeh, A. Talwalkar. "Hyperband: A Novel Bandit-Based Approach to Hyperparameter Optimization." JMLR 18, 2018 (arXiv 1603.06560). | Geometric successive-halving brackets give budget to configurations that currently look best. | Analogous only: within-task, max objective. |
| 2 | T. Li, J. Zhong, J. Liu, W. Wu, C. Zhang. "Ease.ml: Towards Multi-tenant Resource Sharing for Machine Learning Workloads." PVLDB 11(5), 2018 (arXiv 1708.07308). | Picks the user with the largest gap between UCB and best-so-far accuracy. Drops mean quality. Has a regret bound and beats round-robin by up to 9.8x. | Special case: an online MARGINAL rule for regime C across tasks, without the closed form. |
| 3 | I. Char, Y. Chung, W. Neiswanger, K. Kandasamy, A. O. Nelson, M. Boyer, E. Kolemen, J. Schneider. "Offline Contextual Bayesian Optimization." NeurIPS 2019. | Multi-task Thompson sampling picks "the task in which the most improvement can be made". Beats uniform task selection. | Special case (MARGINAL, regime C). Explicitly discusses task difficulty. |
| 4 | M. Pearce, J. Branke. "Continuous multi-task Bayesian optimisation with correlation." EJOR 270, 2018. | REVI, a knowledge-gradient extension, chooses both task and parameter. Beats random allocation. | Special case (value of information = marginal). |
| 5 | K. Swersky, J. Snoek, R. P. Adams. "Multi-task Bayesian optimization." NIPS 2013. | Cost-sensitive entropy search chooses which dataset to query for the most information per unit cost. | Analogous only: single target objective. |
| 6 | A. Graves, M. G. Bellemare, J. Menick, R. Munos, K. Kavukcuoglu. "Automated Curriculum Learning for Neural Networks." ICML 2017. | A bandit over tasks rewarded by learning progress. | Analogous: an empirical marginal-gain rule. |
| 7 | S. Sharma, A. Jha, P. Hegde, B. Ravindran. "Learning to Multi-Task by Active Sampling." arXiv 1702.06053 (2017; ICLR 2018 **[venue unverified]**). | Samples harder tasks (larger gap to target score) more often. | Counter-example: LEVEL MONO-UP (E1). |
| 8 | G. Weisz, A. György, C. Szepesvári. "LeapsAndBounds: A Method for Approximately Optimal Algorithm Configuration." ICML 2018. | Doubling time caps over configurations and instances, with near-optimal total work. | Regime H. Analogous (restart/cap theory). |

## 4. Verdict

AutoML **partly** knows the principle.

**Already known:**
- In multi-tenant / contextual HPO (regime C, best-of-k regret summed over tasks), the leading methods already allocate by estimated marginal improvement and outperform round-robin.
- Ease.ml explicitly rejects level as a cross-task signal.

**What our paper would add for this field:**
1. **A closed-form, model-light rule.** If each task's best-so-far curve is fitted as a_i + b_i k^(−α), allocate k_i ∝ b_i^(1/(1+α)). The codebook's claim that the level cancels and spread governs the gain is not stated anywhere we found. Current methods get the effect only implicitly, through GP posteriors.
2. **A diagnosis of the meta-learning and multi-task task-sampling literature.** Sharma 2018 and Liu 2020 use the "harder gets more" LEVEL heuristic (E1). Our principle predicts this is wrong under regime C unless difficulty happens to correlate with b_i.
3. **Explicit treatment of signal cost and separation.** Per-task curve fitting needs some budget, and most papers do not report this cost.

Regime B is largely irrelevant in this field. Regime H (algorithm configuration) has its own mature theory, from Luby-style restarts to SP and LeapsAndBounds; we add nothing there.

So this is **not "nothing new"**: the field has the marginal idea, but not the closed form or the level-versus-spread diagnosis. The novelty is moderate and lies mainly in theory and diagnosis, not in a new algorithm.
