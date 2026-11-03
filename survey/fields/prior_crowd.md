# Prior work — crowdsourcing / data labeling (field slug: `crowd`)

Codebook v3. Coded file: `coded_crowd.jsonl`. Verification status: [V] means I read the abstract or full text in this session. [M] means the item comes from memory or a secondary source and is not verified.

## Regime choice for this field

- **Majority-vote / label-accuracy objectives are coded as regime B-like.**
  - After k votes on an item with soft label q_i, the probability of a wrong aggregate label decays roughly as exp(−c·k·λ_i), where λ_i = (2q_i − 1)².
  - Khetan & Oh (2016, Sec. 3) show this exact form ("matching predicted e^{−(…)(2q_i−1)²}").
  - The marginal value of one more label is about λ·exp(−kλ). It is non-monotone in difficulty, just as in regime B: the "hopeless" items are those with q ≈ 1/2.
- **Estimation objectives are regime C, α = 1.** These cover the mean of a label distribution, prediction-powered or active inference, and LLM-plus-human estimators. Neyman sampling (π ∝ SD of residual) is correct here.

## Is there a classical or optimal allocation result?

Yes, several.

1. **Karger, Oh, Shah**, "Budget-optimal task allocation for reliable crowdsourcing systems", *Operations Research* 62(1), 2014; arXiv:1110.3564 (2011). [V abstract]
   - **Result:** under the Dawid-Skene model with homogeneous tasks, non-adaptive uniform (random-regular) assignment is order-optimal. Adaptivity does not change the scaling.
   - **Relation to our principle:** a special case. With zero spread across items, uniform is optimal.
2. **Chen, Lin, Zhou**, "Optimistic knowledge gradient policy for optimal budget allocation in crowdsourcing", ICML 2013. Journal version: "Statistical decision making for optimal budget allocation in crowd labeling", *JMLR* 16, 2015; arXiv:1403.3080. [V full text]
   - **Result:** a Bayesian MDP with Beta soft labels. The DP-optimal policy is approximated by Opt-KG, a marginal-value policy.
   - **Key passage (Sec. 1):** "we should simply put those few highly ambiguous instances aside to save budget".
   - **Fig. 4 shows the regime-B peak explicitly:**
     - At low budget, θ ≈ 0.5 instances get fewer labels than θ = 0.35–0.4.
     - Only at high budget does the most ambiguous instance get the most labels.
   - **Relation to our principle:** identical to our regime-B principle for this field, including the budget dependence of the peak.
3. **Khetan & Oh**, "Achieving budget-optimality with adaptive schemes in crowdsourcing", NeurIPS 2016; arXiv:1602.03481. [V full text]
   - **Result:** under generalized Dawid-Skene with task difficulty λ_i, they give a minimax budget–accuracy limit and an adaptive scheme that achieves it.
     - The scheme targets budget ∝ 1/λ per task ("harder gets more"), which equalizes per-task error.
     - The adaptive-versus-uniform gap grows with the spread of difficulty (λ_min versus the collective λ̄).
   - **Caveat:** optimality holds in the high-accuracy regime and under the assumption λ_max/λ_min = O(1). That assumption excludes hopeless tasks.
   - **Relation to our principle:** a special case of our principle in the large-u·p regime. It shows that spread, not level, governs the gain. It does not cover the low-budget or hopeless-item side.
4. **Ipeirotis, Provost, Sheng, Wang**, "Repeated labeling using multiple noisy labelers", *Data Mining and Knowledge Discovery* 28, 2014 (tech report CeDER-10-03). This extends Sheng, Provost, Ipeirotis, KDD 2008, "Get another label?". [V full text of the tech report; KDD 2008 abstract seen via secondary source only, M]
   - **Result:** selective repeated labeling by Bayesian label uncertainty beats round-robin (uniform).
   - **Explicit warning (Sec. 6.1 "What Not To Do"):** entropy-based selection loses to round-robin "because ... most of the labeling resources are wasted", labeling a few examples very many times.
   - **Relation to our principle:** analogous. This is the first empirical statement of the hopeless-sink failure in this field. The fix they propose (Bayesian tail probability) is still a level signal, not a marginal one.
5. **Abraham, Alonso, Kandylas, Patel, Shelford, Slivkins**, "How many workers to ask? Adaptive exploration for collecting high quality labels", arXiv:1411.0149 (SIGIR 2016 [M venue]). [V full text]
   - **Result:** the stopping rule is |V_A − V_B| ≥ C√t − εt.
     - The −εt term deliberately gives up on near-tie items: they are "willing to tolerate a higher error rate for HITs with bias" ≤ ε.
     - ε > 0 beats ε = 0 in their simulations.
   - **Relation to our principle:** analogous. This is a practical hopeless-item discount derived for the workload-level error–cost trade-off.
6. **Hu & Frazier**, "Bayes-optimal effort allocation in crowdsourcing: bounds and index policies", arXiv:1512.09204. [V abstract]
   - **Result:** a POMDP with a Lagrangian-relaxation bound and a Whittle-like index policy.
   - **Relation to our principle:** the marginal-index form, analogous to water-filling.
7. **Manino, Tran-Thanh, Jennings**, "Efficiency of active learning for the allocation of workers on crowdsourced classification tasks", arXiv:1610.06106 (2016). Follow-up: IJCAI 2018, "On the efficiency of data collection for crowdsourced classification" [M, abstract not read].
   - **Result:** uncertainty sampling and info-gain policies beat uniform allocation.
   - **Caveat:** their model has no task-difficulty heterogeneity, so it cannot show the sink.
   - **Relation to our principle:** neither confirms nor contradicts it.
8. **Zrnic & Candès**, "Active statistical inference", ICML 2024; arXiv:2403.03208. [V full text]
   - **Result:** label-sampling probability π(x) ∝ u(x), where u ≈ predicted |Y − f(X)|. This is the Neyman (SD) form for estimation.
   - **Relation to our principle:** identical to the α = 1 regime-C rule.

## Does the field say that level, or dispersion / marginal gain, decides allocation?

**Both views coexist.**

- **The theory papers already have the principle.**
  - Opt-KG uses marginal value and states the ambiguous-item discount in words.
  - Khetan-Oh tie the adaptive gain to the spread of difficulty.
  - Abraham et al. build a give-up term into the stopping rule.
- **Much applied and LLM-era work still uses a level signal**: "most uncertain / least consensus / desired confidence gets more".
  - Examples: Welinder & Perona 2010; uncertainty sampling as analysed by Manino et al.; Clean-or-Annotate 2021.
  - Of these, 6 of 23 included papers are flagged E2.
  - In the estimation sub-area, Perspective-Driven Inference (arXiv:2603.21404, 2026) samples ∝ predicted **squared** error, which is E3. Its own limitations section admits that the rule oversamples groups with irreducible noise.

## Verdict for crowdsourcing

**Largely known.** The regime-B structure of our principle is already in the field (Chen-Lin-Zhou 2013/2015), and so are its main corollaries:

- hopeless items should be dropped at low budget (Chen-Lin-Zhou 2013/2015; Abraham et al.);
- "harder gets more" is right only at high budget or bounded difficulty (Khetan-Oh 2016);
- the gain is driven by spread (Khetan-Oh 2016; Karger-Oh-Shah).

What our paper could add for this field is narrower:

1. A single closed-form statement covering both the regime-B peak (p·(1−p)^k) and the α = 1 Neyman rule, linking the label-accuracy and label-estimation sub-literatures. They do not cite each other.
2. A diagnosis of the recurring level-signal practice in heuristic and LLM-annotation pipelines, and of the variance-versus-SD exponent slip in recent LLM+human inference work.

Claiming novelty of the principle itself for crowdsourcing would not be defensible.
