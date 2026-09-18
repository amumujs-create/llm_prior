# Frozen E6-v1 — Distance × Data-Driven Trust

Prior quality is fixed to a calibrated, correct family-only condition; E6-v1
tests residual trust only. Distance is `d=(x-.60)/.60`. Far-OOD labels are
evaluation-only. Inner is `t<=.45`; pseudo-OOD is `.45<t<=.60`.

Methods: prior only; fixed prior+residual; fixed `exp(-2d)` decay; evidence-
aware decay. The evidence-aware rule is fixed before results: apply `exp(-2d)`
only if both family-prior pseudo-OOD MSE beats affine pseudo-OOD MSE and
residual pseudo-OOD MSE beats prior pseudo-OOD MSE; otherwise use prior-only.
No far-OOD label enters this rule.

Residuals are cubic ridge spline and an 8-unit small neural network. Distances
are `.05,.10,.20,.30,.40,.60,.80,1.00`. Record DeltaR(d), first nonpositive
distance d* (right-censored if none through 1.0), integrated OOD risk, 2x-prior
catastrophic harm, and pseudo-OOD near-gain versus far-collapse.
