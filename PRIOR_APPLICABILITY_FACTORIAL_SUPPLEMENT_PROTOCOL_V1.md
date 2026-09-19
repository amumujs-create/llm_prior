# E8 Supplement v1 — A2 Absolute-Horizon and C2 Bias-Symmetry Checks

## Purpose

These are interpretation controls for E8, not new research axes. A2 separates
observed-support length from the changing *absolute* forecast gap in E8-A. C2
tests whether the biased-specific result depends on the positive perturbation
direction rather than narrow miscalibration itself.

## Shared frozen setting

Seven singleton primitives, three data generators, two realization engines,
and 20 deterministic draws per primitive × generator × cell (seed base `82000`)
use the same core, utility rule, and practical thresholds as E8. Safety stays
engine-conditioned; robust unsafe means harmful in either engine. All rows are
reported separately by engine and with a robust task-level aggregate.

## A2 — support × noise at fixed absolute horizon

- Support fraction: `.35, .525, .70`.
- Noise ratio: `.001, .01, .05`.
- The **absolute future gap** is fixed at `.21` in progression coordinates;
  query endpoint is `support + .21`, rather than `support × (1+.40)`.
- Held fixed: `n=72`, exposure `.55`, effect strength `.55`, heterogeneity
  `.10`.

Thus any support result still includes the changing observed prefix position,
but it no longer arises mechanically from a different absolute forecast gap.

## C2 — signed bias symmetry

- OOD distance: `.10, .40, .80`.
- Candidate tiers: true-full, signed narrow bias `-`, signed narrow bias `+`.
- Held fixed: support `.525`, `n=72`, noise `.01`, exposure `.55`, effect
  strength `.55`, heterogeneity `.10`.
- Positive bias is the frozen full-v1 perturbation: `tau + .20`, rate `×1.5`,
  bound `+.20`. Negative bias is its parameter-space mirror: `tau - .20`,
  rate `×.5`, bound `-.20`; rate is floored at `.05` and tau is clipped to
  `[0,1]` before realization.

The two signed biases are scored on the same latent task. This does not claim
all physical priors have symmetric parameter semantics; it asks whether the
observed failure is one-sided within this frozen benchmark realization.

## Outputs

Primary: engine-conditioned harmful rate and robust-unsafe rate, each with
5,000 within-stratum bootstrap intervals. Secondary: raw utility, beneficial
rate, catastrophic-harm rate, Coverage, sharpness, and ESS. Neither A2 nor C2
trains a critic or changes the locked E8 conclusions.
