# E16-B CCPP Affine-Equivalence and CRPS Amendment v1

## Status and rationale

**FROZEN before validation targets are opened.** The capacity-stage candidate
predictors are affine in the raw specification coefficients
\(\theta=(s,c,\gamma_V,\gamma_{AP},\gamma_{RH})\): candidate continuation is
linear in \(\theta\), and the common fixed-ridge nuisance solution is affine
in the residual target. Consequently, for fixed weights,

\[
\sum_h w_h f_h(x)=f_{\sum_h w_h\theta_h}(x)
\]

under the same train-only fit rule. A uniform or weighted **point** prediction
therefore does not itself demonstrate retention of a predictive distribution.

This amendment does not change D0 candidates, the reference measure, capacity
rule, source, split, target-access sequence, or the point-prediction policies.
It corrects the primary estimand interpretation before validation evidence is
seen.

## Required affine-equivalence audit

Using train targets only, reconstruct all 405 full-train candidate fits at the
frozen \(\lambda_{spec}\). Let \(\bar\theta=405^{-1}\sum_h\theta_h\), fit the
single candidate defined by \(\bar\theta\) with the same nuisance basis and
ridge rule, and evaluate both it and the uniform point mean over every
canonical X row. Require

\[
\max_x\left|405^{-1}\sum_hf_h(x)-f_{\bar\theta}(x)\right|\le10^{-12}.
\]

The result is retained as a deterministic representation audit. It establishes
that NRMSE contrasts between uniform/weighted point means and MAP are
point-specification contrasts, not direct evidence of retained predictive
diversity.

## Predictive-distribution policies

The train-only frozen \(\sigma_{ref}=0.26536872271489265\) defines common
component uncertainty in normalized-target units:

\[
Y\mid h,x\sim\mathcal N(f_h(x),\sigma_{ref}^2).
\]

After validation evidence is frozen:

\[
F_U(y\mid x)=405^{-1}\sum_{h=1}^{405}\mathcal N(f_h(x),\sigma_{ref}^2),
\]

\[
F_M(y\mid x)=\mathcal N(f_{h_{MAP}}(x),\sigma_{ref}^2),
\]

\[
F_W(y\mid x)=\sum_hw_h\mathcal N(f_h(x),\sigma_{ref}^2).
\]

`specification_uniform_ensemble` and `specification_weighted_mixture` thus
retain components as predictive distributions even though their means are
affinely representable by one point specification.

## Exact CRPS scoring and estimands

Confirmatory CRPS uses the exact finite Gaussian-mixture formula, not Monte
Carlo sampling. For component means \(m_i\), weights \(w_i\), observation
\(y\), and \(A(d,s)=2s\phi(d/s)+d[2\Phi(d/s)-1]\),

\[
CRPS(F,y)=\sum_iw_iA(y-m_i,\sigma_{ref})-
\frac12\sum_{i,j}w_iw_jA(m_i-m_j,\sqrt2\sigma_{ref}).
\]

The primary prospective external-retention estimand is amended to

\[
B_1^{CRPS}=CRPS_U-CRPS_M,\qquad B_1^{CRPS}<0.
\]

The secondary non-directional weighting estimand is

\[
B_2^{CRPS}=CRPS_W-CRPS_U.
\]

Existing \(B_1^{NRMSE}\) and \(B_2^{NRMSE}\) remain secondary
point-prediction diagnostics only. They may be reported but must not be
described as evidence that predictive diversity itself was retained.

## Validation and test boundary

Validation targets may next be opened only to compute the pre-frozen Gaussian
working-likelihood scores, deterministic MAP, weights, entropy, and ESS.
Guard and confirmatory targets remain sealed until every candidate prediction
distribution is fixed. Weight ESS never authorizes a temperature change or
another candidate-grid modification.
