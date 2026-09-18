# Frozen protocol — E5 Prior Calibration × Specificity Stress Test v1

**Status:** design frozen; not yet executed  
**Purpose:** separate prior specificity from calibration accuracy.

## Question

When the structural family is correct, how much realization-knowledge error can
a more specific prior tolerate before a broader constraint is safer or more
useful?

## Fixed environment

Retain the three synthetic families, observed support `t <= .60`, inner fit
`t <= .45`, pseudo-OOD `.45 < t <= .60`, and clean D1/D2/D3 evaluation bands.
Use low/mid/high within-family observability, noise `.005/.015/.030`, and 100
draws per cell. Far-OOD D3 is primary.

## Knowledge conditions

For each correct structural family, supply realization constraints at fixed
specificity but independently vary their calibration:

| ID | specificity | calibration |
|---|---|---|
| K0 | family only | no realization constraint |
| K1 | broad interval | centered on truth |
| K2 | medium interval | centered on truth |
| K3 | narrow interval | centered on truth |
| K4 | narrow interval | mildly biased center |
| K5 | narrow interval | strongly biased center |

For onset fields, broad/medium/narrow half-widths are `.20/.10/.03` in
normalized time. Mild/strong onset-center biases are `+.05/+ .15`. For scale
and shape fields (and bound lower/rate fields), the matching half-widths are
`30%/15%/5%` of the true parameter and mild/strong center biases are
`+10%/+30%`. Bounds are clipped to valid generator ranges. All interval bounds
are fixed before seeing outcomes.

## Primary endpoint and planned figure

`Utility = RMSE(family-only) - RMSE(Ki)` at D3. Plot utility against normalized
calibration error with separate narrow/broad lines. Estimate the cross-over
error `e*` where narrow ceases to outperform broad, with bootstrap uncertainty.

## Selection and admission analyses

MSE and predictive BIC are compared as pseudo-OOD selectors; derivative-only
metrics are not repeated because E1 rejected them as standalone selectors.

Admission-v2 must be evaluated with its **frozen confirmation-time
preprocessing, coefficients, family encoding, and .50 threshold**. Before E5
runs, the frozen classifier artifact must be exported from the confirmation
implementation; re-training on E5 is prohibited. Its target is harmful
miscalibrated knowledge (`Utility < 0`), not family truth.

## Guardrails

- Accurate narrow external constraints are allowed to help at low observability;
  this is the E3 result, not a failure.
- “Specificity is risky” may be claimed only if narrow versus broad crosses over
  as calibration degrades, not merely because a wrong family is harmful.
- E5 evaluates synthetic calibration error, not RAG retrieval quality.
