# E16-B CCPP Candidate-Grid D0 Contract v1

## Status

**FROZEN before any target column is read.** D0 asks only whether frozen X
geometry can construct a stable set of distinct, prior-consistent candidate
continuations. It must not load the target, calculate a target scale, fit a
model, calculate a loss, create MAP/weights/ESS, or predict performance.

## Deferred target-scale convention

After D0 and the capacity contract pass, later train-only target processing is

\[
R_y=IQR(PE_{train}),\qquad \tilde y=(PE-\operatorname{median}(PE_{train}))/R_y.
\]

This contract freezes only the unit convention: \(a,s,c,\gamma\) use
train-target-IQR units. D0 neither reads nor calculates \(R_y\). Positive
scaling preserves conditional AT non-increase.

## Parameterization and reference measure

\[
s=-a,\qquad c=ar_c,\qquad \gamma_j=ar_j,
\]

\[
\tilde T_h(u,z)=a[-u+r_cu^2+u(r_Vz_V+r_{AP}z_{AP}+r_{RH}z_{RH})].
\]

Here \(a\) is decrease magnitude, \(r_c\) is curvature shape, and
\((r_V,r_{AP},r_{RH})\) are interaction shapes. D0 computes from canonical
X only:

\[
U_-=|\min_i u_i|,\quad U_+=\max_i u_i,\quad
Z_*=\max_i(|z_{V,i}|+|z_{AP,i}|+|z_{RH,i}|).
\]

Derivative budgets are frozen at \(b_c=0.50\), \(b_\gamma=0.25\), and
\(b_{margin}=0.25\). Define

\[
r_c^-={0.25}/{U_-},\quad r_c^+={0.25}/{U_+},\quad r_\gamma={0.25}/{Z_*}.
\]

The grid is

\[
a\in\{0.1,0.3,0.5,0.7,0.9\},\quad
r_c\in\{-r_c^-,0,+r_c^+\},\quad r_j\in\{-r_\gamma,0,+r_\gamma\}.
\]

Candidate enumeration is lexicographic in that displayed order: amplitude,
curvature, V interaction, AP interaction, then RH interaction. It gives
\(K=5\times3^4=405\) candidates.

This is an operational **reference measure**, not an epistemic claim that
true slope magnitudes are uniformly distributed. Each amplitude midpoint node
has mass \(1/5\) and each shape level has mass \(1/3\), so every candidate
has mass \(1/405\). `specification_uniform_ensemble` is exactly the
expectation under this frozen discrete measure. Uniformity is relative to the
frozen \((a,r_c,r_V,r_{AP},r_{RH})\) parameterization and is not claimed to
be reparameterization-invariant.

## Monotonicity by construction

\[
\partial\tilde T_h/\partial u=a[-1+2r_cu+r_Vz_V+r_{AP}z_{AP}+r_{RH}z_{RH}].
\]

Across all canonical rows and observed AT endpoints, positive curvature can
contribute at most 0.50 and interactions at most 0.25. Hence the bracket is
at most \(-0.25\). D0 confirms this empirically over every canonical X row;
it does not filter candidates after construction. Tolerance is \(\epsilon=10^{-12}\).

## Required D0 audits

The D0 script reads only `AT,V,AP,RH` and must verify:

1. source workbook and frozen split-membership SHA-256 values replay;
2. finite positive \(U_-,U_+,Z_*,r_c^-,r_c^+,r_\gamma\);
3. exactly 405 unique parameter tuples, with 81 candidates per amplitude;
4. deterministic candidate-table SHA-256 on replay;
5. finite continuations and empirical-scope monotonicity for all candidates;
6. future-shell design rank 5 for \(G=[u,u^2,uz_V,uz_{AP},uz_{RH}]\); and
7. pairwise continuation distinctness on \(\mathcal S_X=\{AT>q_{85}=27.96\}\).

For pairwise \(h\ne h'\),

\[
d(h,h')=\sqrt{|\mathcal S_X|^{-1}\sum_{i\in\mathcal S_X}
[\tilde T_h(u_i,z_i)-\tilde T_{h'}(u_i,z_i)]^2}.
\]

D0 records pair count, min, q05, median, q95, max, and the count with
\(d\le10^{-10}\). PASS requires rank 5 and minimum pairwise distance strictly
above \(10^{-10}\). The raw distance matrix is not persisted. A failure is a
v1 implementation failure and does not authorize performance-driven grid
revision.

## Next gate

Only after D0 PASS may a capacity contract open train targets. It must account
for candidate-specific nuisance compensation before validation targets are
opened; realized post-fit candidate prediction collapse is then a stop audit,
not a reason to alter this grid.
