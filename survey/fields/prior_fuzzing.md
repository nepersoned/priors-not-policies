# Prior work: fuzzing and software testing (field slug `fuzzing`)

Survey group D, 2026-10-01. Codebook v3. Coded papers: `coded_fuzzing.jsonl` (36 screened, 31 included).

**Verification markers.**
- [V]: I read the claim in the paper's text (PDF or abstract) during this survey.
- [S]: the claim comes only from a search snippet or a secondary description.
- [U]: the claim is from memory and unverified.

Volume and page numbers are omitted where not verified.

**Regime choice for this field.**
- **Regime B.** I code a seed- or target-level objective as B when it is "a new path, feature or bug is found", or "the target is reached". Each fuzz input is a Bernoulli trial, and its success probability falls as the local neighbourhood is exhausted. In the language of species discovery, the discovery probability is a depleting p.
- **Regime C.** I code totals of coverage over a program or class as C. These are saturating curves, roughly logarithmic in time according to Böhme & Falk 2020 [U]. Allocation across programs, classes or fuzzers falls here.

## 1. Is there a classical or optimal allocation result?

Yes, for regime B. It takes the form "allocate by the estimated probability that the next input discovers something new". It is not stated in closed form like Neyman allocation.

**Woo, Cha, Gottlieb & Brumley (CCS 2013), "Scheduling Black-box Mutational Fuzzing".**
- Fuzzing is modelled as a weighted coupon-collector process [V]. Each (program, seed) configuration is a bandit arm.
- The key quantity is the Remaining Probability Mass (RPM): the probability that one more run yields a new bug. It is bounded by the "Rule of Three", RPM ≤ 3/N(τ) [V].
- Variants:
  - EWT and Rate are time-normalised [V].
  - "Rich Gets Richer" and Density are bug-prior beliefs that give more time to configurations that have already proved buggy [V].
- Round-Robin and Uniform-Random are the baselines [V].

This is the regime-B marginal value p(1−p)^k at the configuration level. Note that it *favours productive (high-p) items*.

**Böhme, Pham & Roychoudhury (CCS 2016; TSE 2019), "Coverage-based Greybox Fuzzing as Markov Chain" (AFLFast).**
- Seeds are states of a Markov chain. The result: CGF "is considerably more efficient if energy is inversely proportional to the density of the stationary distribution and increases monotonically every time that seed is chosen" [V, abstract].
- Relation to our principle: this is analogous, but the signal is **rarity**, not difficulty.
  - A low-frequency path is an under-explored neighbourhood, so rarity tends to *raise* the per-input discovery probability.
  - The exponential growth with times-chosen s(i) is not a hopeless discount.
  - Energy is damped only through f(i) rising.

**Böhme (TOSEM 2018), "STADS: Software Testing as Species Discovery" [U for details].**
- Testing is framed as sampling from a species distribution.
- The Good-Turing estimate of the probability that the next input discovers a new species is f1/n (singletons over samples). This is the empirical marginal value of one more input.
- Relation: identical in spirit to the regime-B marginal-value argument within one campaign. STADS itself does not allocate across items.

**Böhme, Manès & Cha (ESEC/FSE 2020), "Boosting Fuzzer Efficiency: An Information Theoretic Perspective" (Entropic).**
- Shannon entropy of a seed's local species distribution measures the rate at which fuzzing that seed discovers new behaviours. "Entropic assigns more energy to seeds revealing more information" [V].
- A Laplace-style prior gives unfuzzed seeds high energy [V].
- Relation: a special case of marginal-rate allocation, regime B.

**Böhme & Falk (ESEC/FSE 2020), "Fuzzing: On the Exponential Cost of Vulnerability Discovery" [U].**
- Finding each additional vulnerability linearly requires exponentially more machines or time. Coverage grows roughly as log t.
- Relation: this is curve-shape evidence. Coverage-over-time is the α→0 limit of the power-law family, with very flat marginal returns. So level-based allocation across programs is even less informative there than in a typical regime C.

**Yue et al. (USENIX Sec 2020) EcoFuzz [S]; Lyu et al. (USENIX Sec 2019) MOpt [U]; Luo et al. (AsiaCCS 2024) T-Scheduler [V].**
- These are bandit formulations: an adversarial MAB, particle-swarm optimisation over operators, and a Beta-Bernoulli bandit with Thompson sampling.
- Each estimates per-arm or per-seed yield probability and allocates toward it.
- Relation: analogous (learned marginal rate).

**Across items in the strict sense.**
- **Nikolić & Jain (arXiv 2406.18058, 2024/2025), "Fuzzing at Scale".**
  - An equal-time scheduler across about 1,000 programs is suboptimal [V]. The gap between naive and dynamic schedulers can match the gap between two fuzzers [V].
  - Their MAB uses a discounted recent-coverage reward [V].
- **Scalabrino et al. (TOSEM 2021), BOT.**
  - Predicts each class's coverage-vs-budget curve and adds budget greedily by cost-effectiveness [V].
  - This is regime-C water-filling, and it beats the size-proportional rule of Campos et al. (ASE 2014) [V, as described in BOT].

## 2. Level vs dispersion/marginal; warnings about "harder gets more" and hopeless items

**Seed scheduling: the field speaks in marginal-rate language.**
- Examples: "efficiency to trigger unique paths" (SLIME [V, abstract]), discovery probability (Woo; STADS), entropy (Entropic), Beta-Bernoulli posteriors (T-Scheduler).
- The dominant heuristic signal is **rarity**, not difficulty: AFLFast, FairFuzz, AFL-Hier, AFL++ "rare". It is usually justified as under-exploration.
  - FairFuzz's abstract does equate rare branches with code "empirically hard to cover" [V, S2 abstract].
  - AFL-Hier explicitly abandons the raw marginal reward. The stated reason is that "the probability of exercising new coverage is dramatically decreased" [V]. It switches to a rareness reward.

**Hopeless-item discounts exist and are explicit.**
- K-Scheduler: the count "should decrease if mutation history information suggests an edge is hard to reach" [V].
- FishFuzz: "exhaustively explored targets should be dropped" and it "discards unfruitful targets" [V].
- Beacon prunes provably infeasible paths [S].
- Woo et al.'s RPM decays to zero for exhausted configurations [V].

**"Harder gets more" without a hopeless discount appears in multi-target directed fuzzing.**
- LeoFuzz (TDSC 2023): "TSi is more difficult to reach, and thus the seed should be assigned more energy" [V].
- AFLRun (USENIX Sec 2024) assigns equal weight per target so that "deeper target sites" are not starved [V]. It has no discount for unreachable targets.
- These are the two E2 flags.

**No warning against these rules was found.**
- I found no fuzzing paper that states the regime-B threshold: harder-gets-more is right only when u·p is large, and at small u·p solvable items should get more.
- I also found none that warns against "fairness" across targets of very different reachability.
- DigFuzz (NDSS 2019) sends the "most difficult paths" to concolic execution [V, abstract]. This is a division-of-labour argument for a complementary, near-deterministic tool, not an attempts-allocation argument (coded N/A).

## 3. Key references

1. **Woo, M., Cha, S. K., Gottlieb, S., Brumley, D.** "Scheduling Black-box Mutational Fuzzing." ACM CCS 2013. doi:10.1145/2508859.2516736.
   - Result: weighted coupon-collector and MAB allocation across (program, seed) configurations, by remaining probability mass. [V]
   - Relation: **analogous to / special case of** regime-B marginal allocation, from empirical upper bounds.
2. **Böhme, M., Pham, V.-T., Roychoudhury, A.** "Coverage-based Greybox Fuzzing as Markov Chain." ACM CCS 2016 (ext. IEEE TSE 2019). doi:10.1145/2976749.2978428.
   - Result: energy should be inversely proportional to the stationary density of the seed's path. [V]
   - Relation: **analogous.** The rarity signal approximates discovery probability. It is not a difficulty level.
3. **Böhme, M.** "STADS: Software Testing as Species Discovery." ACM TOSEM 27(2), 2018. doi:10.1145/3210309 [DOI unverified].
   - Result: Good-Turing discovery probability as the marginal value of the next test. [U for exact statements]
   - Relation: **analogous** (it gives the marginal-value estimator, but no cross-item allocation).
4. **Böhme, M., Manès, V. J. M., Cha, S. K.** "Boosting Fuzzer Efficiency: An Information Theoretic Perspective." ESEC/FSE 2020. doi:10.1145/3368089.3409748.
   - Result: entropy measures the discovery rate, and energy goes to high-information seeds. [V]
   - Relation: **special case** (marginal-rate allocation in regime B).
5. **Böhme, M., Falk, B.** "Fuzzing: On the Exponential Cost of Vulnerability Discovery." ESEC/FSE 2020. doi:10.1145/3368089.3409729 [DOI unverified].
   - Result: discoveries grow roughly logarithmically in resources. [U]
   - Relation: **curve-shape evidence** (flat marginal returns), not an allocation rule.
6. **Nikolić, I., Jain, R.** "Fuzzing at Scale: The Untold Story of the Scheduler." arXiv:2406.18058 (2024; v2 2025).
   - Result: dynamic MAB schedulers across programs beat equal time allocation. [V]
   - Relation: **analogous** (marginal-rate allocation across items).
7. **Scalabrino, S., Mastropaolo, A., Bavota, G., Oliveto, R.** "An Adaptive Search Budget Allocation Approach for Search-Based Test Case Generation." ACM TOSEM 30(3):36, 2021. doi:10.1145/3446199.
   - Result: predicted coverage curves per class plus a greedy marginal allocation. [V]
   - Relation: **identical in form** to regime-C water-filling, with a learned curve.
8. **Liang, H., Cheng, X., Liu, J., Li, J.** "Multiple Targets Directed Greybox Fuzzing" (LeoFuzz). IEEE TDSC 2023, arXiv:2206.14977.
   - Result: harder target sequences get more energy. [V]
   - Relation: **counter-example** (E2).

## 4. Verdict

**What the field already has.**
- For seed scheduling, and for time across programs and fuzzers, fuzzing already practises the regime-B principle in its own vocabulary. It allocates by estimated discovery probability or marginal yield, and it discounts exhausted or infeasible items. See Woo 2013, STADS, Entropic, the bandit schedulers, K-Scheduler and FishFuzz.
- Test generation across classes has regime-C water-filling (BOT).
- For these settings our paper adds **little beyond a unifying explanation**.

**What our paper can add.**
1. **Multi-target directed fuzzing.** Recent "fairness" and "harder target gets more" energy rules (LeoFuzz, AFLRun) lack a hopeless-target discount. The regime-B analysis says that at small u·p, which is typical for deep targets, energy should go to reachable targets.
2. **Rarity versus difficulty.** The field conflates rarity (under-exploration, often high p) with difficulty (low p). The codebook's level-vs-marginal distinction makes this explicit.
3. **An explicit u·p threshold.** I found no fuzzing paper that states it, or the peak of p(1−p)^k at p = 1/(k+1).

These are modest additions. For the core of fuzzing power-schedule theory, the verdict is **"largely known; nothing fundamentally new"**.
