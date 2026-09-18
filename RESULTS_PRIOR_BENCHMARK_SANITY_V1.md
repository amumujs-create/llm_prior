# Prior Primitive–Composition Benchmark v1 — Core Sanity Result

**Status:** failed; full benchmark remains blocked.

## Purpose

This run tests whether the frozen generator–checker–sharpness machinery measures
the intended prior objects. It is not a predictive-performance experiment.
There are 840 tasks: 7 primitives × 3 generator realizations × 40 paired
specifications. Each sharpness sampler uses `M=4096` continuations.

## Results

| Gate | Result | Decision |
|---|---:|---|
| Generator/checker recovery, overall and per primitive | 1.000 | pass |
| Broad < medium < narrow correct ordering | .514 spline / .512 basis | **fail** |
| Narrow-biased: higher sharpness and lower coverage | 1.000 / 1.000 | pass |
| Conjunction monotonicity violations | 0 / 0 | pass |
| Cross-sampler sharpness rank correlation | .987 | pass |

Median ESS is 175.4 (`Q_spline`) and 176.0 (`Q_basis`). The `ESS<100` warning
rate is 11.2% and 12.1%, respectively.

## Diagnosis

The failed gate is a construct mismatch, not a utility result. At zero noise
with dense prefix observations, the weighted continuation ensemble becomes so
concentrated that broad- and medium-correct intervals often both receive
probability near one. Their median sharpness is approximately `.0001`; narrow
is only `.0001–.0002`. Strict ordering therefore fails even though all three
correct intervals preserve the true continuation. This is valid behavior for
`S(P|D_obs)`: logical specificity need not add information already supplied by
the prefix.

The failure is primitive-dependent. Strict nested ordering is 1.0 for
direction, curvature, and asymptote; 0 for bound, inflection, and turning; and
about .59–.60 for regime. This means a single zero-noise dense-prefix sanity
condition cannot validate specificity across primitives with different
identifiability geometry.

## Decision

Do not run full v1 and do not lower the `.95` threshold. Protocol v1.1 instead
separates exact nondecreasing logical nesting from primitive-specific empirical
resolvability. Equality is valid. Saturation becomes a reported signal of low
incremental information, not automatically an estimator failure. Structural-
null and informational-null validation remains outstanding before full v1.

## Artifacts

- `experiments/prior_benchmark_sanity_v1.py`
- `results/prior_benchmark_sanity_v1/summary.json`
- `results/prior_benchmark_sanity_v1/task_metrics.csv`
- `figures/fig24_prior_benchmark_sanity.png`
