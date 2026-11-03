# Prior work: budget allocation across targets / items in molecule, protein and materials design (field slug `molecule`)

Written 2026-10-01 under CODEBOOK_v3. "[verified]" means I read the abstract or full text in this pass. "[unverified]" means the item comes from memory or a secondary summary.

## 1. Is there a classical or optimal allocation result?

Yes, in three adjacent sub-literatures. There is none for generative design across targets.

**(a) Free-energy estimation: Neyman allocation is known and used.**
- Allocating MD time across λ-windows or perturbation edges to minimize Var(ΔG) gives n_i ∝ σ_i. Equivalently, at the optimum the time derivative of each window's variance of the mean is equal.
- Clark et al. (JCTC 2024) implement this for absolute binding free energies [verified via PMC].
- Xu (2019) generalizes it to A/D/E-optimal allocation over networks of pairwise differences (DiffNet) [verified abstract].
- SAMTI (JPCB 2025) cites Neyman but implements P ∝ Var_i, i.e. proportional to variance rather than SD (Eq. 8) [verified in full text]. This is a clean E3 case.

**(b) Best-of search across arms: max-K-armed bandits.**
- Cicirello & Smith (2005) and Streeter & Smith (2006) give allocation of restarts/trials across stochastic searches to maximize the single best value [unverified details].
- "Materials Discovery using Max K-Armed Bandit" (arXiv 2212.08225) imports it to molecular MCTS design [verified abstract; author unverified]. It explicitly rejects mean-reward bandits for discovery.
- This is the regime-C best-of-k setting.

**(c) Markov-state-model adaptive sampling.**
- Seeding MD trajectories from states that contribute most to model uncertainty, rather than evenly, is a variance-reduction allocation across states.
- Singhal & Pande (2005, JCP, "Error analysis and efficient sampling in Markovian state models") [unverified].
- Hinrichs & Pande (2007, JCP) [unverified].
- Bowman, Ensign & Pande (2010, JCTC 6:787) [venue verified via search; content unverified].

**Also relevant: Bayesian optimization / ranking & selection** [unverified details].
- Knowledge gradient (Frazier, Powell, Dayanik 2008)
- OCBA (Chen et al. 2000)
- Multi-task BO choosing the task by information gain per cost (Swersky, Snoek, Adams 2013)

All give marginal value-of-information allocation. Molecular BO uses them within a task; I found none applied across design targets.

## 2. Does the field say level or dispersion/marginal gain decides? Does it warn against "harder gets more"?

- **FE estimation:** dispersion (σ) decides. Level plays no role. This is consistent with the principle.
- **Max-K-armed bandit:** argues for tail/marginal improvement of the best, not mean.
- **Library screening:**
  - Thompson-sampling over reagents (Klarich et al. 2024 [verified abstract]; Zhao et al. 2025 roulette-wheel variant [snippet only]) allocates by posterior mean of reagent scores, i.e. level.
  - BOBa (arXiv 2606.26657) [verified abstract] uses optimism-under-uncertainty across library partitions.
- **Generative design across targets:**
  - Benchmarks fix the oracle budget per task (PMO: 10k calls/task).
  - Protein binder pipelines report widely varying per-target success rates. BindCraft, from secondary sources [unverified], runs 300–3000 trajectories per target.
  - I found **no paper that allocates generation or oracle budget across targets** and compares it to uniform allocation.
- No paper in this field discusses "hopeless targets" in an allocation sense.

## 3. Key references

1. **Neyman, J. (1934).** JRSS 97:558–606.
   - Result: n_h ∝ σ_h.
   - Relation: identical (α = 1). SAMTI cites it as the basis (verified reference list).
2. **Clark, Robb, Cole, Michel (2024).** *Automated Adaptive Absolute Binding Free Energy Calculations.* JCTC 20(18):7806–7828 [verified].
   - Result: adaptive per-window time allocation to equalize the marginal variance decrease; equivalent results to non-adaptive, often faster equilibration.
   - Relation: identical (Neyman / water-filling).
3. **Lee, Jahanmahin, Pal, York (2025).** *SAMTI: Sampling Adaptive Thermodynamic Integration.* JPCB, doi 10.1021/acs.jpcb.5c05358 [verified].
   - Result: P_target ∝ Var_i, labelled Neyman.
   - Relation: misapplication (E3); proportional to variance instead of SD.
4. **Xu, H. (2019).** *Optimal measurement network of pairwise differences.* arXiv 1906.08599 (JCIM 2019, unverified) [abstract verified].
   - Result: A/D/E-optimal allocation of cost across RBFE edges.
   - Relation: generalization of Neyman to networks.
5. **Streeter & Smith (2006).** *An asymptotically optimal algorithm for the max k-armed bandit problem.* AAAI 2006 [unverified].
   - Result: allocate trials to maximize the expected maximum.
   - Relation: identical setting to regime-C best-of-k across items.
6. **Materials Discovery using Max K-Armed Bandit.** arXiv 2212.08225 (2022) [verified abstract].
   - Result: UCB on expected improvement of the best reward beats mean-reward bandits late in search.
   - Relation: analogous / special case.
7. **Klarich, Goldman, Kramer, Riley, Walters (2024).** *Thompson Sampling — An Efficient Method for Searching Ultralarge Synthesis on Demand Databases.* JCIM 64(4):1158–1171 [verified].
   - Result: finds >50% of the top-100 by evaluating 1%.
   - Relation: level-based counterpoint (E1, mechanical).
8. **Gao, Fu, Coley, Sun (2022).** *Sample Efficiency Matters (PMO).* NeurIPS D&B [unverified venue].
   - Result: fixed 10k oracle calls per task.
   - Relation: shows the uniform-per-target status quo.

## 4. Verdict

**The principle is split by sub-area.**
- **Free-energy and MD estimation:** it already knows Neyman allocation, and the α = 1 case adds **nothing new**. We can only point out misapplications like SAMTI's variance-proportional rule.
- **Best-of search:** max-K-armed bandits already embody "marginal improvement of the best, not mean". This is analogous and known.
- **Generative design across targets:** this is what the task asked about, and **the principle appears new**. That covers best-of-N per target, oracle budget across targets or design tasks, and test-time scaling for molecular or protein generation. No paper found allocates across targets, and benchmarks enforce uniform per-target budgets.

So our contribution here is to:
- frame cross-target budgets as water-filling on per-target best-of-k curves (k_i ∝ b_i^(1/(1+α)));
- show the target's difficulty level cancels;
- show that success-rate (binary hit) objectives fall in regime B, which needs a hopelessness discount.

Coverage caveat: the field yielded few on-topic papers (13 included, several low-confidence and coded from abstracts or snippets).
