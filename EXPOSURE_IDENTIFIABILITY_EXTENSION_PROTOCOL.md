# Exposure / Identifiability Extension protocol v1

## Question

The oracle-decomposition development result established that seeing a structural
signal is not necessarily enough to realize it safely. This extension asks a
single pre-specified question for regime change and emergent curvature:

> With substantially longer post-onset exposure, does a generative-family oracle
> converge to the parameter oracle?

## Frozen design

- Families: regime change and emergent curvature only.
- Prefix remains noisy observations through `.60` (Gaussian SD `.015`); the clean
  tail after `.70` is evaluation-only.
- Observability levels are `.533, .60, .70, .80, .90`, corresponding to onset
  locations `.28, .24, .18, .12, .06`. The first level bridges directly to the
  prior decomposition; the other four are the new high-exposure extension.
- 250 newly drawn trajectories per family × level (2,500 tasks), random seed
  `20260924`. No draw or seed is shared with prior development or confirmation
  experiments.
- Methods and equations are unchanged from Oracle Decomposition v1: affine
  fallback; **generative-family oracle** (right family only, all parameters fit
  from prefix); **parameter oracle** (true onset, post-onset scale, exponent;
  initial rate fit from prefix); and full-information oracle.

## Primary endpoint and decision rule

For each family and observability level, compute the paired realization gap:

`G = RMSE(generative-family oracle) − RMSE(parameter oracle)`.

The primary diagnostic is mean `G` with a paired nonparametric bootstrap 95%
interval (2,000 resamples). Before looking at results, *practical convergence*
is defined as an upper 95% interval endpoint at most `.01` far-OOD RMSE. This is
a descriptive decision rule, not a claim of exact equality.

## Mechanism record

For successful generative-family fits, record onset absolute error, post-onset
scale relative error, exponent absolute error, and their normalized aggregate.
This separately tests whether increased exposure improves identification of the
realization parameters rather than merely improving a fitted curve by chance.

## Interpretation guardrails

- Convergence supports: with this generator and noise level, enough support can
  make family-only information operationally sufficient.
- Failure to converge supports: family identity remains insufficient at this
  support; it does **not** prove universal intrinsic insufficiency. External
  knowledge could still be required, or even longer support may be needed.
- No threshold, equation, feature, or method may be changed after reading this
  output. A follow-up must use a new version and new draws.
