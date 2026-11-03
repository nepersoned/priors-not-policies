# Prior work: robotics and embodied agents (field slug `robotics`)

Survey group D, 2026-10-01. Codebook v3. Coded papers: `coded_robotics.jsonl` (30 screened, 26 included).

**Verification markers.**
- [V]: I read the claim in the paper's text (PDF or abstract) during this survey.
- [S]: the claim comes only from a search snippet.
- [U]: the claim is from memory and unverified.

**Scope note.** The literature on "allocating a retry budget across tasks" is thin. Several searches (retry policies, re-planning budgets, when to give up) turned up only fixed per-task retry caps. I found no paper that allocates a shared retry budget across tasks and compares it with uniform retries. The coded set therefore covers five groups:
1. Planning-time metareasoning.
2. Restarts.
3. Training curricula: episodes across goals or tasks.
4. Data collection and evaluation budgets across tasks or factors.
5. Human-help budgets and VLA test-time compute.

## 1. Is there a classical or optimal allocation result?

**Restarts (regime H).**
- Luby, Sinclair & Zuckerman (1993) give the optimal fixed cutoff for a known run-time distribution (RTD) and a universal schedule for an unknown one [U]. This concerns one instance.
- Wedge & Branicky (2008) show heavy-tailed RRT runtimes that restarts can exploit [S].
- "Faster Motion Planning via Restarts" (arXiv 2506.19016, 2025) adds new restart strategies with optimality proofs for PRM/RRT [V, abstract].
- Relation: analogous (regime H). Allocation is across runs of one instance, not across items.

**Anytime-planning metareasoning.**
- Hansen & Zilberstein (AIJ 2001) monitor anytime algorithms with performance profiles and dynamic programming [U].
- Sung, Kaelbling & Lozano-Pérez (IROS 2021) learn when to quit an anytime motion planner. They beat "the fixed-time strategy and the fixed-quality strategy" [V]. Stopping when predicted improvement no longer pays for the time cost is the Lagrangian form of marginal allocation across instances.
- "Effort Allocation for Deadline-Aware TAMP" (arXiv 2410.05828) allocates computation across plan skeletons to maximise the probability of an executable plan before a deadline [V]. It is an MDP over learned performance profiles, NP-hard by reduction from knapsack [V], and it beats Round Robin [V].
- Relation: identical in spirit to regime-B/H marginal allocation.

**Curricula over goals and tasks with binary success (regime B for training).**
- Goal GAN (ICML 2018) trains on goals of intermediate difficulty, "always at the appropriate level of difficulty" [V, abstract]. Reverse Curriculum (CoRL 2017) does the same with start states [V].
- VDS (NeurIPS 2020) samples goals "neither too hard nor too easy" [V].
- PAIRED (NeurIPS 2020) warns that minimax adversarial (hardest-first) generation yields environments "that are often unsolvable" [V]. Its regret objective removes the value of hopeless environments.
- Learning-progress teachers move effort toward items whose learning curve rises fastest. Examples:
  - Oudeyer et al. 2007 [U];
  - TSCL (2017; TNNLS 2019): "the slope of the learning curve is highest" [V];
  - CURIOUS (ICML 2019): "some goals might prove easy and some impossible" [V];
  - ALP-GMM (CoRL 2019).
- The Portelas et al. (IJCAI 2020) survey on automatic curriculum learning summarises this [U].
- Relation: **closely analogous to the regime-B principle.** The NON-MONO, intermediate-difficulty rule and the explicit discount of impossible goals are exactly the "do not spend on hopeless items, do not give everything to the hardest" message. It is reached empirically, through learning progress, not from a p(1−p)^k derivation.

**Data collection and evaluation (regime C).**
- "Guiding Data Collection via Factored Scaling Curves" (FSC, arXiv 2505.07728, 2025) fits a power law per environment factor, 1 − a(n+|D|)^b. It allocates demonstrations by "the marginal return of collecting more demonstrations" [V].
  - It beats Equal allocation, and a Greedy baseline that gives the whole budget "to the single factor with the lowest success rate" [V].
  - This is regime-C water-filling vs a LEVEL, harder-gets-more rule, in one paper.
- Anwar et al. (CoRL 2025) allocate evaluation trials across (policy, task) pairs by cost-aware expected information gain, against random baselines [V].
- AMF (ICML 2025) allocates demonstrations across tasks by information gain about the expert policy, against uniform sampling [V].

**Human-help budgets.**
- Fleet-DAgger (CoRL 2022) allocates limited human supervisors across robots by priority: constraint violation, then uncertainty, then risk [V].
- ThriftyDAgger (ICRA 2022) [V, abstract] and KnowNo (CoRL 2023) [V, abstract] send help to novel, risky or uncertain states.
- Coded N/A. Help is a near-deterministic fix, not a repeated attempt, so harder-gets-more is appropriate there.

## 2. Level vs dispersion/marginal; warnings about "harder gets more" and hopeless items

- **Curricula already warn against both errors.** PAIRED warns against hardest-first, Goal GAN and VDS use intermediate difficulty, and CURIOUS and ALP-GMM drop "impossible" and "unlearnable" items. The governing signal is marginal (learning progress), not level.
- **FSC explicitly compares marginal returns against a level rule.** Marginal allocation on power-law curves beats a level-based rule (lowest success first).
- **The new VLA test-time-compute papers use level signals.** VLA-ATTC (arXiv 2605.01194, 2026) switches to best-of-16 deliberation at states above an uncertainty percentile (the 80th by default) [V]. Its threshold percentile is ablated on benchmark success [V], which is a possible E4.
  - Per-state action error vs number of samples follows an "exponentiated power law" (RoboMonkey, arXiv 2506.17811 [V, abstract]). That makes this regime C, where the spread of b_i, not the uncertainty level, should govern allocation. Hence the E1 flag.
  - I found no robotics test-time-scaling paper that allocates samples by estimated marginal gain.

## 3. Key references

1. **Florensa, C., Held, D., Geng, X., Abbeel, P.** "Automatic Goal Generation for Reinforcement Learning Agents." ICML 2018 (arXiv:1705.06366).
   - Result: train on goals of intermediate difficulty (success within [Rmin, Rmax]). [V abstract; band definition U]
   - Relation: **analogous** (the NON-MONO regime-B rule for training).
2. **Dennis, M., Jaques, N., Vinitsky, E., Bayen, A., Russell, S., Critch, A., Levine, S.** "Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design" (PAIRED). NeurIPS 2020 (arXiv:2012.02096).
   - Result: regret-based environment design; minimax adversaries yield unsolvable environments. [V abstract; author list U]
   - Relation: **analogous** (an explicit warning against hopeless items).
3. **Matiisen, T., Oliver, A., Cohen, T., Schulman, J.** "Teacher-Student Curriculum Learning." IEEE TNNLS 2019 (arXiv:1707.00183).
   - Result: sample tasks by the slope of the learning curve, which beats uniform sampling. [V abstract; author list U]
   - Relation: **analogous** (marginal-gain allocation).
4. **Sung, Y., Kaelbling, L. P., Lozano-Pérez, T.** "Learning When to Quit: Meta-Reasoning for Motion Planning." IROS 2021 (arXiv:2103.04374).
   - Result: learned per-instance stopping beats fixed-time and fixed-quality rules. [V]
   - Relation: **special case** (marginal stopping, regime C with a time cost).
5. **"Effort Allocation for Deadline-Aware Task and Motion Planning: A Metareasoning Approach."** arXiv:2410.05828, 2024 [authors not recorded].
   - Result: an MDP or knapsack allocation of planning effort across plan skeletons, which beats round robin. [V]
   - Relation: **identical in form** (regime-B/H marginal allocation across options).
6. **"Guiding Data Collection via Factored Scaling Curves."** arXiv:2505.07728, 2025 [authors not recorded].
   - Result: per-factor power-law curves with marginal-return allocation, which beats Equal and lowest-success-first allocation. [V]
   - Relation: **identical** (regime-C water-filling).
7. **Luby, M., Sinclair, A., Zuckerman, D.** "Optimal Speedup of Las Vegas Algorithms." Information Processing Letters, 1993. [U]
   - Result: optimal and universal restart schedules.
   - Relation: **analogous** (regime H, within one instance).
8. **Kwok, J. et al.** "RoboMonkey: Scaling Test-Time Sampling and Verification for VLA Models." arXiv:2506.17811, 2025. [title V; authors U]
   - Result: action error vs samples follows an exponentiated power law.
   - Relation: **curve-shape evidence** for regime C at the state level. It uses no adaptive allocation.

## 4. Verdict

**Curricula and data collection: nothing new.**
- Curriculum learning already knows the principle empirically: intermediate difficulty, learning progress, and discounting impossible goals. PAIRED explicitly warns against harder-gets-more.
- Data collection has a direct regime-C water-filling instance (FSC), which beats a level rule.
- Planning-time metareasoning (Sung 2021; deadline-aware TAMP 2024) does marginal or optimal allocation.

**Test-time sampling and retries: something to add.**
1. Adaptive test-time compute for VLAs (VLA-ATTC) allocates by uncertainty level, harder first. Yet the per-state curves are power-law (RoboMonkey). Our regime-C result (k_i ∝ b_i^(1/(1+α)); spread, not level) and the E4 caution are new to this subfield.
2. I found no theory or empirical comparison for allocating a shared retry budget across tasks. The regime-B analysis (marginal value p(1−p)^k; at small u·p favour solvable tasks) would be a novel contribution there.

Evidence for gap 2 is absence of evidence from searching. It is not a proof that no such work exists.
