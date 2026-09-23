# E15-D v1.1 factorised-D2 and D0 contract

## Status and scope

This is a pre-outcome amendment to `E15D_SEMANTIC_CONTRACT_V1.md`. It adds a
factorised weighting policy so that the D2 primary estimand isolates marginal
\(\lambda\)-dimension reduction from posterior-dependence utilization. It
also operationalizes D0 numerical selection. No E15-D policy outcome has been
calculated or inspected before this amendment.

## D2 isolation amendment

The original full joint weights are

\[
w_{ij}=p(\kappa_i,\lambda_j\mid D_{\rm prefix}),\qquad
w_i^\kappa=\sum_jw_{ij},\qquad w_j^\lambda=\sum_iw_{ij}.
\]

`joint_weighted` uses \(w_{ij}\), so compared with `kappa_selective` it both
reduces \(\lambda\) marginal uncertainty and uses \(\kappa\)-\(\lambda\)
posterior dependence. It is therefore retained but no longer defines D2.

### Additional frozen policy: `factorized_joint_weighted`

\[
\hat f_{\rm fact}(x)=\sum_{ij} w_i^\kappa w_j^\lambda f_{ij}(x).
\]

It uses both marginal likelihood weights but deliberately removes joint
dependence from the policy representation.

| Policy | \(\kappa\) treatment | \(\lambda\) treatment | Joint dependence |
| --- | --- | --- | --- |
| `joint_uniform` | uniform | uniform | none |
| `kappa_selective` | \(w^\kappa\) | uniform | none |
| `factorized_joint_weighted` | \(w^\kappa\) | \(w^\lambda\) | none |
| `joint_weighted` | full joint | full joint | used |
| `joint_MAP` | point | point | collapsed |

### Revised primary and secondary estimands

The S-regime primary estimands are

\[
D1_D=NRMSE_{\kappa\text{-selective}}-NRMSE_{\rm joint-uniform},
\]

\[
D2_D=NRMSE_{\rm factorized\ joint}-NRMSE_{\kappa\text{-selective}}.
\]

Thus D2 isolates adding marginal \(\lambda\) weighting while preserving the
same marginal \(\kappa\) weighting and excluding dependence utilization.

The secondary dependence contrast is

\[
D_{\rm dep}=NRMSE_{\rm joint-weighted}-NRMSE_{\rm factorized\ joint}.
\]

`joint_MAP` remains the secondary all-dimensions point-collapse stress policy:

\[
D3_D=NRMSE_{\rm joint-MAP}-NRMSE_{\rm joint-weighted}.
\]

## Public normalization and candidate numerical ladders

The public anchor is frozen as

\[
a=0,\qquad b=1,\qquad R_0=b(1-0)=1.
\]

Noise and NRMSE are both normalized by \(R_0\): \(\sigma=\rho R_0=\rho\).
No policy receives future truth or a realization-specific normalization.

The common coefficient-support candidates, in descending preference order,
are:

| Candidate | \(I_\kappa\) | \(I_\lambda\) |
| --- | --- | --- |
| broad | \([.10,.90]\) | \([.10,.90]\) |
| medium | \([.20,.80]\) | \([.20,.80]\) |
| narrow | \([.30,.70]\) | \([.30,.70]\) |

Latent truth \((\kappa^\*,\lambda^\*)\) is sampled continuously and
uniformly on the selected support, not restricted to grid points.

Additional D0 candidates:

| Component | Candidates |
| --- | --- |
| common grid spacing | \(.05,.025\) |
| noise ratio \(\rho\) | \(.01,.025,.05,.10\) |
| exposure triples \((x_L,x_S,x_J)\) | \((.25,.55,.80),(.25,.60,.85),(.30,.65,.90)\) |
| far horizon | \(.95,1.00\) |
| joint-continuation distinctness | normalized RMS threshold \(.01\), minimum 4 mutually distinguishable continuations |

All L/S/J prefixes must be nested views of one master standardized noise path
per latent task.

## D0 construct-validity gates

For the evidence vector \((E_\kappa,E_\lambda)\), D0 must satisfy:

### L regime

\[
\operatorname{median}E_\kappa^L\le .05,\qquad
\operatorname{median}E_\lambda^L\le .05.
\]

### S regime: prospective primary geometry

\[
\operatorname{median}E_\kappa^S-\operatorname{median}E_\kappa^L\ge .10,
\]

\[
\operatorname{median}E_\lambda^S\le .05,
\]

\[
\operatorname{median}E_\kappa^S-\operatorname{median}E_\lambda^S\ge .10.
\]

### J regime

\[
\operatorname{median}E_\lambda^J-\operatorname{median}E_\lambda^S\ge .10,
\qquad \operatorname{median}E_\lambda^J\ge .10,
\]

\[
\operatorname{median}E_\kappa^J\ge\operatorname{median}E_\kappa^S.
\]

These are D0 construct-calibration gates, not universal strong-evidence
thresholds. To retain exposure continuity, D0 also requires

\[
Q_{95}(E_\kappa^L)>Q_{05}(E_\kappa^S),\qquad
Q_{95}(E_\lambda^S)>Q_{05}(E_\lambda^J).
\]

## Deterministic D0 selection order

Select, in order:

1. widest admissible common support: broad → medium → narrow;
2. coarsest admissible common grid: \(.05\) → \(.025\);
3. largest admissible noise: \(.10\) → \(.05\) → \(.025\) → \(.01\);
4. earliest admissible exposure triple: \(T_1\) → \(T_2\) → \(T_3\);
5. longest admissible horizon: \(1.00\) → \(.95\).

The confirmatory common evaluation window is

\[
\Omega_{\rm far}=(x_J,x_{\rm far}].
\]

D0 may inspect only evidence geometry, continuation distinctness, finite
trajectory behavior, and numerical stability. It may not create, inspect, or
persist policy predictions, RMSE, CRPS, D1, D2, \(D_{\rm dep}\), D3, policy
means, signs, rankings, or winners.

## Prospective directional predictions

In the preregistered S primary cell:

\[
D1_D<0,\qquad D2_D>0.
\]

That is, reducing the identified \(\kappa\) uncertainty is predicted to help,
whereas additionally reducing still-weak \(\lambda\) uncertainty is predicted
to harm.

In J, conditional on D0 satisfying the J evidence geometry, the secondary
prediction is

\[
D2_D^J<0.
\]

E15-D is a prospective test: success and failure are both retained as the
scientific result. No D0 outcome can change these predictions.

## Additional outcome-free audits

- All policies share the same joint candidate grid and continuations.
- `factorized_joint_weighted` uses \(w_i^\kappa w_j^\lambda\) exactly and
  its weights sum to one.
- With \(K_\lambda=1\), `kappa_selective`,
  `factorized_joint_weighted`, and `joint_weighted` are prediction-identical.
- With \(K_\kappa=K_\lambda=1\), every policy is prediction-identical.
- Future labels, latent truth, and scoring windows cannot enter prefix NLL,
  marginalization, weights, or predictions.
