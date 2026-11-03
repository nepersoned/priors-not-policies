# Prior work — computerized adaptive testing (field slug: `cat`)

Codebook v3. Coded file: `coded_cat.jsonl`. Verification status: [V] means I read the abstract or full text in this session (via PMC, publisher page or secondary abstract). [M] means memory only; not verified.

## Regime

**Ability estimation is regime C with α = 1.**
- Var(θ̂_i) ≈ 1/(k_i·Ī_i), where Ī_i is the information the item bank can deliver near θ_i.
- The sum-of-MSE (Neyman) optimum across examinees is k_i ∝ Ī_i^(−1/2).
- A **fixed-SE (fixed-precision) stopping rule** gives k_i ∝ 1/Ī_i, i.e. proportional to variance.
  - This is E3 relative to an aggregate objective.
  - It is correct for the field's stated goal of equal precision per examinee. I coded these papers E3 with an objective-conditional note.
- **Caveat on the shared budget:** CAT has no literal shared budget across examinees. The "budget" is the average test length, which is how variable-length rules are compared against fixed-length tests.

**Classification / mastery testing is B-like.**
- This covers SPRT, GLR, confidence-interval rules and cognitive-diagnosis CAT (CD-CAT).
- P(misclassification) ≈ Φ(−|θ − θ_c|·√(k·I)), so error decays exponentially in k at rate λ = (θ − θ_c)²·I.
- Examinees at the cut score are the "hopeless" items.

## Classical and optimal results

1. **Choi, Grady, Dodd**, "A new stopping rule for computerized adaptive testing" (PSER), *Educational and Psychological Measurement*, 2011 (online 2010; volume/pages unverified). [V abstract]
   - **Result:** stop when the predicted SE reduction from the next item falls below a "hypo" threshold, even if the SE target is unmet. The rule administers "fewer items when predictive gains in information are small".
   - **Relation to our principle:** identical to the marginal rule for α = 1. The motivating problem is the sink at bank-poor θ.
2. **Morris, Bass, Howard, Neapolitan (2020)**, "Stopping rules for computer adaptive testing when item banks have nonuniform information", *International Journal of Testing* 20(2):146–168. [V abstract, PMC7518406]
   - **Result:** under the SE rule, examinees outside the bank's coverage are asked every item. PSER "can avoid administering excessive questions that provide little additional information".
   - **Relation to our principle:** analogous. This is a field-internal statement of the E3/sink failure.
3. **Babcock & Weiss (2012)**, "Termination criteria in computerized adaptive tests: do variable-length CATs provide efficient and effective measurement?", *JCAT* 1:1–18. [V abstract]
   - **Result:** SE termination is "sensitive to the item bank information structure". Change-in-θ (a marginal-type rule) is less sensitive. They also report diminishing returns with very long tests.
   - **Relation to our principle:** analogous.
4. **Wang, Weiss, Shang (2019)**, "Variable-length stopping rules for multidimensional CAT", *Psychometrika* 84:749–771. [V abstract]
   - **Result:** the stated goal is "equal measurement precision for all examinees regardless of" θ. The paper connects the various precision-based rules.
   - **Relation to our principle:** a different objective (equal precision). It is E3 only under an aggregate objective.
5. **Classification CAT: the SPRT family.** [M; abstracts not retrieved]
   - Reckase (1983) [M].
   - Spray & Reckase (1996), *JEBS* 21:405–414 [M details].
   - Eggen (1999), *APM* 23(3):249–261 [M].
   - Thompson (2011), *PARE* (GLR) [V via secondary source].
   - **Result:** these use a likelihood-ratio stop truncated at a maximum length. Near-cut examinees run to the maximum: the length cap is the only protection.
   - **Relation to our principle:** E2-type (MONO-UP, capped).
6. **Stochastic curtailment and projection rules.**
   - Finkelman (2008), *JEBS* 33:442–463 [V secondary abstract]. Curtailment halves average SPRT length without accuracy loss.
   - Sie, Finkelman, Bartroff, Thompson (2015), *APM* 39(4):278–292 [V abstract]. The test stops when the decision is unlikely to change. The paper notes that near-cut examinees otherwise receive all n items.
   - Huebner & Fina (2015), *BRM* 47:549–561 (SCGLR) [V abstract].
   - Luo, Kim, Dickison (2018), *APM* 42(4):275–290 [V abstract]. The confidence-interval rule is "less efficient in the near-cut regions"; projection removes items that are futile.
   - **Relation to our principle:** analogous to the regime-B marginal / NON-MONO rule. The field fixes the hopeless-item sink by asking "can another item change the decision?", which is a marginal-value test.
7. **Recent patient-reported-outcome and Bayesian work.**
   - Luijten et al. (2025), *QoL Research* 34:3205–3214: an SE-reduction rule; gains are largest under floor/ceiling effects [V abstract].
   - Niu & Choi (2026), *BRM* 58: a combined SE plus change-in-θ rule "reduced unnecessarily long tests" [V abstract].
   - BAMA (arXiv:2103.03766): a decision-theoretic per-student stop [V abstract].
   - **Relation to our principle:** analogous (marginal rules).

## Does the field say that level, or dispersion / marginal gain, decides allocation?

**Both coexist, and the field has explicitly diagnosed the level-rule failure.**

- **Default practice** is level-based: stop at SE < threshold, CI excludes the cut, or posterior probability ≥ 0.8.
- **Since about 2008–2011** a methodological line has argued that more items should not go where they cannot help:
  - PSER, change-in-θ and SE-reduction rules for estimation;
  - stochastic curtailment and projection for classification.
- The motivation is stated in our terms: at bank-poor θ, and for near-cut examinees, additional items are wasted.
- CD-CAT termination rules still favour level-type thresholds. Guo & Zheng (2019) recommend an entropy-level (SHE) rule.

## Verdict for CAT

**Partly known.**

- The marginal-value stopping idea, and the warning against spending items on examinees who cannot benefit, is established (Choi et al. 2011; Finkelman 2008; Morris et al. 2020).
- It is framed as heuristic stopping rules. The field does not frame it as a budget-allocation optimum.

What our paper could add:

1. **The explicit exponent.** Under an aggregate-precision objective with a fixed mean test length, the optimum is k_i ∝ Ī_i^(−1/2), not the k_i ∝ 1/Ī_i implied by fixed-SE stopping. I found no CAT paper deriving that Neyman-type allocation across examinees. **Unverified as a gap**: the search was limited to stopping-rule literature.
2. **For classification CAT, the regime-B formula** (peak marginal value at intermediate |θ − θ_c|) as the principled version of curtailment heuristics.

The core qualitative principle is not new to this field.
