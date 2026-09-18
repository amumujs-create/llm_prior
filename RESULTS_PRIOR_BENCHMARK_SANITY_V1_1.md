# Prior Benchmark v1.1 — Measurement-Resolvability Result

**Status:** logical gate passed; structural-null gate not yet run; full v1 stays
blocked.

## Main result

Across 1,680 measurements (`7 primitives × 3 generators × 40 × 2 samplers`),
logical nesting violations were zero. Under the frozen data-limited condition,
effective conditional specificity remained strongly primitive-dependent.

| Primitive | Median ΔS narrow−broad, spline/basis | Saturation rate | Informational-null rate |
|---|---:|---:|---:|
| Direction | 1.724 / 1.721 | 0 / 0 | 0 / 0 |
| Curvature | 1.758 / 1.755 | 0 / 0 | 0 / 0 |
| Inflection | .003 / .004 | .992 / .967 | 1 / 1 |
| Turning point | .004 / .004 | .992 / .992 | 1 / 1 |
| Regime change | 1.330 / 1.195 | 0 / 0 | 0 / 0 |
| Bound | .059 / .058 | 0 / 0 | 1 / 1 |
| Asymptote | .396 / .400 | 0 / 0 | 0 / 0 |

Saturation means `S_narrow<.01`; informational null means every tested
coverage-preserving specificity remains below `.10` in both samplers.

## Interpretation

`Logical specificity != effective conditional specificity.` Direction,
curvature, regime, and asymptote constraints remove substantial continuation
mass when the prefix is data-limited. Inflection and turning-point realization
intervals remove almost none under the current continuation ensemble, despite
being logically narrower. Bound occupies an intermediate case: its ladder is
detectably ordered but provides less than `.10` nat of information.

Thus saturation is not automatically a measurement defect. It can identify a
true prior whose added specificity is redundant given the data and reference
continuation geometry. This directly extends the earlier E4 finding that truth
does not imply incremental information.

## Decision

The old strict-ordering gate is retired only in protocol v1.1, not retroactively
declared passed. Logical nondecrease is the validity gate; resolvability and
informational-null rates are anatomy outputs. Full v1 remains blocked because
the independently defined structural-null generator/checker gate has not yet
been executed.

## Artifacts

- `PRIOR_BENCHMARK_SANITY_PROTOCOL_V1_1.md`
- `experiments/prior_benchmark_resolvability_sanity_v1_1.py`
- `results/prior_benchmark_resolvability_sanity_v1_1/summary.json`
- `results/prior_benchmark_resolvability_sanity_v1_1/task_metrics.csv`
- `figures/fig25_resolvability_sanity_v1_1.png`

