# E15-D v1.2 confirmatory contract

## Frozen numerical geometry and scoring target

E15-D confirmation inherits the selected D0 v1.2 geometry:

\[
I_\kappa=I_\lambda=[.10,.90],\quad \Delta=.05,\quad \rho=.10,
\quad (x_L,x_S,x_J)=(.25,.60,.85),\quad x_{\rm far}=1.00.
\]

The public observation grid is \(x_n=n/100\), \(n=0,\ldots,100\). All
exposures use the common clean far-OOD target window

\[
\Omega_{\rm far}=(.85,1.00].
\]

The target is the latent clean continuation

\[
f^*(x)=x+\kappa^*x^2+\lambda^*x^6,
\]

not a future noisy observation. Scores are NRMSE, whose denominator is the
public \(R_0=1\).

## Shared likelihood and candidate continuations

Every forecast policy uses the same grid
\(\mathcal G=\{(.10+.05i,.10+.05j)\}\), the same prefix-only sum NLL,
and the same normalized weights \(w_{ij}\) and marginals
\(w_i^\kappa,w_j^\lambda\). The continuation is

\[
f_{ij}(x)=x+\kappa_i x^2+\lambda_jx^6.
\]

No policy has access to future labels, \(\kappa^*\), \(\lambda^*\), the
clean far target, or the scoring window during fitting or weighting.

## Forecast policies

`joint_uniform`:

\[
\hat f_U(x)=\frac1{K_\kappa K_\lambda}\sum_{ij}f_{ij}(x).
\]

`kappa_selective`:

\[
\hat f_K(x)=\sum_{ij}w_i^\kappa\frac1{K_\lambda}f_{ij}(x).
\]

`factorized_joint_weighted`:

\[
\hat f_F(x)=\sum_{ij}w_i^\kappa w_j^\lambda f_{ij}(x).
\]

`joint_MAP` selects the row-major first minimizer of the common prefix NLL
(smallest \(\kappa\), then smallest \(\lambda\) under an exact numerical tie).

`joint_weighted` is not a scientific forecast-policy row. It is computed only
for the deterministic additive representation audit

\[
\max_{x\in[0,1]}|\hat f_{\rm joint}(x)-\hat f_F(x)|\le10^{-12}.
\]

## Estimands and prospective decision rule

Primary S estimands are

\[
D1_S=NRMSE_K-NRMSE_U,\qquad D2_S=NRMSE_F-NRMSE_K.
\]

Predictions are \(D1_S<0\) and \(D2_S>0\). The primary prospective principle
is **supported** only when both 95% latent-task paired-bootstrap confidence
intervals lie entirely on their predicted sides of zero. A sign-compatible
estimate whose interval includes zero is **direction-compatible but
inconclusive**; an interval entirely on the opposite side is a **prospective
failure**.

The preregistered secondary J estimand is

\[
D2_J=NRMSE_F-NRMSE_K,\qquad \text{prediction }D2_J<0.
\]

The secondary point-collapse stress estimand is evaluated at S:

\[
D3_S=NRMSE_{MAP}-NRMSE_F.
\]

Results are opened in the fixed order
\(D1_S\rightarrow D2_S\rightarrow D2_J\rightarrow D3_S\).

## Protected quota pilot and corpus rules

The protected quota pilot uses exactly 400 fresh discarded task IDs under
`e15d-quota-v1.2-protected`. It exposes only per-estimand paired standard
deviations and quota requirements, never contrast values, means, signs,
rankings, or winners. With \(\epsilon=.025\), its requirement for estimand
\(r\) is

\[
n_r=\left\lceil\left(\frac{1.96s_r}{.025}\right)^2\right\rceil.
\]

The confirmatory quota is \(\max(125,\max_r n_r)\) across
\(D1_S,D2_S,D2_J,D3_S\). The confirmatory namespace is
`e15d-confirmatory-v1.2`; it contains exactly that many latent tasks with no
acceptance/rejection, resampling, or evidence-conditioned task selection.

## Inference and integrity

Inference uses 5,000 latent-task paired bootstrap replicates and cellwise 95%
confidence intervals. Before outcomes are opened, integrity must confirm
complete task × exposure × forecast-policy rows, no missing/duplicate/nonfinite
values, prefix-only weighting, deterministic replay, common grid, clean-target
scoring, and additive joint–factorized equivalence.
