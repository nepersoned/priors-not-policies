# Prior work: algorithm portfolios, SAT/MIP solving, restarts, anytime scheduling (field slug `portfolio`)

Survey group A, 2026-10-01. Codebook v3. Coded papers: `coded_portfolio.jsonl` (25 screened, 20 included).

**Verification markers.** [V] means I read the claim in the paper's text during this survey. [S] means search snippet or secondary description only. [U] means from memory, unverified. Page and volume numbers are given only where verified or marked.

## 1. Is there a classical or optimal allocation result?

Yes, several. All of them are for **regime H/B** (time-to-first-success, heavy-tailed or arbitrary run-time distributions).

- **Luby, Sinclair & Zuckerman (1993).** For a known run-time distribution (RTD), the optimal restart strategy is a fixed cutoff t*. For an unknown RTD, the universal sequence 1,1,2,1,1,2,4,... is within a log factor of optimal, and no universal strategy beats it by more than a constant factor. [V, as restated in Streeter et al. 2007 and Kautz et al. 2002] This concerns a single instance. The value of more time on a run depends on the shape of the RTD, not on the instance's mean difficulty.
- **Streeter, Golovin & Smith (2007a, 2007b).** They choose one restart schedule or task-switching schedule for an *ensemble* of instances, minimizing total time. The greedy rule "greedily maximize the number of instances solved per unit time" [V] is a 4-approximation, and better is NP-hard [V]. This is exactly a **marginal-gain-per-cost** allocation for a sum-over-instances first-success objective.
- **Cayci, Eryilmaz & Srikant (2020).** For a bandit with controlled restarts under a time horizon, the optimal decisions maximize the renewal reward rate. A run should be abandoned when its residual reward rate falls below that of a fresh trial. [V] This is the marginal principle in its continuous-time form.
- **Deliberation scheduling** (Boddy & Dean 1989/1994) and **anytime composition** (Zilberstein & Russell 1996). These allocate computation across several anytime procedures using performance profiles (expected quality vs time). With diminishing returns, the greedy/equal-marginal allocation is optimal. [S for Boddy & Dean; U for exact optimality statements and the Zilberstein & Russell details] This is the classical AI statement of "allocate by marginal improvement of the performance profile". It is the closest analogue to regime C water-filling.

## 2. Difficulty level vs dispersion/marginal; warnings against "harder gets more" or spending on hopeless items

The field explicitly favours marginal/RTD-shaped allocation and **warns against sinking time into long (hopeless) runs**.

- **Kautz, Horvitz, Ruan, Gomes & Selman (2002).** Dynamic restart policies, conditioned on early solver-trace features, **prune runs predicted to be long**. The naive policy of giving each predicted class its own optimal cutoff "performed poorly". The authors conclude: "This shows the importance of pruning long runs." [V] Result: 40–65% faster than Luby's fixed-optimal policy on a fresh test set.
- **Heavy tails** (Gomes, Selman, Crato & Kautz 2000; Gomes, Selman & Kautz 1998). Heavy-tailed RTDs make long runs a bad investment, and restarts or portfolios cut the tail. [S/U for exact statements; widely cited] Huberman, Lukose & Hogg (1997) and Gomes & Selman (2001) show portfolios reduce mean and variance by mixing algorithms. [S via Kautz et al. 2002 citation]
- **Portfolio scheduling** (aspeed, 3S, SATzilla presolvers, SUNNY). Time slices go to solvers *more likely to succeed*. SUNNY makes slices proportional to the number of neighbours solved [V]. aspeed computes timeout-minimal non-uniform schedules and beats the uniform ppfolio schedule under 10-fold CV [V]. Lindauer et al. (2016) found that spreading time across too many solvers hurts: "Sunny tends to employ many algorithms per schedule" [V].
- **Penalized metrics** (PAR10) and **per-instance cutoffs** are standard. No paper in the screened set advocates "give more time to harder instances" as a design rule. I did not find an explicit published formula saying that *mean difficulty cancels* in the allocation.
- **Measurement hygiene.** Train/test or cross-validation separation is the norm: aspeed (10-fold CV), SUNNY (5×5 CV), Haim & Walsh (10-fold), Kautz et al. (fresh test set). Streeter et al. (2007a) report in-sample results together with leave-one-out, and the estimate rose by about 4% [V]. The in-sample bias issue is already recognized in practice here.

## 3. Key references

| # | Reference | One-line result | Relation to our principle |
|---|---|---|---|
| 1 | Luby, M., Sinclair, A. & Zuckerman, D. (1993). *Optimal speedup of Las Vegas algorithms.* Information Processing Letters 47(4):173–180. [pages V via citation; volume U] | Optimal fixed cutoff for a known RTD; log-optimal universal schedule for an unknown RTD. | **Analogous**: the single-item regime-H counterpart. Allocation follows the RTD shape. |
| 2 | Kautz, H., Horvitz, E., Ruan, Y., Gomes, C. & Selman, B. (2002). *Dynamic Restart Policies.* AAAI-02. [V] | Feature-conditioned cutoffs that prune predicted-long runs; 40–65% faster than fixed-optimal. | **Special case / identical in spirit** to the regime-B/H warning: don't fund hopeless runs. |
| 3 | Streeter, M., Golovin, D. & Smith, S. F. (2007a). *Restart Schedules for Ensembles of Problem Instances.* AAAI-07, pp. 1204–1210. [V] | Offline, learning-theoretic and online schedules for many instances; 1.7× faster than Luby, 1.5× faster than best uniform cutoff. | **Special case**: sum-over-instances, first-success objective, greedy marginal allocation. |
| 4 | Streeter, M., Golovin, D. & Smith, S. F. (2007b). *Combining Multiple Heuristics Online.* AAAI-07. [V] | Greedy "instances solved per unit time" task-switching schedule, 4-approx; no-regret online. | **Identical** to the marginal rule for regime B/H (across solvers, summed over instances). |
| 5 | Cayci, S., Eryilmaz, A. & Srikant, R. (2020). *Continuous-Time Multi-Armed Bandits with Controlled Restarts.* JMLR 21. arXiv:2007.00081. [V] | Maximize solved-per-unit-time; restart when the residual reward rate falls below a fresh trial's. | **Identical** (marginal reward-rate rule) for regime H. |
| 6 | Hoos, H., Kaminski, R., Lindauer, M. & Schaub, T. (2015). *aspeed: Solver Scheduling via Answer Set Programming.* TPLP 15(1). arXiv:1401.1024. [V; volume U] | Timeout-minimal non-uniform schedules beat the uniform ppfolio schedule (10-fold CV). | Special case: exact optimization of the summed objective. |
| 7 | Gagliolo, M. & Schmidhuber, J. (2006). *Learning Dynamic Algorithm Portfolios.* Annals of Mathematics and Artificial Intelligence, doi:10.1007/s10472-006-9036-z. [V for content and DOI; volume/pages U] | Online time shares from learned RTDs, mixed with a uniform share via Exp4. | Analogous: model-based shares vs uniform, learned online. |
| 8 | Boddy, M. & Dean, T. (1994). *Deliberation scheduling for problem solving in time-constrained environments.* Artificial Intelligence 67(2):245–285. [U for bibliographic details; concept S] | Allocate time across anytime procedures using performance profiles. | **Analogous** to regime-C water-filling (marginal quality per unit time). |

Other relevant work, not in the table: Gomes, Selman, Crato & Kautz (2000), *Heavy-tailed phenomena in satisfiability and constraint satisfaction problems*, J. Automated Reasoning 24 [U for pages]. Xu, Hutter, Hoos & Leyton-Brown (2008), *SATzilla*, JAIR 32:565–606 [U pages]. Kadioglu, Malitsky, Sellmann & Tierney (2010), *ISAC*, ECAI [U]. Kadioglu et al. (2011), *Algorithm Selection and Scheduling (3S)*, CP, LNCS 6876 [S]. Amadini, Gabbrielli & Mauro (2014), *SUNNY*, TPLP [V]. Lindauer, Bergdoll & Hutter (2016), LION, LNCS 10079:253–259 [S]. Hoos & Stützle (2000), *Local search algorithms for SAT: an empirical evaluation*, J. Automated Reasoning 24 [U]. Their RTD methodology shows that for exponential RTDs restarts give no benefit, because the process is memoryless [U, standard result].

## 4. Verdict for this field

- **Does the field already know the principle?** **Yes, for its own regime.** For time-to-solve objectives (regime H/B), the portfolio and restart literature already knows several things:
  1. The value of more time depends on the run-time-distribution shape (Luby).
  2. Allocation should follow marginal "solved per unit time" (Streeter et al.; Cayci et al.).
  3. Long or hopeless runs should be pruned rather than funded (Kautz et al.).
  4. Non-uniform schedules beat uniform ones only when solvers or instances are complementary (aspeed vs ppfolio; Lindauer et al. 2016).

  It also routinely uses cross-validation, so the E4 failure mode is mostly avoided. In the coded set there are 0 E1, 0 E2, 0 E3, 0 E4 and 0 E5 flags; 9 papers are OK.
- **What our paper adds here.** Very little that is substantive. Three possible contributions:
  - **(a) Unification.** Stating that regime-H/B practice (marginal solve-rate, prune hopeless runs) and regime-C best-of-k water-filling are one principle, and that "harder gets more" is wrong in B/H at low u·p.
  - **(b) The level-cancels/spread-governs statement.** This is not stated in these terms in the papers I read. Deliberation scheduling with performance profiles implies it for concave profiles [U whether stated explicitly].
  - **(c) Regime-C content.** The continuous exponent rule k_i ∝ b_i^(1/(1+α)) has no counterpart here, because portfolio objectives are first-success or time-to-solve.

  Recommended framing: **"nothing new for this field's core practice; cite it as established prior art for the regime-B/H half of the principle"** (Kautz 2002, Streeter 2007a/b, Cayci 2020, Luby 1993).
