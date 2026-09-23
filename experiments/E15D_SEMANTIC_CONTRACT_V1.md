# E15-D v1 semantic contract

## Purpose

E15-D is a prospective test of the frozen E15-A/B/C utilization principle:

> Reduce uncertainty only when the evidence is informative about the same
> uncertainty dimension being reduced.

It tests selective uncertainty reduction in a held-out multidimensional shape
prior. It is not a policy winner search.

## Frozen prior object and uncertainty anatomy

The clean continuation family is

\[
f(x)=a+bx+\kappa x^2+\lambda x^6,\qquad x\in[0,1].
\]

`a` and `b` are supplied and fixed. The only uncertain coordinates are
\(U=(U_\kappa,U_\lambda)\). With positive \(b,\kappa,\lambda\), the
continuation is increasing and convex. There is no event onset, finite
validity endpoint, or mechanistic residual in this experiment.

Every policy shares the same frozen joint grid

\[
\mathcal G=\{(\kappa_i,\lambda_j)\}
\]

and the same candidate continuations

\[
f_{ij}(x)=a+bx+\kappa_i x^2+\lambda_j x^6.
\]

Policies may differ only in how they average or collapse those common
continuations.

## Evidence vector

For each joint grid point, the prefix-only likelihood is

\[
\ell_{ij}=NLL(D_{\rm prefix}\mid\kappa_i,\lambda_j),\qquad
w_{ij}=\frac{\exp[-(\ell_{ij}-\ell_{\min})]}
{\sum_{rs}\exp[-(\ell_{rs}-\ell_{\min})]}.
\]

Marginal weights and dimension-specific evidence are

\[
w_i^\kappa=\sum_jw_{ij},\qquad w_j^\lambda=\sum_iw_{ij},
\]

\[
E_\kappa=1-\frac{H(w^\kappa)}{\log K_\kappa},\qquad
E_\lambda=1-\frac{H(w^\lambda)}{\log K_\lambda}.
\]

Evidence is explicitly vector-valued. No scalar evidence summary may replace
\((E_\kappa,E_\lambda)\) for D0 selection or confirmatory interpretation.

## Frozen policies

1. `joint_uniform`

   \[
   \hat f(x)=\frac{1}{K_\kappa K_\lambda}\sum_{ij}f_{ij}(x).
   \]

2. `kappa_selective`

   \[
   \hat f(x)=\sum_{ij}w_i^\kappa\frac{1}{K_\lambda}f_{ij}(x).
   \]

   It reduces only \(\kappa\) uncertainty and keeps \(\lambda\) uniform.

3. `joint_weighted`

   \[
   \hat f(x)=\sum_{ij}w_{ij}f_{ij}(x).
   \]

4. `joint_MAP`

   \[
   (\hat\kappa,\hat\lambda)=\arg\max_{ij}w_{ij}.
   \]

   It is a secondary all-dimensions point-collapse stress policy.

## Primary prospective estimands

The preregistered primary test is the S regime, where D0 must establish
greater \(\kappa\) evidence while \(\lambda\) remains weak:

\[
E_\kappa\text{ informative},\qquad E_\lambda\text{ weak}.
\]

\[
D1_D=NRMSE_{\kappa\text{-selective}}-NRMSE_{\rm joint-uniform}
\]

tests the value of reducing only the identified \(\kappa\) coordinate.

\[
D2_D=NRMSE_{\rm joint-weighted}-NRMSE_{\kappa\text{-selective}}
\]

tests the cost or value of also reducing the still-weak \(\lambda\)
coordinate. The prospective directional prediction is that selective
reduction is preferred in S.

\[
D3_D=NRMSE_{\rm joint-MAP}-NRMSE_{\rm joint-weighted}
\]

is secondary all-dimensions point-collapse stress.

## D0 calibration boundary

D0 may select only numerical geometry: \(\kappa,\lambda\) ranges, grid
spacing, noise, L/S/J exposure locations, and far horizon. It must use only
dimension-specific evidence geometry, joint-continuation distinctness, and
numerical stability. It must not inspect policy RMSE, CRPS, D1, D2, D3,
policy means, signs, rankings, or winners.

D0 must construct these ordered evidence regimes without thresholding them as
strong versus weak evidence:

| Regime | Required geometry |
| --- | --- |
| L | \(E_\kappa\) low, \(E_\lambda\) low |
| S | \(E_\kappa\) clearly greater than L, \(E_\lambda\) remains weak |
| J | \(E_\kappa\) increased and \(E_\lambda\) materially increased |

## Outcome-free implementation audits

- Every policy uses only its prefix and the supplied joint grid.
- All policies share identical candidate continuations and forecast grid.
- `kappa_selective` uses marginal \(w^\kappa\) and a uniform \(\lambda\)
  factor exactly.
- With \(K_\lambda=1\), `kappa_selective` and `joint_weighted` are
  prediction-identical.
- With \(K_\kappa=K_\lambda=1\), all policies are prediction-identical.
- Future labels, true \((\kappa,\lambda)\), and scoring outcomes never enter
  likelihood, weighting, or prediction.

## Interpretation boundary

E15-D tests selective collapse for the frozen two-coordinate smooth shape
family only. It does not establish a universal multidimensional-prior rule
outside the tested geometry.
