# Prior work — online experimentation / A/B testing (field slug: `abtest`)

Codebook v3. Coded file: `coded_abtest.jsonl`. Verification status: [V] means I read the abstract or full text in this session. [M] means the item comes from memory or a secondary citation and is not verified.

## Regime

- **Estimation of means or treatment effects is regime C with α = 1** (variance σ²/n). Our water-filling rule reduces exactly to **Neyman allocation**, n_i ∝ σ_i (weighted by the stratum/arm weight). This is a 1934 result.
- **Detection or discovery objectives are B-like.** Examples are power and probability of finding a winner. Type II error decays as a Gaussian tail in √n.

## Classical and optimal allocation results

1. **Neyman (1934)**, "On the two different aspects of the representative method", *JRSS* 97(4). [M; textbook result]
   - **Result:** optimum stratum allocation n_h ∝ N_h·S_h.
   - **Relation to our principle:** identical to our α = 1 rule.
2. **Hahn, Hirano, Karlan (2011)**, "Adaptive experimental design using the propensity score", *JBES* 29(1):96–108. [V via secondary abstract]
   - **Result:** a two-stage design in which stage-1 data choose the propensity score. The optimal propensity is the Neyman ratio σ₁(x)/(σ₁(x) + σ₀(x)).
   - **Relation to our principle:** identical (α = 1).
3. **Neyman-regret line.** All verified at abstract level [V]:
   - Dai, Gradu, Harshaw, "Clip-OGD", NeurIPS 2023 (arXiv:2305.17187).
   - Zhao, "Adaptive Neyman allocation", EC 2023 (arXiv:2309.08808); explicitly used on online A/B data.
   - ClipSMT (arXiv:2411.14341).
   - Stronger Neyman regret (arXiv:2502.17427).
   - TS-Neyman (arXiv:2606.08418). Its priority index is the "exact one-step marginal variance reduction", i.e. a marginal/water-filling rule.
   - **Relation to our principle:** identical. These papers treat the Neyman design as the gold standard and measure regret against it.
4. **Cai & Rafi (2022/2024)**, "On the performance of the Neyman allocation with small pilots", *J. Econometrics*; arXiv:2206.04643. [V abstract]
   - **Result:** with small pilots, plug-in Neyman can have higher variance than a balanced split. This happens when heteroskedasticity is small or kurtosis is high.
   - **Relation to our principle:** analogous to our points that "spread governs the gain" and "the signal cost must be charged".
   - Also: "Benefits and costs of adaptive sampling" (arXiv:2604.24652) [V full text] shows that adaptive Neyman beats uniform only under variance heterogeneity. It identifies a pilot-error penalty.
5. **Antos, Grover, Szepesvári (2010, TCS)** [M] and **Carpentier, Lazaric, Ghavamzadeh, Munos, Auer (ALT 2011; arXiv:1507.04523)** [V abstract]; also Riquelme et al., ICML 2017 (Trace-UCB) [V abstract].
   - **Result:** for estimating all means "uniformly well" (a max-loss objective), the optimum is n_k ∝ σ_k² (variance).
   - **Relation to our principle:** a different objective, not an error. Under max-loss, the variance exponent is optimal. It would be E3 only under a sum-of-MSE objective. Coded OK with `conditional_flags: ["E3"]`.
6. **"Minimizing Type 2 errors in an experiment-rich regime via optimal resource allocation"**, arXiv:2603.17031 (2026). [V full text]
   - **Setting:** traffic allocation across M concurrent A/B tests.
   - **Result:** the minimax-power optimum is n_i ∝ (σ_i/δ_i)², which equalizes Type II error. The paper contrasts this with minimax-MSE allocation (n ∝ σ²).
   - **Relation to our principle:** a B-like objective under a minimax criterion, so harder-gets-more without bound is correct for it. Under an average-power or expected-discoveries objective, experiments with tiny effects would be hopeless sinks. Coded OK with `conditional_flags: ["E2"]`.
7. **Schmit, Shah, Johari**, "Optimal testing in the experiment-rich regime", AISTATS 2019 (arXiv:1805.11754). [V abstract via secondary source]
   - **Result:** the optimal policy internalizes the opportunity cost of samples. A "paradox of power" holds: high-powered classical tests waste samples.
   - **Relation to our principle:** analogous to the regime-B "don't overspend on low-yield items".
8. **Azevedo, Deng, Montiel Olea, Rao, Weyl**, "A/B testing with fat tails", *JPE* 128(12), 2020. [V abstract via secondary source]
   - **Result:** the optimal number and size of experiments depends on the tail of the effect-size distribution. With fat tails, run many small ("lean") experiments.
   - **Relation to our principle:** analogous. The shape of the value curve decides allocation, not the difficulty level.

## Does the field say that level, or dispersion / marginal gain, decides allocation?

**Dispersion / marginal.**

- Every estimation paper coded (19 of 21) allocates by SD (Neyman) or by marginal variance reduction.
- None allocates by level (e.g., "experiments with smaller effects get more traffic") under a sum objective.
- Proportional-to-variance appears only under explicitly minimax objectives, where it is optimal.
- The literature also warns that the gain disappears when spread is small and pilots are noisy (Cai & Rafi; arXiv:2604.24652).

## Verdict for A/B testing

**Nothing new for the estimation side.** Our regime-C, α = 1 result is Neyman (1934) and its adaptive versions, a mature and actively developed line (Neyman regret, 2023–2026).

What our paper could add is narrower:

- The cross-field framing: Neyman as the α = 1 member of the k ∝ b^(1/(1+α)) family.
- For portfolio/detection objectives (arXiv:2603.17031, Schmit et al.), the explicit warning that power-equalizing allocation (∝ (σ/δ)²) is a minimax choice. Under an average-discovery objective, tiny-effect experiments should be starved instead. I did not find a paper in this sample that states that contrast explicitly. **Unverified as a gap:** the search was limited.

**Flag count: 0 hard flags out of 21 included.**
