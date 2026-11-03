# Prior work: simulation optimization / ranking & selection (field slug `simopt`)

Written 2026-10-01 (group B). Items marked **[unverified]** were not checked against the text in this session; they come from memory or from search snippets.

## 1. Is there a classical or optimal allocation result?

Yes. There are several, and they line up with our regimes.

- **Estimation of many means or strata (our regime C, α = 1).**
  - Neyman allocation (n_i ∝ w_i σ_i) is textbook in Monte Carlo stratified sampling. Examples: Glasserman, *Monte Carlo Methods in Financial Engineering*, 2004, §4.3 **[section number unverified]**.
  - Adaptive versions with finite-time guarantees exist: Etoré & Jourdain (MCAP 2010) and Carpentier & Munos (NeurIPS 2011, MC-UCB).
  - Stochastic kriging (Ankenman, Nelson & Staum, OR 2010) derives an optimal replication allocation across design points of square-root (Neyman-like) form **[exact formula unverified]**.
  - When the objective is the *maximum* error rather than the sum, allocation ∝ σ_i² is optimal (Antos, Grover & Szepesvári, TCS 2010). Simopt and bandit papers already separate the σ and σ² exponents by objective.
- **Selection: probability of correct selection (PCS).**
  - OCBA (Chen, Lin, Yücesan & Chick, DEDS 2000) allocates n_i ∝ (σ_i/δ_i)² among non-best designs.
  - Glynn & Juneja (WSC 2004) show that the asymptotically optimal allocation balances the large-deviations rates of the pairwise false-selection events.
  - PFS decays exponentially in n, like our regime B. At large budgets, rate balancing means "the harder (smaller gap) gets more", and that is optimal for PCS.
- **Marginal value of information.**
  - Knowledge gradient: Frazier, Powell & Dayanik, SIAM J. Control Optim. 47(5), 2008; correlated version in INFORMS JOC 2009.
  - The expected-improvement and LL procedures of Chick & Inoue (OR 2001) are the same kind of rule.
- **Allocation across problem instances (contexts, scenarios).**
  - Contextual R&S (Shen, Hong & Zhang, IJOC 2021; Cakmak, Gao & Zhou, TOMACS; Zhang et al., T-ASE 2023) allocates replications across contexts × alternatives by large-deviations rate optimization. The objective is worst-case or average PCS.
  - Nested simulation:
    - Broadie, Du & Moallemi (Mgmt Sci 2011) allocate inner samples to the scenario with "the greatest marginal impact" on the loss-probability estimate. Scenarios far from the threshold get few samples, which matches regime B's "don't spend on settled items".
    - Lee & Glynn (2003) already analysed non-uniform nested estimators **[unverified detail]**.
    - Dang, Feng & Hardy (2022) put all inner samples on proxy-tail scenarios.

## 2. Level versus spread/marginal; warnings against "harder gets more"

- **Estimation:** spread (σ_i) governs allocation and the mean level is irrelevant. This is the standard Neyman result.
- **Selection (PCS):** the level-like quantity (gap δ_i, scaled by σ_i) decides allocation, and "harder gets more" is correct asymptotically for this objective.
- **Known caveats at small budgets, close to our "hopeless items" point:**
  - Shi, Peng & Tuffin (arXiv 2411.10695) report non-monotone PCS behaviour "in low-confidence scenarios". Their finite-budget allocation departs from the large-deviations one.
  - Wu & Zhou (arXiv 1811.12183) show that the initial-sample (signal) cost changes the convergence rate. A constant initial sample gives only a sub-exponential rate.
  - Indifference-zone and probability-of-good-selection formulations deliberately stop separating designs that are within δ of each other. This amounts to not spending on near-ties, which are effectively hopeless to resolve. **[conceptual mapping; no specific paper checked this session]**
  - Broadie et al. 2011 spend little on scenarios already far from the threshold.

## 3. Key references

| # | Citation | Result | Relation to our principle |
|---|---|---|---|
| 1 | J. Neyman. "On the two different aspects of the representative method." JRSS 97(4), 1934. | Optimal stratified allocation n_h ∝ N_h S_h. | **Identical** to regime C with α = 1. |
| 2 | C.-H. Chen, J. Lin, E. Yücesan, S. E. Chick. "Simulation budget allocation for further enhancing the efficiency of ordinal optimization." DEDS 10(3):251–270, 2000. | OCBA ratios n_i/n_j = (σ_i/δ_i)²/(σ_j/δ_j)², plus a rule for the best design. | **Analogous**: a different objective (PCS) with an exponential curve. Harder gets more is correct asymptotically. |
| 3 | P. Glynn, S. Juneja. "A large deviations perspective on ordinal optimization." Proc. WSC 2004. | The optimal static allocation balances the large-deviations rates of false selection. | **Analogous** to regime B at large budget. |
| 4 | P. I. Frazier, W. B. Powell, S. Dayanik. "A knowledge-gradient policy for sequential information collection." SIAM J. Control Optim. 47(5):2410–2439, 2008 **[page numbers unverified]**. | One-step-optimal marginal value-of-information allocation. | **Special case** of the MARGINAL rule for a selection objective. |
| 5 | A. Carpentier, R. Munos. "Finite time analysis of stratified sampling for Monte Carlo." NeurIPS 2011. | MC-UCB adaptively reaches the oracle Neyman allocation, with a regret bound. | **Identical** principle (regime C, α = 1), with a learned signal and its cost charged. |
| 6 | B. Ankenman, B. L. Nelson, J. Staum. "Stochastic kriging for simulation metamodeling." OR 58(2):371–382, 2010. | Optimal replication allocation across design points **[square-root form unverified]**. | Special case of regime-C water-filling, weighted by the metamodel. |
| 7 | M. Broadie, Y. Du, C. C. Moallemi. "Efficient risk estimation via nested sequential simulation." Mgmt Sci 57(6):1172–1194, 2011. | Greedy marginal allocation of inner samples across scenarios beats uniform, improving the MSE order from k^(−2/3) to about k^(−4/5). | **Analogous** to regime B / MARGINAL (threshold misclassification decays exponentially). |
| 8 | H. Shen, L. J. Hong, X. Zhang. "Ranking and selection with covariates for personalized decision making." IJOC 2021 **[year/volume unverified]**. | A fixed-precision PCS guarantee for every covariate value, with allocation across problem instances. | **Analogous** (allocation across R&S problems, PCS objective). |

## 4. Verdict

Simulation optimization **already knows the principle**, and in some respects knows more than our paper states.

- **Regime C (estimation):** Neyman allocation and its adaptive versions are standard, so this is **nothing new for the field**.
- **Selection objectives:** large-deviations rate balancing (OCBA, Glynn–Juneja) is the established optimal allocation. Its "harder gets more" is correct for PCS and must not be flagged as an error. KG and EI are the marginal rules.
- **Allocation across problem instances:** contextual R&S and nested simulation already allocate non-uniformly, by rate or marginal impact, and compare against uniform allocation.

**What could be new, modestly:** a finite-budget statement for *additive* objectives across many independent R&S problems or contexts (average PCS or sum of correct decisions).
- In that setting our regime-B result says that at small budgets the marginal value p(1−p)^k peaks at intermediate difficulty. Near-tied contexts, which are effectively hopeless, should then get *less*. This is the opposite of what asymptotic rate balancing prescribes.
- The finite-budget R&S literature (Shi–Peng–Tuffin; Wu–Zhou; indifference-zone and PGS ideas) touches this but, as far as this search found, does not state it as an allocation rule across contexts. **[absence claim — limited search]**

Beyond that one point, our principle adds **nothing new for this field**.
