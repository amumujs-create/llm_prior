# Admission-v2: observable, identifiable, useful

## Question

Can prefix-only evidence reduce admission of a **harmful** matched prior while
retaining useful-prior coverage? The label is tail utility, not observability:
`U = RMSE(linear fallback) - RMSE(matched prior)`. A prior is harmful iff `U < 0`.
True observability is used only to explain mechanism, never as a model feature.

## Frozen task grid

- Families: regime change, emergent curvature, asymptotic bound.
- Six observability levels per family. For the first two, this is onset `tau`;
  for asymptotic bound, it is dimensionless exposure `rate * boundary`.
- Noise SD: `.005, .010, .020, .035, .055`.
- Fifty independent parameter/noise seeds at each cell: `3 * 6 * 5 * 50 = 4,500`.
- Boundary `t_b=.60`; models see only `t <= .60`; clean `t > .70` is endpoint-only.
- Train seeds `0..34`; locked test seeds `35..49`. The v2 classifier threshold is
  fixed at probability `.50`; no test threshold selection is allowed.

## Prefix-only evidence vector

All quantities are candidate-specific and computed without tail data:

`e_k = [boundary slope change, slope decay, change BIC advantage, post-change support,
quadratic curvature z-score, asymptote proximity, fit stability, parameter precision,
covariance condition, v1 pseudo-OOD score, candidate identity]`.

`O_hat` is the model's estimated usefulness probability, not a substitute for
`O_true`. Admission is `A = 1[Pr(U>0 | e_k) >= .50]`.

## Models and comparisons

- **v1 baseline:** uniform rolling pseudo-OOD score `A_v1 > 0`.
- **v2:** standardized evidence vector plus a logistic regression (`C=1`,
  balanced classes, fixed random state 20260920), trained only on train seeds.
- **Fallback:** linear least squares; **matched prior:** correct generic family
  with unknown parameters fitted solely on the prefix.

## Primary test endpoints

On locked test seeds only report: false-admission rate `P(admit | U<0)`, coverage
`P(admit)`, conditional harm among admitted `P(U<0 | admit)`, and useful-prior
admission `P(admit | U>0)`. Plot coverage versus conditional harm risk across
descriptive thresholds. A v2 gain must not be described as confirmatory: the
mechanism and feature list were motivated by v1.
