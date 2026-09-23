# E15-D0 v1.1 implementation addendum

## Status

This addendum freezes numerical conventions required to execute the discarded,
outcome-free D0 calibration. It supplements, and does not amend, the frozen
semantic and factorised-D2 contracts.

## Public observation and prefixes

The public observation grid is exactly

\[
x_n=n/100,\qquad n=0,\ldots,100.
\]

It contains 101 points including both endpoints. A prefix at exposure
\(x_e\) contains exactly those grid points satisfying \(x_n\le x_e\).

## Prefix likelihood and evidence summaries

The likelihood is Gaussian with known \(\sigma=\rho R_0=\rho\). Omitting
only candidate-common constants, the runner uses the **sum** negative
log-likelihood

\[
\ell_{ij}=\frac{1}{2\sigma^2}\sum_{x_n\le x_e}
 [y_n-f_{ij}(x_n)]^2.
\]

It never substitutes a mean NLL. Entropy uses natural logarithms. All 5/50/95
percentiles use `numpy.quantile(..., method="linear")`.

## Exact continuation distinctness

Distinctness is evaluated on \((x_J,x_{\rm far}]\), not on an arbitrary
evaluation grid. For coefficient differences \(\Delta\kappa,\Delta\lambda\),
the normalized squared continuous RMS is exactly

\[
 d^2=\Delta\kappa^2\frac{x_{\rm far}^5-x_J^5}
 {5(x_{\rm far}-x_J)}
 +2\Delta\kappa\Delta\lambda\frac{x_{\rm far}^9-x_J^9}
 {9(x_{\rm far}-x_J)}
 +\Delta\lambda^2\frac{x_{\rm far}^{13}-x_J^{13}}
 {13(x_{\rm far}-x_J)}.
\]

Because \(R_0=1\), \(d=\sqrt{d^2}\). An edge requires \(d\ge .01\),
and the audit requires an exact size-four clique rather than a greedy count.

## Random-number generation and reuse

For task \(r\), the seed is the first eight **digest bytes** of

`SHA256("e15d-d0-v1.1-discarded:task:" + str(r))`,

interpreted as an unsigned big-endian integer and reduced modulo \(2^{63}\).
The only generator is

`numpy.random.Generator(numpy.random.PCG64(seed))`.

Its draw order is frozen:

1. `u_kappa = rng.random()`;
2. `u_lambda = rng.random()`;
3. 101 draws from `rng.standard_normal()` for one master noise path.

No candidate may call the RNG. Supports transform the same uniforms and every
candidate reuses the same master path; L/S/J are nested prefixes of one noisy
trajectory.

## Execution boundary

The runner contains no policy-prediction or outcome computation. It may only
construct coefficient continuations for the continuous-RMS clique audit and
calculate prefix likelihood, posterior weights, marginal entropies, and
permitted aggregate evidence summaries. Formal D0 cannot run until its runtime
configuration is marked `FROZEN`.
