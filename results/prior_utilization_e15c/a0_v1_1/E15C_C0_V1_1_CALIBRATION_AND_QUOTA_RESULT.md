# E15-C0 v1.1 calibration and protected quota result

## Versioned estimator correction

The sole change from v1 is bounded nuisance-amplitude profiling:

\[
\hat A(q)=\operatorname{clip}(\hat A_{\rm LS}(q),-1.5A_{\rm ref},+1.5A_{\rm ref}).
\]

Generator, invariant, residual family, public coordinate, `R_inv`, amplitude generator range, grid candidates, noise candidates, exposure endpoints, and far-horizon candidates are unchanged.

## Outcome-free calibration

All C0 gates pass, with the same predeclared selection outcome:

\[
\Delta q=.05,\qquad \rho=.10,\qquad x_{\rm far}=1.00.
\]

Residual evidence remains ordered low < medium < high without universal endpoint saturation; adjacent 5–95% intervals overlap; median effective continuation counts are at least four at every exposure; and uniform residual predictions remain distinct from the closed-mechanism stress condition.

The bounded profile is active in weak-prefix geometry (fraction at the amplitude cap: low `.534`, medium `.300`, high `.247`), confirming that v1.1 addresses the intended nuisance-profile blow-up rather than changing residual-shape uncertainty.

## Protected quota result

The protected C1/C2 variance calculation uses the inherited precision target `epsilon=.025` NRMSE and minimum quota 125. Per-task contrasts, contrast means, signs, policy scores, rankings, winners, RMSE, and CRPS were never persisted or inspected.

Every primary C1/C2-by-exposure cell required no more than the minimum quota. The resulting confirmatory quota is therefore

\[
n_{\rm confirm}=125,
\]

with outcome-free max-attempts value `133` under the frozen Wilson/binomial rule.

## Artifacts

- Outcome-free sweep: `E15C_C0_V1_1_OUTCOME_FREE_SWEEP.json`
  - SHA-256: `1e40b87a0b648cf23dab92bfa4f337737fd8ea03bace0c0d9756d8c499492a0b`
- Protected quota: `E15C_C0_V1_1_PROTECTED_QUOTA.json`
  - SHA-256: `4a4d14bf9cd4af687f87c10d90037f0d95069476556dfeed724a19684289ad18`
- Estimator amendment: `E15C_C0_V1_1_BOUNDED_PROFILE_AMENDMENT.md`
