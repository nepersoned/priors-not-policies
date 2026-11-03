# Prior work: neural / classical combinatorial optimization (field slug `nco`)

Survey group A, 2026-10-01. Codebook v3. Coded papers: `coded_nco.jsonl` (24 screened, 6 included).

**Verification markers.** [V] means I read the claim in the paper's text during this survey. [S] means I saw it only in a search-engine snippet or a secondary description. [U] means it comes from memory and is unverified, so check it before citing. Page numbers are given only where verified.

## 1. Is there a classical or optimal allocation result?

The answer is yes for allocating restarts across heuristics or runs on **one** problem instance. For allocating a budget across **instances**, I found nothing in the NCO or metaheuristic literature apart from the requester's own preprints.

- **Max k-armed bandit (multi-start allocation).** Trials are split across k randomized heuristics to maximize the expected *best single sample*. Under a Gumbel (extreme-value) model, the optimal policy gives the observed-best arm double-exponentially more trials than the others. Later work gives distribution-free and PAC algorithms. The objective is a **single global max**, so the optimum concentrates the budget on one arm. This is an identification problem, not a split of a budget across items whose outcomes add up.
- **Multi-start local search with a convergence-rate model** (György & Kocsis 2011). Steps are split across parallel local-search runs, using an assumed convergence-rate curve g(n) with an unknown constant. In effect this gives more budget to runs whose *optimistic potential improvement* is largest. This is the closest classical analogue of curve-shape-aware ("marginal") allocation. It is still within one objective with a max criterion.
- **Optimal stratified allocation (Neyman 1934) and OCBA (Chen et al. 2000).** These are not used in NCO. OCBA appears only in simulation-optimization (ranking and selection over designs). [U for exact OCBA citation]

## 2. Difficulty level vs dispersion/marginal; warnings about "harder gets more"

- In NCO proper, every test-time method I screened uses a **uniform per-instance budget**: POMO starts and augmentations, EAS, SGBS, Poppy, COMPASS and MEMENTO. Sampling budget is a single global hyperparameter.
- The one included NCO paper that varies compute per instance is Gao et al. (ICML 2025). Its signal is **selector uncertainty**, not difficulty: more solvers go to low-confidence instances. It is neither LEVEL-based nor explicitly marginal. The authors leave runtime-aware allocation as future work. [V]
- The max-k-armed-bandit literature contains a dispersion warning. David & Shimkin show that uniform/random arm choice can beat adaptive allocation "when the maximal rewards of the arms happen to be similar" [V]. This is the max-objective analogue of "spread, not level, governs the gain".
- I found no NCO paper that argues "harder gets more" explicitly. I also found none that warns against it. The question has not been posed in NCO, outside the requester's own work.

## 3. Key references

| # | Reference | One-line result | Relation to our principle |
|---|---|---|---|
| 1 | Cicirello, V. A. & Smith, S. F. (2005). *The Max K-Armed Bandit: A New Model of Exploration Applied to Search Heuristic Selection.* AAAI-05. [V] | Splitting restarts among heuristics to maximize the expected best sample: the optimum gives the best arm double-exponentially more trials (Gumbel model). | **Analogous**: same "best-of-k with a curve" object, but a max objective over arms rather than a sum over items. |
| 2 | Streeter, M. J. & Smith, S. F. (2006). *An Asymptotically Optimal Algorithm for the Max k-Armed Bandit Problem.* AAAI-06. [V] | Gives O(k ln(k/δ)/ε²) trials to identify a near-best arm for expected max payoff, and an asymptotically optimal strategy. | Analogous (identification). |
| 3 | Streeter, M. J. & Smith, S. F. (2006). *A Simple Distribution-Free Approach to the Max k-Armed Bandit Problem.* CP 2006, LNCS 4204. [S; LNCS volume U] | Threshold Ascent: a distribution-free max-bandit algorithm, applied to scheduling heuristics. | Analogous. |
| 4 | György, A. & Kocsis, L. (2011). *Efficient Multi-Start Strategies for Local Search Algorithms.* JAIR 41:407–444. [V] | MetaMax: gives resources to runs that "could converge to the optimum" under an assumed convergence rate; within a logarithmic factor of the ideal start in practice. | **Analogous**: allocation driven by curve shape (potential improvement), single objective. |
| 5 | David, Y. & Shimkin, N. (2015). *The Max K-Armed Bandit: A PAC Lower Bound and tighter Algorithms.* arXiv:1508.05608. [V; later venue U] | PAC lower bound. Random arm choice can beat adaptive allocation when the arms' maxima are similar. | Analogous: low dispersion means little gain from adaptivity. |
| 6 | Carpentier, A. & Valko, M. (2014). *Extreme Bandits.* NeurIPS 2014. [S] | ExtremeHunter: allocate to detect extreme values. Regret is measured against the heaviest-tailed arm. | Analogous (max objective). |
| 7 | Gao, C., Shang, H., Xue, K. & Qian, C. (2025). *Neural Solver Selection for Combinatorial Optimization.* ICML 2025, arXiv:2410.09693. [V] | Per-instance neural solver selection. Rejection-based and top-p strategies run more solvers on low-confidence instances. | Closest NCO paper with non-uniform per-instance compute. The signal is selector uncertainty, not a curve. **Not** our principle. |
| 8 | Luby, M., Sinclair, A. & Zuckerman, D. (1993). *Optimal speedup of Las Vegas algorithms.* Information Processing Letters 47(4):173–180. [pages V via Kautz et al. 2002 reference list; volume U] | For a known run-time distribution, the optimal schedule is a fixed cutoff. The universal schedule is within a log factor of it. | Regime H, single item. See prior_portfolio.md. |

**Requester's own work (excluded from coding).** Bae, J. (2026a), arXiv:2608.13087, measures allocation in NCO: no detectable gain in-distribution, +11–12% under a uniform/clustered mix, and phantom 2–3% gains from in-sample evaluation. Bae (2026b), arXiv:2609.27917, is a companion paper on spread vs scale. [S] These are the only NCO papers I found that study a sum-over-instances allocation of best-of-k samples.

## 4. Verdict for this field

- **Does NCO already know the principle?** No. The NCO literature uses a uniform per-instance sample budget throughout. The only per-instance compute variation I found (Gao et al. 2025) is driven by selector confidence, not by improvement-curve shape. Classical CO knows **curve-aware allocation across runs/heuristics on one instance** (max-k-armed bandit, MetaMax). That literature uses a global-max objective, so its optimum is "concentrate on the best arm", not water-filling.
- **What would be new for NCO.** These points are new relative to all non-self literature found:
  1. A sum-over-instances formulation for best-of-k gaps with power-law tails, f_i(k) ≈ a_i + b_i k^(−α), with water-filling k_i ∝ b_i^(1/(1+α)).
  2. The statement that the difficulty level a_i cancels, so the dispersion of b_i decides the gain. This matches the max-bandit hint (David & Shimkin) that uniform wins when arms are similar.
  3. The in-sample selection-bias audit.

  All three appear in the requester's own preprints. The paper's contribution to NCO therefore stands, as long as those preprints are the paper's own precursors.
- **Caveat.** NCO uses the term "multi-start" for POMO's N starting nodes *within* an instance. Make clear that the principle concerns allocation *across* instances, not across starts.
