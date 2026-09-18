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
| Bound/asymptote | finite limiting region / one-sided bound | bound type → bound interval → bound + approach-rate range |

A prior is a set of constraints, never a particular power-law or exponential
formula. Formula classes are possible realizations only.

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

For every candidate record structural coverage, conditional sharpness,
incremental utility, harm rate, calibration sensitivity, and distance stability.
Do not force one best-prior score. Report the **Prior Quality Frontier**:
coverage-preserving candidates that are sharp, useful, and low harm.

## Benchmark splits

1. Seen primitives, unseen parameters.
2. Seen primitives, held-out compositions.
3. Held-out primitive/mechanism (open-world prior OOD).

## Future proposer evaluation

Only after the grammar benchmark is established compare handcrafted grammar,
random generator, learned proposer, LLM, and LLM+RAG. Proposal engines are
evaluated on candidate recall, coverage, sharpness, calibration, harm,
diversity, and abstention—not generator-label accuracy alone.
