# E16-B Post-hoc Mean–Spread Decomposition v1

**Status: post-hoc diagnostic analysis.** This analysis uses the already
opened and frozen E16-B confirmatory corpus. It is not a new confirmatory
experiment and cannot alter the E16-B primary disposition.

## Fixed inputs and prohibited changes

Reuse exactly the frozen 956-row confirmatory targets, 956-by-405 normalized
component means, uniform and validation-weighted vectors, and
\(\sigma_{ref}=0.26536872271489265\). No model is refit and no candidate,
weight, component scale, split, or guard use is changed.

For policy weight vector \(w\), let \(m(x)=\sum_hw_hf_h(x)\) and
\(v(x)=\sum_hw_h[f_h(x)-m(x)]^2\). For
\(\rho\in\{0,0.25,0.5,0.75,1\}\), define
\[
f_{h,\rho}(x)=m(x)+\rho[f_h(x)-m(x)],\quad
F_\rho=\sum_hw_h\mathcal N(f_{h,\rho}(x),\sigma_{ref}^2),
\]
and the moment-matched Gaussian
\[
G_\rho=\mathcal N\{m(x),\sigma_{ref}^2+\rho^2v(x)\}.
\]

## Primary post-hoc comparison and decomposition

The first interpreted contrast is weighted retention,
\(R(F_{W,1})-R(F_{W,0})\). Its variance and shape path decomposition is
\[
R(F_{W,1})-R(F_{W,0})=
[R(G_{W,1})-R(F_{W,0})]+[R(F_{W,1})-R(G_{W,1})].
\]

For the uniform-to-weighted recovery, report the exact score-path terms
\[
L=R(F_{W,0})-R(F_{U,0}),
\]
\[
V=[R(G_{W,1})-R(F_{W,0})]-[R(G_{U,1})-R(F_{U,0})],
\]
\[
S=[R(F_{W,1})-R(G_{W,1})]-[R(F_{U,1})-R(G_{U,1})],
\]
so \(R(F_{W,1})-R(F_{U,1})=L+V+S\).

## Bootstrap and integrity checks

Use the same 956-row indices jointly across every policy and term for 5,000
PCG64 (`20260924`) bootstrap replicates. Report each term's own percentile
95% interval using linear quantiles. These are empirical-row resampling
intervals, not plant-population intervals.

Require normalized-scale tolerance \(10^{-12}\) for: mean preservation;
total-variance matching; \(F_1\) reproduction of frozen weighted/uniform
CRPS and their original difference; \(F_0\) equality to its single Gaussian;
and both row-level and bootstrap-level decomposition identities. Middle
\(\rho\) values are descriptive response curves only; no best \(\rho\) is
selected.
