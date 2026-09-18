# Prior Primitive–Composition Benchmark v1 — frozen design

## Scope

This benchmark studies priors as scientific objects, not models. Version 1 is
deliberately restricted to **one-dimensional progression → scalar target**.
Scaling, memory, conservation, multivariate interaction, and periodicity are
out of scope for v1.

## Constraint primitives

| Primitive | Constraint-level truth label | Specificity ladder |
|---|---|---|
| Direction | sign of `f'` on target domain | sign → sign + rate range |
| Curvature | sign of `f''` | sign → sign + magnitude range |
| Inflection | `f''` changes sign | possible → one change → location interval |
| Turning point | `f'` changes sign | possible → one turn → location/type interval |
| Regime/change point | local law changes | possible → one change → onset interval → onset + post-change shape range |
| Bound | one-sided range constraint, e.g. `f>=L` | type → bound interval |
| Asymptote | convergence toward a limiting region, `f→L` | possible → limit interval → limit + approach-rate range |

A prior is an **AND conjunction** of constraints, never a particular power-law
or exponential formula. Formula classes are possible realizations only. In
particular: inflection is continuous `f''` sign change; turning point is `f'`
sign change; regime change is a change in local law/parameter at an onset. A
trajectory may carry multiple labels, but code must retain which check supplied
each label.

## Composition and truth

Sample one-to-three compatible primitives. Truth is multi-label, e.g.
`decreasing + convex + bound` or `decreasing + regime change + curvature`.
Candidate priors include true weak/strong, broad correct, narrow correct,
narrow biased, partially correct composition, and wrong composition.

## Generator–realization separation

Generate trajectories from random constrained splines, random basis mixtures,
or random ODEs. Labels are evaluated on the realized target trajectory using
constraint checks. Candidate realization routines must not reuse the generator
family, preventing a power-law-to-power-law shortcut.

## Randomized data conditions

Support length, sampling density, noise, exposure, OOD distance, unit-level
heterogeneity, and identifiability vary independently. Each task is indexed by

```text
primitive composition × data condition × distance × knowledge quality
```

## Candidate profile and frontier

For every candidate record structural coverage, conditional sharpness, marginal
sharpness under composition, logical specificity, incremental utility, harm
rate, calibration sensitivity, and distance stability. Conditional sharpness
freezes its reference ensemble: generator rule, ensemble size, prefix
conditioning likelihood, and candidate-prior independence. A later robustness
check compares spline and basis-mixture ensembles for ranking stability.
Do not force one best-prior score. Report the **Prior Quality Frontier**:
coverage-preserving candidates that are sharp, useful, and low harm.

## Benchmark splits

1. Seen primitives, unseen parameters.
2. Seen primitives, held-out compositions.
3. Held-out primitive/mechanism (open-world prior OOD).
4. Held-out generator realization for a fixed structure (e.g. ODE test versus
   spline/basis development), to detect generator-artifact learning.

## Null and interaction cases

Include null/no-useful-prior tasks where the vocabulary has no informative safe
constraint; correct behavior is abstention or a weak prior. For conjunctions,
report marginal information such as `ΔS(B|A)=S(A∧B)-S(A)` and the matching
deployment-dependent utility difference. This distinguishes redundancy,
synergy, and harmful interactions.

## Future proposer evaluation

Only after the grammar benchmark is established compare handcrafted grammar,
random generator, learned proposer, LLM, and LLM+RAG. Proposal engines are
evaluated on candidate recall, coverage, sharpness, calibration, harm,
diversity, and abstention—not generator-label accuracy alone.

## Operational definitions required before execution

Truth has two labels: phenomenological (realized target satisfies a constraint)
and mechanistic (generator contains its mechanism). Regime change records both.
Asymptote stores latent generator truth and a finite-horizon operational label
based on predeclared late-domain decline in distance-to-limit and slope.

Freeze a compatible/conditional/incompatible composition table and each
constraint's global versus segment-local scope. Conditional sharpness freezes
the reference ensemble generator, size, prefix-likelihood conditioning, and
candidate independence; its robustness endpoint is rank correlation between
spline-ensemble and basis-mixture-ensemble sharpness rankings. Utility is
explicitly `U(prior, realization engine, baseline, distance)` and headline
results must repeat under spline and constrained-neural realization engines.

Null tasks report unnecessary proposal rate, harmful proposal rate, abstention
coverage, and missed-useful-prior rate. Before full execution, a 30–50 task per
primitive sanity suite at zero noise/dense observations/near OOD must verify
coverage, sharpness ordering, biased-narrow behavior, conjunction logic, and
cross-generator label agreement.
