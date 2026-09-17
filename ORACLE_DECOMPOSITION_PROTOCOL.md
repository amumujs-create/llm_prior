# Oracle Decomposition protocol v1

## Question

Why can extrapolation fail even when the correct structural family is known?
Separate family knowledge from knowledge needed to realize the family outside
observed support.

## Frozen primary design

- Three families: regime change, emergent curvature, asymptotic bound.
- Seven observability levels × 100 independent draws per family (2,100 tasks).
- Prefix is noisy observations through `.60` (SD `.015`); clean tail after `.70`
  is evaluation only.
- **No prior:** affine least-squares fit.
- **Generative-family oracle:** correct family only; all parameters fitted from prefix.
- **Parameter oracle:** correct family plus realization-bottleneck information.
  Regime change and emergent curvature receive true onset, post-onset scale, and
  exponent; only the initial rate remains fitted. Asymptotic bound receives true
  lower limit; rate remains fitted.
- **Full-information oracle:** all actual generator parameters; predicts the clean
  trajectory directly.

## Expected diagnostic pattern

At low observability, family oracle may be worse than fallback while parameter
and full-information oracles retain low tail error. At high observability, the
family-oracle gap to parameter oracle should narrow. This diagnoses missing
realization information—not family misspecification—as the failure source.

## Auxiliary realization robustness

For emergent curvature, fit the same structural assumption with (1) power law,
(2) concavity-constrained piecewise-linear spline, and (3) a shallow constrained
ReLU-squared neural basis. The auxiliary result asks only whether low-observability
harm is restricted to one formula. It is not a model leaderboard.
