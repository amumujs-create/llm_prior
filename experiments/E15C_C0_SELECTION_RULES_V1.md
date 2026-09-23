# E15-C0 predeclared selection rules v1

This contract completes the outcome-free selection rules for the E15-C0 numerical sweep.

## Residual-continuation distance

For two fixed residual-shape hypotheses `q_i` and `q_j`, compare their forecast predictions on the common far grid of `M` points:

\[
d_{ij}=
\frac{\sqrt{M^{-1}\sum_{m=1}^{M}[\hat y_{q_i}(t_m)-\hat y_{q_j}(t_m)]^2}}
{R_{\rm inv}}.
\]

They count as distinct residual continuations when

\[
d_{ij}\ge\delta_{\rm cont},\qquad \delta_{\rm cont}=0.01.
\]

The threshold is one percent of the invariant-only public reference scale. It is a construct-validity threshold and may not be tuned using policy outcomes.

The effective residual-continuation count is computed from this predeclared relation on the same common far grid used by all candidates. The C0 gate remains a median count of at least four.

## Residual-grid selection

Candidate grid spacings are `.05` and `.025` on the same closed `[0,1]` `q` domain.

> **Select the coarsest admissible residual grid.**

Thus `.05` is selected if it satisfies all continuation-distinctness, residual-evidence geometry, and numerical-stability gates. Use `.025` only if `.05` fails one or more such gates. This prevents an unnecessarily dense grid from changing mixture entropy merely through redundant representation.

## Noise selection

Candidate ratios are `rho in {.01, .025, .05, .10}`.

> **Select the largest admissible noise ratio.**

Admissibility requires the predeclared residual-evidence progression, adjacent-exposure overlap, non-saturation, continuation, and numerical-stability gates. It does not use policy RMSE, CRPS, contrast values, rankings, or winners.

## Deterministic response construction

Because

\[
g_q(x)=(1-q)x+qx^3,
\]

the corresponding invariant-filtered responses must be constructed as

\[
z_q(t)=(1-q)z_1(t)+qz_3(t),
\]

where `z1` and `z3` are computed once on the frozen common time grid. All candidate `q` responses are then exact linear combinations of those two stored basis responses; no per-`q` ODE solve or independent quadrature is permitted.

This rule removes candidate-specific numerical variation from residual evidence and continuation geometry.
