# Experiment notebook — generic structural-prior extrapolation

> **Purpose.** This is the living scientific log for this repository. It does
> not replace frozen protocols or machine-readable results. After every
> experiment, add (1) the question inherited from the prior result, (2) what
> was held fixed and manipulated, (3) the observed result including negative
> evidence, (4) the supported and unsupported claims, and (5) the precise next
> uncertainty. This prevents a collection of plots from becoming a post-hoc
> story.

## Current research thesis

```text
Retrieve plausible structural knowledge
→ constrain its extrapolative realization
→ admit it only when remaining uncertainty is safe
→ far-OOD extrapolation
```

The working prior is not merely a family label. It has three components:

```text
P = { family, ψ: realization constraints, q: confidence / uncertainty }
ψ may contain onset, scale, shape, bound, or intervals/distributions over them.
```

The central causal chain under investigation is:

```text
Family truth → Structural evidence → Parameter identifiability
             → Safe realization → Utility
```

`O` is always interpreted **within a family** as an exposure coordinate. Equal
numeric values of `O` do not imply equal absolute information across families.

---

## 0. Study rules and vocabulary

### What is being evaluated

- **Generative-family oracle:** receives only the true structural family; all
  realization parameters are fitted from the observed prefix.
- **Parameter oracle:** receives the family plus predeclared consequential
  realization parameters; remaining nuisance parameters are fitted.
- **Full-information oracle:** receives the complete generator and is an
  upper-bound reference, not a deployable method.
- **Admission:** must estimate `P(U_P > 0 | D_obs)`, not whether the family is
  true in the world.

### Status conventions

- **Development:** mechanism discovery or rule construction. Do not call it a
  confirmation result.
- **Frozen confirmation:** a previously locked rule on independent draws.
- **Negative result:** a prespecified statement did not hold. Keep it; do not
  tune it away.

Full definitions and legacy-key mappings are in [TERMINOLOGY.md](TERMINOLOGY.md).

---

## Literature grounding - why fit error alone is not enough

These papers are **external methodological grounding**, not independent
validation of this repository's synthetic claims. They motivate what should be
measured and constrained; our own experiments establish the specific
observability, identifiability, and realization findings below.

### A. Symbolic regression: accuracy must be traded against complexity

Harry Desmond's recent work on exhaustive symbolic regression and MDL frames
selection as an accuracy-complexity trade-off: highly complex likelihood-maximizing
expressions can overfit and generalize or extrapolate poorly. It treats the
accuracy-complexity plane as a Pareto problem rather than selecting by MSE alone.

- Desmond, H. (2026). *[Exhaustive Symbolic Regression and model selection by
  minimum description length](https://doi.org/10.1098/rsta.2024.0584)*,
  Philosophical Transactions of the Royal Society A.

**Use in this project.** Prefix fit cannot be the selection criterion for an
extrapolative prior. We therefore retain far-OOD utility, parameter
identifiability, and realization-gap measures alongside fit quality. This paper
does not imply that our particular family priors or complexity measures are
optimal.

### B. Shape constraints: structural validity and pointwise loss are separate objectives

Haider et al. study shape-constrained multi-objective symbolic regression under
noise and extrapolation. Their constrained search treats prediction error and
constraint violation separately; they report a low-noise setting where enforcing
shape constraints increases training prediction error while slightly lowering
test error. They also note that guaranteed constraints can restrict the search
space and affect accuracy.

- Haider, C., de Franca, F. O., Burlacu, B., & Kronberger, G. (2023).
  *[Shape-constrained multi-objective genetic programming for symbolic
  regression](https://doi.org/10.1016/j.asoc.2022.109855)*, Applied Soft
  Computing, 132, 109855.

**Use in this project.** It supports reporting structural/derivative validity
separately from pointwise RMSE, and motivates the acceleration robustness check
with constrained spline and neural-basis realizations. It is not evidence that
any shape constraint is beneficial when its scientific premise is wrong or
unobservable.

### C. Derivative-aware learning: values and derivatives encode different information

Sobolev Training augments value matching with target derivative matching. The
authors give theory and experiments in which derivative supervision improves
data efficiency and generalization in their studied settings.

- Czarnecki, W. M., Osindero, S., Jaderberg, M., Swirszcz, G., & Pascanu, R.
  (2017). *[Sobolev Training for Neural
  Networks](https://proceedings.neurips.cc/paper_files/paper/2017/hash/758a06618c69880a6cee5314ee42d52f-Abstract.html)*,
  NeurIPS 2017.

**Use in this project.** It is methodological precedent for recording slope,
curvature, and derivative-sign consistency as evidence primitives, rather than
evaluating only function-value RMSE. It does not establish that Sobolev loss or
true derivatives are available in our deployment setting; our current pipeline
uses prefix-derived structural evidence instead.

### D. Distance from training support: OOD risk and uncertainty are deployment variables

Distance from the observed/training support is a separate source of risk from
whether a structural mechanism has become visible in the prefix. Meyer and
Pebesma define a dissimilarity index as a weighted distance from a prediction
point to the training data in predictor space, and use it to delimit an *area
of applicability*. Their central warning is that cross-validation error is not
automatically applicable outside that support.

- Meyer, H., & Pebesma, E. (2021). *[Predicting into unknown space? Estimating
  the area of applicability of spatial prediction
  models](https://doi.org/10.1111/2041-210X.13650)*, Methods in Ecology and
  Evolution, 12(9), 1620–1633.

Tossou et al. independently construct molecular regression OOD settings and
report that performance and calibration deteriorate as test/deployment examples
move farther from the training distribution. They argue that train-to-deployment
distance should be represented in evaluation and deployment decision-making.

- Tossou, P., Wognum, C., Craig, M., Mary, H., & Noutahi, E. (2024).
  *[Real-World Molecular Out-of-Distribution: Specification and
  Investigation](https://doi.org/10.1021/acs.jcim.3c01774)*, Journal of
  Chemical Information and Modeling, 64(4), 1012–1025.

**Use in this project.** Let `O` denote *mechanism exposure* inside the
observed prefix (for example, post-onset evidence), and let `d` denote the
distance of an evaluation/deployment query beyond the support boundary. They
must not be conflated: a mechanism can be highly observable (`O` high) while a
farther query still has larger continuation risk. The current synthetic tail
keeps its far-OOD region fixed, so it demonstrates an `O → utility` relation;
it does **not** yet estimate a `d → utility` curve.

### E. Extrapolation-aware validation: interpolation and extrapolation select differently

Garcia and Naets introduce Leave-Boundary-Out (LBO) splitting specifically to
select regression models for extrapolation. Across their benchmark they find an
interpolation–extrapolation trade-off, and the models selected with
extrapolation considered are often simpler than those selected under standard
splits (with the precise pattern model-class dependent).

- Garcia, M., & Naets, F. (2025). *[Beyond Limits: Enhancing the
  Extrapolation Performance of Regression Models by Leaving the Boundary
  Out](https://doi.org/10.1007/s10994-025-06933-8)*, Machine Learning.

**Use in this project.** This supports treating a boundary/leave-out-tail
protocol as a model-selection instrument rather than evaluating only random
interpolation-style splits. It does not claim that a simpler realization is
always better; complexity must be judged jointly with held-out continuation
utility and structural validity.

### Consequence for the experimental record

Every future experiment should distinguish at least four layers:

```text
prefix fit / function-value error
structural or derivative validity
parameter identifiability and realization uncertainty
distance from support (d) and uncertainty/calibration
far-OOD utility and harm risk
```

This makes a model that fits a prefix well but has an implausible continuation
visible as a separate failure mode, rather than hiding it in one aggregate score.

---

## 1. Generic observability sweep — the starting phenomenon

**Question inherited from the initial feasibility check.** If the matching
structural family is true, is it always useful for far-OOD extrapolation?

**Design.** Three generic families—regime change, emergent curvature, and
asymptotic bound—were exposed to different degrees before the fixed boundary.
The matching generative-family prior was fit only on a noisy prefix and compared
with an affine fallback on a clean withheld tail.

**What we observed.** In all three families, low exposure could make a matching
family prior harmful; utility increased as the family-defining behavior became
visible. The pooled observability–utility association was strongly positive
(`Spearman ρ=.726` in the later, broader sweep), but not deterministic.

**What this established.**

```text
Prior truth ≠ prior observability ≠ prior utility.
```

**What it did not establish.** It did not tell us whether a useful prior could
be recognized from the prefix, nor why a true family could fail.

**Next question generated.** Can admission use prefix-only evidence to prevent
harmful matching priors from being deployed?

**Artifacts.** `RESULTS_V1.md`, `results/generic_observability_sweep_v1/`,
`figures/fig01_observability_to_utility.png`.

---

## 2. Admission-v2 development — utility-aware safety screening

**Question inherited from the observability sweep.** Does prefix evidence
separate useful from harmful realizations better than a simple pseudo-OOD gate?

**Design.** A 4,500-task development grid used boundary, structural,
stability, and identifiability evidence. A fixed logistic rule targets the sign
of clean-tail utility. `O_true` is analysis-only and never enters the feature
matrix.

**What we observed.** Relative to v1, v2 reduced harmful false admission from
`65.0%` to `20.9%`, while coverage changed from `63.3%` to `56.3%` and useful
prior admission improved from `62.4%` to `76.8%`.

**What this established.** The evidence primitives could discriminate harmful
from useful fitted priors in held-out development seeds; this was not explained
solely by rejecting everything.

**What it did not establish.** Development tuning is not independent evidence.

**Next question generated.** Does the frozen rule reproduce on fully disjoint
draws without feature, normalization, threshold, or label changes?

**Artifacts.** `ADMISSION_V2_PROTOCOL.md`, `RESULTS_ADMISSION_V2.md`.

---

## 3. Frozen admission-v2 confirmation — the safety finding reproduces

**Question inherited from v2 development.** Is the safety gain robust on new
random seeds, parameter draws, and noise realizations?

**Design.** The protocol, source, configuration hashes, classifier, and `.50`
threshold were frozen before an independent 4,500-task confirmation grid.
Primary endpoint: harmful false-admission rate (FAR).

**What we observed.** FAR fell from `63.98%` (v1) to `19.28%` (v2), paired
`ΔFAR=-.4469`, 95% CI `[-.4785, -.4166]`. Coverage changed `62.16%→56.02%`,
useful-prior admission `61.10%→77.27%`, and admitted-set harm risk
`37.72%→12.61%`.

**Qualification retained.** For the asymptotic-bound family, FAR rose because
harmful cases are rare, though admitted-set harm risk fell and useful-prior
admission increased. Pooled evidence must not hide this family-level nuance.

**What this established.** Admission can be framed as a reproducible
utility-aware safety decision, rather than a family-truth classifier.

**Next question generated.** What makes a matching family realization harmful
when the family itself is known to be true?

**Artifacts.** `FROZEN_ADMISSION_V2_MANIFEST.json`,
`RESULTS_ADMISSION_V2_CONFIRMATION.md`,
`figures/fig08_confirmation_coverage_harm_risk.png`.

---

## 4. Oracle decomposition — family truth is not realization knowledge

**Question inherited from confirmation.** Why can extrapolation fail despite
knowing the correct structural family?

**Design.** On identical synthetic tasks, compare affine fallback,
generative-family oracle, parameter oracle, and full-information oracle.
The parameter oracle receives onset, post-onset scale, and exponent for regime
change/curvature; asymptotic bound receives its true lower limit.

**What we observed.** At low exposure, the matching family prior was much worse
than fallback (e.g., regime `0.097–0.110` vs fallback `0.014–0.034`), while the
parameter oracle was approximately `.003`. Emergent curvature replicated this
pattern. For asymptotic bounds, family-only performance became excellent only
when the saturation behavior was strongly exposed. Three acceleration
realizations—power law, constrained spline, constrained neural basis—also
showed low-exposure harm, ruling out a power-law-only explanation.

**What this established.**

```text
Structural truth ≠ knowledge of extrapolative realization.
```

The failure is consistent with uncertainty in consequential continuation
parameters, not family misspecification.

**Qualification retained.** At the original maximum `O=.533`, family-only had
not converged to the parameter oracle. Visibility and identifiability remained
separate; this was not yet evidence that longer exposure could never close the
gap.

**Next question generated.** Does substantially more post-onset exposure make
family-only realization parameters identifiable from data alone?

**Artifacts.** `ORACLE_DECOMPOSITION_PROTOCOL.md`,
`RESULTS_ORACLE_DECOMPOSITION_V1.md`, `figures/fig09_*`, `figures/fig10_*`.

---

## 5. Exposure / identifiability extension — more exposure helps but does not close the gap

**Question inherited from oracle decomposition.** Does extended observation of
a true structural behavior make its extrapolative realization identifiable from
data alone?

**Design.** Regime change and emergent curvature only; new independent draws;
`O=.533, .60, .70, .80, .90`; 250 tasks per family-level. Primary endpoint is
the paired realization gap:

```text
G = RMSE(generative-family oracle) − RMSE(parameter oracle).
```

The pre-result practical-convergence rule was upper paired bootstrap 95% CI of
`G <= .01`. Mechanism records track onset, scale, and exponent errors.

**What we observed.** Both family-only error and realization-parameter error
decreased with exposure, but practical convergence did not occur.

| Family | G at O=.533 | G at O=.90 | 95% CI at O=.90 | Result |
|---|---:|---:|---:|---|
| Regime change | .0675 | .0346 | [.0310, .0383] | Not converged |
| Emergent curvature | .0687 | .0438 | [.0382, .0494] | Not converged |

At the same `O=.90`, family knowledge was valuable: family-only RMSE was `.0362`
versus fallback `.1816` for regime change, and `.0477` versus `.1173` for
curvature. Parameter error also fell, so more exposure improves realization
quality and utility without making external realization knowledge dispensable
in the tested grid.

**What this established.**

```text
Visible ≠ identifiable.
Family knowledge is valuable, but not sufficient in this tested setting.
```

**What it does not establish.** It does not prove family labels are universally
or intrinsically insufficient. More support, a nearer tail, lower noise, or a
different generator could change the result.

**Next question generated.** Which parts of realization knowledge are valuable,
and how precise must that knowledge be before it improves far-OOD extrapolation?

**Artifacts.** `EXPOSURE_IDENTIFIABILITY_EXTENSION_PROTOCOL.md`,
`RESULTS_EXPOSURE_IDENTIFIABILITY_EXTENSION_V1.md`,
`figures/fig11_exposure_identifiability_extension.png`,
`figures/fig12_exposure_parameter_identification.png`.

---

## 6. Partial Realization Knowledge Sweep — the retrieval target is family-dependent

**Why this is next.** The parameter oracle is intentionally too strong to model
real scientific retrieval: RAG rarely returns exact onset, scale, and exponent.
Before building RAG, establish the minimum useful content and precision of
external knowledge. Otherwise a failed RAG result confounds retrieval failure,
missing realization fields, imprecise knowledge, and admission error.

**Primary question.**

> Which realization fields, supplied at which precision, close enough of the
> family-to-parameter gap to yield positive far-OOD utility?

### Frozen conditions

For each of regime change and emergent curvature:

1. Family only.
2. Each singleton: onset only, scale only, shape/exponent only.
3. Each pair: onset+scale, onset+shape, scale+shape.
4. All three fields (the existing parameter-oracle reference).
5. All three fields, exact (the parameter-oracle reference).

For each supplied field, distinguish exact knowledge from noisy or interval
knowledge. A starting onset-noise sweep is `σ_K ∈ {0, .02, .05, .10, .20}` for
`τ_known = τ + ε`, `ε ~ Normal(0, σ_K²)`. Corresponding scale and exponent
precision grids must be specified before the experiment runs.

### Execution result

The sweep ran at `O=.90` on 400 independent base trajectories (2 families ×
200), reusing each noisy prefix across all conditions. It produced 14,400
paired fits. Exact constraints show that no field has a universal ranking:

| Family | Strongest exact pair | Gap closed | Important counterexample |
|---|---|---:|---|
| Regime change | onset+scale | 97.7% [97.0, 98.2] | onset alone: 21.3% |
| Emergent curvature | scale+shape | 92.8% [90.5, 94.7] | onset alone: 3.6%, CI includes 0 |

Precision changes the result. The all-field condition is perfect only when
exact; for regime change it falls to 53% closure at `.05` retrieval noise and
below family-only at `.10`. Curvature tolerates moderate all-field uncertainty
better (68% at `.10`) but falls below family-only at `.40`. Therefore RAG must
return constraints **and their uncertainty**, rather than be treated as a
point-parameter oracle.

### Outputs now recorded

- Far-OOD RMSE and utility versus fallback for every knowledge subset.
- Incremental gap closure relative to family-only and full parameter knowledge.
- Knowledge precision → utility curves, with intervals over fresh random draws.
- Family-specific ranking of onset, scale, and shape information.
- An uncertainty-aware ontology recommendation:

```text
Structural family
└── realization constraints: onset, scale, shape, bound
    └── uncertainty / confidence / provenance
```

### Decision and next question

- Retrieval schema: family plus onset, scale, shape, and an uncertainty/confidence
  field. The evidence priority is onset+scale for regime change and scale+shape
  for curvature in this generator.
- Admission should be prior-conditioned, `A(P, D_obs)`, because both valuable
  fields and tolerance to imprecision differ by family.
- Next step before actual retrieval: freeze a **RAG information specification**
  that describes what an item must return (field, constraint/range, confidence,
  provenance) and how uncertain constraints enter realization fitting. Actual
  RAG can then be evaluated as candidate/constraint recall rather than an
  uninterpretable end-to-end black box.

**Artifacts.** `PARTIAL_REALIZATION_KNOWLEDGE_PROTOCOL.md`,
`RESULTS_PARTIAL_REALIZATION_KNOWLEDGE_V1.md`,
`results/partial_realization_knowledge_sweep_v1/results.json`,
`figures/fig13_partial_knowledge_exact_gap_closure.png`,
`figures/fig14_partial_knowledge_precision_sweep.png`.

---

## Update checklist for every future experiment

1. Add a frozen protocol before running; do not edit its scientific rule after
   observing results.
2. Add a dated entry above with question, manipulation, held-out information,
   primary endpoint, and status.
3. Report the strongest contrary or family-specific evidence, not only pooled
   improvements.
4. State what the result supports, what it does not support, and one next
   question that follows logically.
5. Record both mechanism exposure/observability (`O`) and query distance from
   support (`d`) when the design varies either one; do not use one as a proxy
   for the other without an explicit validation.
6. Link protocol, code, results JSON, figures, and any commit/hash.

---

## 7. Prior Evaluation Metric Experiment — selection is not only a value-fit question

**Question.** Can pseudo-OOD pointwise MSE select a structural-prior candidate
reliably as evaluation moves farther outside observed support, or do
direction/curvature/complexity metrics provide a better selection signal?

**Why this follows now.** The prior-realization results showed that a family
label does not determine a safe continuation. Before testing residual capacity
or knowledge specificity, we must ask whether the *selection metric* rewards
the appropriate candidate at all. This test explicitly separates structural
compatibility, realization quality, and far-OOD utility.

**Frozen manipulation.** Three existing generators × low/mid/high evidence ×
noise `.005/.015/.030` × 100 draws (2,700 tasks). Inner fit is `t <= .45`,
pseudo-OOD selection is `.45 < t <= .60`, candidates are refit on `t <= .60`,
and far-OOD bands are D1 `.70–.80`, D2 `.90–1.00`, D3 `1.20–1.30`. No composite
score was formed. Candidate metrics were MSE, first/second-difference cosine,
derivative-sign agreement, Spearman trend, and predictive BIC.

**Result.** MSE was the strongest value/shape-only selection rule, but
complexity-aware predictive BIC did better pooled: D3 regret `.0817`
`[.0769,.0869]` versus MSE `.0973` `[.0905,.1044]`, a 16.1% reduction, and
incompatible selections fell from 25.4% to 22.7%. Derivative-sign and Spearman
were safe in a narrow compatibility sense (0% incompatible selections) but
lost too much realization information: both had D3 regret `.1648` and 97.0%
pseudo-vs-far winner disagreement. Difference-cosine rules were worse and
selected incompatible candidates frequently.

**What it supports.** Pseudo-OOD MSE is not uniformly optimal for the fixed
candidate library; adding an explicit complexity penalty improved pooled
far-OOD selection. The result does **not** support replacing value fit with
derivative/trend matching alone. The BIC improvement is family-dependent:
asymptotic-bound settings drive much of it, while several high-exposure
regime-change cells favor MSE.

**Logical next question.** Is MSE sometimes selecting an incompatible prior
because that candidate has extra residual capacity that improves near-support
fit while concealing a poor structural continuation? E2 will compare MSE and
BIC under capacity-matched versus capacity-stress residual corrections.

**Artifacts.** [Frozen protocol](PRIOR_EVALUATION_METRIC_PROTOCOL_V1.md) ·
[result report](RESULTS_PRIOR_EVALUATION_METRIC_V1.md) ·
`experiments/prior_evaluation_metric_v1.py` ·
`results/prior_evaluation_metric_v1/results.json` ·
`figures/fig15_prior_metric_regret_by_distance.png` ·
`figures/fig16_prior_metric_selection_risk.png`

---

## 8. Model Capacity / Residual Stress Test — a falsified mechanism is still useful

**Question.** Does pseudo-OOD MSE prefer an incompatible structural candidate
only because a higher-capacity residual can improve near-support fit?

**Frozen manipulation.** E1's entire generator/support/selection contract was
retained. Each candidate was `prior + ridge-polynomial residual`. Compatible
candidates and neutral `P0` used four basis terms; incompatible candidates used
four, eight, or sixteen. E1's MSE and predictive BIC were the only selectors.
This is 2,700 base draws × 3 capacity ratios = 8,100 capacity cases.

**Result.** The proposed monotone masking pattern did not occur. MSE's
incompatible-selection rate fell from 36.0% at matched capacity to 3.8% at 2×
and 0% at 4×; BIC followed the same direction (34.3%, 2.0%, 0%). High-capacity
polynomial corrections were often sufficiently unstable already in pseudo-OOD
that both selectors rejected them. However, rare 2× selections produced severe
D3 regret: MSE `14.052 [10.706,17.594]`, BIC `7.986 [5.507,10.761]`. The
average selected residual/prior norm ratio was about `.07`, but the residual
changed first-difference direction about `.31` of pseudo-OOD steps.

**What it supports.** Residual capacity is itself a distance-dependent
realization risk, and BIC reduces the extreme failure in this stress setting.
It does **not** support the general causal claim that flexible residuals make
MSE select an incompatible prior more often. That claim stays open for spline
or neural corrections; it cannot be claimed from this result.

**Logical next question.** Even without the masking mechanism, how much prior
detail should a system use at each evidence level? E3 tests the independent
specificity hierarchy: weak constraints → family → family plus realization
intervals.

**Artifacts.** [Frozen protocol](RESIDUAL_CAPACITY_STRESS_PROTOCOL_V1.md) ·
[result report](RESULTS_RESIDUAL_CAPACITY_STRESS_V1.md) ·
`experiments/residual_capacity_stress_v1.py` ·
`results/residual_capacity_stress_v1/results.json` ·
`figures/fig17_residual_capacity_stress.png`

---

## 9. Prior Specificity Hierarchy — accurate external constraints can dominate exposure

**Question.** Is a more specific prior harmful when evidence is low, and useful
when evidence is high?

**Result.** Not under the specified L4 condition. L4 supplied the matching
family plus ±10% intervals on realization fields. It beat direction-only L1
even at low exposure: D3 `L4-L1` was −.1666 for regime change, −.1383 for
curvature, and −.0192 for bounds. At very high evidence, weak L1 had large
under-specificity costs: .4614, .3025, and .5386, respectively.

**Interpretation.** This is a boundary condition on the previous realization
claim, not a contradiction. Accurate external constraints can make a specific
prior useful before the structure is identifiable from the prefix. Therefore
the v1 hierarchy cannot support an “over-specificity always harms at low O”
claim. The next valid variant must vary interval calibration/width, rather than
assuming all L4 constraints are accurate.

**Artifacts.** [Frozen protocol](PRIOR_SPECIFICITY_HIERARCHY_PROTOCOL_V1.md) ·
[result report](RESULTS_PRIOR_SPECIFICITY_HIERARCHY_V1.md) ·
`experiments/prior_specificity_hierarchy_v1.py` ·
`results/prior_specificity_hierarchy_v1/results.json` ·
`figures/fig18_prior_specificity_hierarchy.png`
