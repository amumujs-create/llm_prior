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

## 6. Next preregistration target — Partial Realization Knowledge Experiment

**Why this is next.** The parameter oracle is intentionally too strong to model
real scientific retrieval: RAG rarely returns exact onset, scale, and exponent.
Before building RAG, establish the minimum useful content and precision of
external knowledge. Otherwise a failed RAG result confounds retrieval failure,
missing realization fields, imprecise knowledge, and admission error.

**Primary question.**

> Which realization fields, supplied at which precision, close enough of the
> family-to-parameter gap to yield positive far-OOD utility?

### Candidate conditions to freeze before execution

For each of regime change and emergent curvature:

1. Family only.
2. Each singleton: onset only, scale only, shape/exponent only.
3. Each pair: onset+scale, onset+shape, scale+shape.
4. All three fields (the existing parameter-oracle reference).
5. Full-information oracle (upper-bound reference).

For each supplied field, distinguish exact knowledge from noisy or interval
knowledge. A starting onset-noise sweep is `σ_K ∈ {0, .02, .05, .10, .20}` for
`τ_known = τ + ε`, `ε ~ Normal(0, σ_K²)`. Corresponding scale and exponent
precision grids must be specified before the experiment runs.

### Planned outputs

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

### Decision logic

- If one field (e.g., onset) closes most of the gap, retrieval should prioritize
  evidence for that field rather than generic family labels.
- If field importance differs by family, use prior-conditioned admission
  `A(P, D_obs)` and a family-specific knowledge schema.
- If only exact values help, represent RAG output as uncertain constraints and
  quantify whether ordinary scientific knowledge is sufficiently precise before
  claiming deployment value.
- Only after this experiment should actual RAG candidate generation be added:
  RAG supplies plausible family plus realization constraints; admission decides
  whether remaining uncertainty is safe.

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
5. Link protocol, code, results JSON, figures, and any commit/hash.
