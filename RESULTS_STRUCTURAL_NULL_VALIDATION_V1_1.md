# Structural-Null Validation v1.1

**Status:** passed. The last protocol-level sanity blocker for full benchmark
v1 is cleared.

## Frozen definition

Structural null uses only the out-of-grammar generator and frozen truth
checkers. It does not use utility or conditional sharpness. Target values are
normalized to the declared physical range `[-1,1]`; meaningful bound candidates
are fixed before generation at `±.75, ±.50, ±.25, 0` for both one-sided
directions. Endpoint or post-hoc bounds are prohibited.

## Result

| Generator | Accepted/requested | Total attempts | Exhausted | Violations |
|---|---:|---:|---:|---:|
| Spline | 40/40 | 42 | 0 | 0 |
| Basis | 40/40 | 50 | 0 | 0 |
| ODE-style | 40/40 | 41 | 0 | 0 |

Every accepted curve rejected global direction, global curvature, exactly-one
inflection, exactly-one turning point, mechanistic/phenomenological single
regime change, every registered meaningful bound, and latent/operational
asymptote. No utility- or sharpness-based relabeling occurred.

## Decision

The >=95% per-generator acceptance gate passed at 100%, with zero accepted-task
violations. Together with v1.1 logical nesting and the earlier generator/checker,
confidently-wrong, conjunction, and sampler-robustness gates, the protocol-level
sanity blockers are cleared. Full benchmark v1 may now be implemented and run
without removing inflection or turning-point primitives. Their conditional
information remains an anatomy outcome to map across data conditions.

## Artifacts

- `experiments/structural_null_validation_v1_1.py`
- `results/structural_null_validation_v1_1/summary.json`
- `results/structural_null_validation_v1_1/accepted_tasks.csv`
- `figures/fig26_structural_null_validation.png`

