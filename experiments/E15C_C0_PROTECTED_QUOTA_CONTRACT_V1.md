# E15-C0 protected quota contract v1

## Inherited precision contract

E15-C inherits the E15-A/B paired-NRMSE precision framework:

\[
\epsilon=0.025\ \text{NRMSE},\qquad n_{\min}=125.
\]

The protected pilot estimates only the variance of predeclared paired C1/C2 NRMSE contrasts. It has no authority to alter E15-C0 numerical geometry.

## Primary precision cells

The six cells are the Cartesian product of:

- contrasts: `C1_C = weighted residual mixture − residual MAP`; `C2_C = weighted residual mixture − uniform residual ensemble`;
- prefix exposures: low, medium, high.

For each cell, a streaming accumulator may retain only count, sample standard deviation, one-sided 95% standard-deviation upper bound, and corresponding required quota:

\[
n_j=\left\lceil\left(\frac{1.96s_{\Delta,U,j}}{0.025}\right)^2\right\rceil,
\qquad
n_{\rm confirm}=\max\left(125,\max_j n_j\right).
\]

The pilot seed namespace is discarded and independent from the future confirmatory namespace.

## Protection rule

Per-task contrast values are passed directly from internal scoring to a streaming variance accumulator. They are never written, returned, logged, printed, or retained in an artifact. Contrast means, signs, policy-specific means, rankings, winners, hypothesis tests, RMSE, and CRPS are unavailable.

## Attempts

Generator acceptance is assessed only through outcome-free numerical admissibility. `max_attempts` is the smallest integer `N` satisfying

\[
P[\operatorname{Binomial}(N,p_L)<n_{\rm confirm}]<10^{-4},
\]

where `p_L` is the one-sided Wilson lower bound from discarded-pilot task acceptance.
