# E15-B — Shape-prior utilization under finite scope uncertainty

## Question

Given the same directional knowledge object, how should a shape prior be used
when its future validity horizon is uncertain?

E15-B holds the shape content fixed and changes only utilization. It is not a
second event-onset experiment: the latent uncertainty is the horizon through
which a directional constraint remains valid.

## Representative prior

`K = {df/dt >= 0 on a future interval of uncertain endpoint h}`.

The clean truth is nondecreasing through a task-specific `h*` and may change
afterward. The supplied knowledge object describes direction but not an exact,
globally valid endpoint. Thus a globally hard monotonic constraint can become
invalid after `h*`, even when it is valid on its declared local scope.

This directly tests the E10/E13 anatomy distinction:

`validity != scope`.

## Held fixed

- One frozen synthetic shape family and the same noisy prefix per latent task.
- Same task seeds, forecast grid, model capacity, optimizer budget, and
  validation-free fitting rule across every utilization policy.
- Same stated direction knowledge and same admissible horizon support `H`.
- No policy may see future labels, `h*`, or any post-prefix scope oracle.
- Scope is evaluated on clean truth after prediction; it is never reused for
  policy selection.

## Candidate utilization policies

| Policy | Treatment of the same directional knowledge |
|---|---|
| `free_baseline` | No supplied directional constraint. |
| `hard_global` | Enforces nondecreasing continuation across the whole forecast horizon. |
| `hard_local_MAP` | Enforces the constraint only through one selected horizon in `H`. |
| `soft_global` | Applies a frozen violation penalty across the whole horizon. |
| `slack_distribution` | Marginalizes over a fixed distribution of permissible directional slack. |
| `scope_hypothesis_ensemble` | Retains multiple horizon-constrained continuations uniformly over `H`. |
| `evidence_weighted_scope_mixture` | Retains the same horizon hypotheses and reweights them only with prefix evidence. |

The primary decomposition parallels E15-A but concerns scope rather than onset:

- `D1 = evidence_weighted_scope_mixture - hard_local_MAP`: retention of
  multiple admissible horizons after the same horizon likelihood is used.
- `D2 = evidence_weighted_scope_mixture - scope_hypothesis_ensemble`:
  likelihood weighting while retaining scope uncertainty.

`hard_global` is a predeclared stress condition, not the comparator for the
primary scope-uncertainty estimand: it changes the asserted scope by extending
the directional claim beyond the supplied support.

## Factors

1. **Scope knowledge:** exact local horizon, narrow valid interval, broad valid
   interval, endpoint-unspecified support, covered biased interval, uncovered
   biased interval.
2. **Prefix exposure / directional evidence:** low, medium, high; a continuous
   prefix-derived scope-evidence descriptor is reported separately.
3. **True scope:** task-specific `h*`, evaluated only after predictions have
   been fixed. It determines coverage and scope violation, not policy input.

## Predeclared hypotheses

1. With broad scope uncertainty and weak prefix evidence, retaining multiple
   locally constrained continuations will reduce far-OOD error relative to early
   single-horizon commitment.
2. When evidence identifies the viable scope, likelihood weighting will become
   more useful and retention's advantage will contract.
3. When the supplied directional knowledge has uncertain or finite scope,
   globally hard enforcement can incur post-scope error even when the direction
   was locally valid.

## Primary outcomes

- Far-OOD NRMSE and CRPS on a common post-prefix window.
- Distance-wise degradation.
- Scope violation rate and excess post-scope error.
- Worst-valid and Worst-all error, retaining uncovered scope supports as a
  validity-failure stratum rather than hiding them.
- Scope-hypothesis entropy, truth-neighborhood scope mass, and wrong scope
  collapse/commitment for covered supports.

## Required A0 calibration

Before a confirmatory run, discarded-seed E15-B0 must freeze the shape family,
noise ratio, common far-OOD horizon, scope-support geometry, numerical
constraint solver, quota, and maximum attempts without inspecting directional
policy winners or contrast signs.

## Interpretation boundary

E15-B can establish a controlled utilization result for the frozen
direction-plus-finite-scope family only. It does not establish a universal rule
for curvature, bounds, or mechanistic invariants; those require separate
representative studies.
