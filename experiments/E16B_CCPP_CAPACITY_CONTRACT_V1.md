# E16-B CCPP Capacity Contract v1

## Status and data-access sequence

**FROZEN before opening train targets.** This contract authorizes the first
target use only after it is frozen:

\[
PE_{train}\rightarrow\text{capacity and realized-distinctness only},\quad
PE_{validation}\rightarrow\text{candidate scoring only},\quad
PE_{test}\rightarrow\text{final scoring only}.
\]

Guard and confirmatory targets remain sealed throughout this capacity stage.

## Train-only target normalization

On the frozen train partition only, calculate once:

\[
m_y=\operatorname{median}(PE_{train}),\qquad R_y=IQR(PE_{train}),\qquad
\tilde y=(PE-m_y)/R_y.
\]

Require finite \(R_y>0\). The resulting values and their train-index source
are frozen in the train-capacity artifact; they are never recomputed from
validation, guard, test, or an enlarged training set.

## Common 10-term nuisance family

Every frozen D0 candidate \(h\) uses the same background basis

\[
B_\eta(z)=\beta_0+\sum_j\beta_jz_j+\sum_j\beta_{jj}z_j^2+
\sum_{j<k}\beta_{jk}z_jz_k,
\]

for \(j,k\in\{V,AP,RH\}\). The fixed 10 columns are intercept, three linear
terms, three squares, and three pairwise products, in that order. For each
candidate,

\[
\tilde y_i-\tilde T_h(u_i,z_i)=B_{\eta_h}(z_i)+\epsilon_i.
\]

Candidate nuisance coefficients may differ, but basis, train rows, target
scale, solver, folds, and regularization are exactly shared.

## Shared train-only ridge selection

The intercept is unpenalized. For the remaining nine columns, the ridge
objective is

\[
n^{-1}\|r-B\beta\|_2^2+\lambda\|\beta_{-0}\|_2^2.
\]

The frozen grid is \(\lambda\in\{10^{-6},10^{-5},\ldots,10^2\}\). Folds are
defined by zero-based canonical Sheet1 train-row index modulo 5. Their sizes
are `1320, 1358, 1332, 1356, 1333`, and the SHA-256 over big-endian uint32
index plus uint8 fold pairs is

`41607f07db26c966c1525ad1ae37b68c5a72a2c20017d0b293bf9ae01d37e1b6`.

For each lambda, compute every candidate's five-fold train-only CV MSE and
select one common value:

\[
\lambda_{spec}=\arg\min_\lambda\frac1{405}\sum_{h=1}^{405}CV-MSE_h(\lambda).
\]

When values are tied within relative tolerance \(10^{-12}\), choose the
largest \(\lambda\). No candidate receives a separate ridge value.

## Frozen working-likelihood scale

The later validation weights use the Gaussian working likelihood

\[
\ell_h^{val}=SSE_h^{val}/(2\sigma_{ref}^2),\qquad
\sigma_{ref}=\operatorname{median}_h RMSE_{h}^{OOF,train}.
\]

This scale is calculated only from train out-of-fold predictions after
\(\lambda_{spec}\) is fixed. The weights are operational evidence weights
under a frozen Gaussian working likelihood, not calibrated Bayesian posterior
probabilities. There is no evidence temperature. Entropy and ESS will be
reported later but never used to alter weighting.

## Post-fit candidate-realization audit

After full-train fitting at \(\lambda_{spec}\), generate each candidate's
prediction vector on validation plus guard plus confirmatory **X locations**.
No target from those partitions may be loaded. Record pairwise RMS distances,
minimum/q05/median/q95/maximum, exact-equivalent count using \(10^{-10}\),
the centered prediction-matrix numerical rank, singular values, and condition
diagnostics.

If any pair has RMS distance at or below \(10^{-10}\), record
`E16-B v1 implementation realization failure` and STOP. A merely small but
nonzero distance is recorded without altering the frozen D0 grid.

## Separate incremental-value block

`free_baseline`, `hard_sign_constraint`, and `soft_sign_constraint` are not
implemented in this stage. Their later common design has the same ten
nuisance columns plus \([u,u^2,uz_V,uz_{AP},uz_{RH}]\), for 15 coefficients.
They will share target transform, rows, folds, ridge grid, and solver; only
the derivative treatment differs. Their contrasts remain secondary and are
not substitutes for B1/B2.

## Capacity-stage pass criteria

PASS requires exact D0 candidate-table replay, positive finite train IQR,
fold-hash replay, finite shared-ridge fit, finite positive \(\sigma_{ref}\),
and no realized exact-equivalent pair. Only then may validation targets be
opened to select MAP and frozen Gaussian working-likelihood weights.
