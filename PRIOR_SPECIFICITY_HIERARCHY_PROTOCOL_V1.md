# Frozen protocol — Prior Specificity Hierarchy Experiment v1

**Status:** frozen before execution  
**Experiment ID:** `prior_specificity_hierarchy_v1`

## Question

Does the useful specificity of a structural prior depend on how much relevant
evidence has been observed, rather than being a fixed “more prior is better”
rule?

## Fixed environment

The existing three generators and `t <= .60` support remain unchanged. Four
within-family exposure levels are used: regime-change/curvature onset values
`.59,.48,.32,.15`, and asymptotic-bound rates `.35,1.50,3.50,5.00`. Observed
noise is fixed at `.015`; each cell has 100 independent draws (1,200 tasks).
Evaluation uses clean D1/D2/D3 bands; D3 is primary.

## Prior hierarchy

The levels are functions of each generator rather than a claim that levels
carry identical absolute information across families.

| Level | Regime / curvature | Asymptotic bound |
|---|---|---|
| L0 | unconstrained local affine | unconstrained local affine |
| L1 | decreasing affine direction | decreasing affine direction |
| L2 | direction + generic quadratic curvature | direction + generic convex slope-decay quadratic |
| L3 | matching structural family, all parameters prefix-fit | exponential-bound family, parameters prefix-fit |
| L4 | L3 plus ±10% intervals around generator realization fields | L3 plus ±10% intervals for bound/rate |

L4 is an *information upper-bound condition*, not a realistic RAG output. It
asks whether a constrained realization can be useful when external knowledge
is supplied as an interval rather than an exact fixed parameter.

## Primary quantities

For every level and exposure condition, report D3 RMSE. Report two prespecified
contrasts:

- low-evidence over-specificity cost: `RMSE(L4) - RMSE(L1)`;
- high-evidence under-specificity cost: `RMSE(L1) - RMSE(L4)`.

The test supports evidence-conditioned specificity only if over-specificity
cost is positive at low evidence and/or under-specificity cost is positive at
high evidence. It is valid for either contrast to be absent in a family.

## Guardrails

- L4 receives realization intervals by design, so its score measures value of
  external constraints, not a deployable data-only method.
- Do not compare numeric exposure values across families as equal information.
- A nonmonotonic hierarchy curve is an admissible result; “more specific” is
  not presumed better in advance.
