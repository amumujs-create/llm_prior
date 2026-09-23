# E15-D v1.1 dependence-equivalence amendment

## Status

This is a pre-outcome amendment. It leaves the D0 candidate geometry, the S
primary estimands D1 and D2, and every prospective directional prediction
unchanged.

## Additive-mixture equivalence

For the frozen continuation family

\[
f_{ij}(x)=x+\kappa_i x^2+\lambda_j x^6,
\]

let \(w_{ij}\) be any normalized joint weights, with marginals
\(w_i^\kappa=\sum_jw_{ij}\) and \(w_j^\lambda=\sum_iw_{ij}\). Then

\[
\sum_{ij}w_{ij}f_{ij}(x)
=x+x^2\sum_i\kappa_iw_i^\kappa+x^6\sum_j\lambda_jw_j^\lambda,
\]

which is exactly the same expression obtained from factorized weights
\(w_i^\kappa w_j^\lambda\). Thus posterior dependence cannot affect the
mixture-mean point prediction after its two marginals are fixed.

## Consequence

`joint_weighted` and `factorized_joint_weighted` are prediction-identical
under the frozen NRMSE point-prediction estimand. The former secondary
dependence contrast is therefore retired as a scientific contrast and retained
only as the deterministic representation-equivalence audit

\[
\max_{x\in[0,1]}|\hat f_{\rm joint}(x)-\hat f_{\rm factorized}(x)|\le10^{-12}.
\]

No \(\kappa\lambda\) interaction is added to the continuation family to
manufacture a dependence effect. Posterior-dependence utilization is outside
the scope of E15-D and may be studied only in a later experiment.

## Unchanged primary claims

The prospective S predictions remain

\[
D1_D<0,\qquad D2_D>0,
\]

and the conditional J prediction remains \(D2_D^J<0\). D0 remains strictly
outcome-free.
