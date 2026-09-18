# Frozen protocol — Model Capacity / Residual Stress Test v1

**Status:** frozen after E1, before execution  
**Experiment ID:** `residual_capacity_stress_v1`

## Question

Can an incompatible structural prior win pseudo-OOD MSE because a flexible
data-driven residual corrects it near the support boundary, even when that
choice has larger far-OOD regret?

## Inherited fixed contract

This protocol reuses E1's three generators, observed support (`t <= .60`),
inner/pseudo split (`.45`), D1/D2/D3 bands, noise levels, observability levels,
100 draws per cell, candidates, and compatibility labels. The only new factor is
residual capacity. Thus it contains 2,700 base trajectories × 3 capacity ratios
= 8,100 capacity-stress cases.

Every candidate is realized as `prediction = structural_prior + residual`.
The residual is a ridge-regularized polynomial basis in `t`; all candidates use
the identical architecture and regularization, differing only in number of
basis terms. This is a stress test, not a claim that polynomial residuals are
the preferred deployment architecture.

## Capacity conditions

Compatible non-neutral candidates receive `q=4`. Neutral `P0` also receives
`q=4`. Incompatible candidates receive:

| condition | `q_incompatible` | ratio `q_incompatible / q_compatible` |
|---|---:|---:|
| matched | 4 | 1 |
| stress-2x | 8 | 2 |
| stress-4x | 16 | 4 |

The structural prior is fitted first, then residual coefficients are fitted to
training residuals only. No far-OOD labels enter fitting or selection.

## Selection rules

E1's prespecified handoff criterion was met, so selection compares:

- pseudo-OOD MSE;
- predictive BIC with effective parameter count equal to structural parameters
  plus residual basis count.

No threshold or score is tuned after seeing capacity results.

## Primary endpoint

At each ratio and each selector, report
`P(selector chooses incompatible candidate)` and D3 far-OOD selection regret.
The pre-registered visual is capacity ratio versus incompatible-selection rate.

Secondary mechanism records are residual-to-prior norm ratio on pseudo-OOD and
the rate at which the residual changes the structural prior's first-difference
direction. These distinguish “structurally right” from “residual overwrote it.”

## Interpretation guardrail

If MSE's incompatible-selection rate rises with capacity while BIC is more
stable, it is evidence that unconstrained near-support flexibility can mask
structural mismatch in this setup. If it does not rise, the proposed residual
masking mechanism is not supported and must remain a negative result.
