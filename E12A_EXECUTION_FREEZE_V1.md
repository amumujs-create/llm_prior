# E12-A Execution Freeze v1

This freeze implements `PRIOR_FRAGILITY_E12A_PROTOCOL_DRAFT_V1.md` without
adding a research axis.

## Corpus

- Fields: regime onset, inflection location, turning location, lower-bound
  level, asymptotic limit.
- Generators: spline, basis, ODE.
- Requested: 30 accepted latent trajectories per field × generator cell.
- Maximum attempts: 1,000 per field × generator cell.
- Baseline specification states: `r0=-.8,0,+.8` for two-sided fields;
  `m0/R_ref=.005,.035,.075` for lower bound.
- Perturbations: zero once; signs `-1,+1` at
  `.025,.05,.10,.20,.30` (11 rows per baseline state).
- Expected: 450 latent trajectories and 14,850 perturbation rows.

`R_ref=max_Omega(f*)-min_Omega(f*)`; bound/asymptote tasks with
`R_ref<.05` are rejected/redrawn, with accounting. Location/event truths must
lie in `[.54,.66]`; clipping is prohibited.

## Measurement and independence

Observed prefix is `[0,.40]`; the scoring target is fixed
`Omega=[.40,.80]`. Every trajectory shares one noisy prefix and one paired
`M=4096` ambient bank across all baseline states and perturbations. The bank
and its satisfaction semantics are frozen in
`E12A_SATISFACTION_REGISTRY_V1.json`.

The scorer can receive only prefix observations, candidate `(f_m,z_m)` bank,
and the declared perturbed specification. Coverage/violation use oracle clean
truth in a separate validation stage. Prediction, utility, RMSE, engine output,
and future target values are prohibited from scoring.

## Exact status rules

- `epsilon_break,s*`: first invalid nonzero grid point; `>.30` only when no
  invalid point is observed.
- `epsilon_CW,s*`: first row with invalid coverage, `ESS>=100`, and
  sharpness `>=.10 nat`; if no break, not-at-risk; if break but no onset,
  `>.30` right-censored.
- `Delta_epsilon_CW` is recorded only when both endpoints are observed.
- `Delta S_spec=S(P_epsilon|D)-S(P_0|D)` is exact when neither prior floors;
  lower bounded when only perturbed floors; upper bounded when only baseline
  floors; unresolved when both floor. Censored values are never pooled as
  exact changes.
- ESS and likelihood weights must be byte/numerically identical across all
  baseline state × sign × epsilon rows of a trajectory.

## Primary reporting and inference

Primary tables/figures stratify by `field × baseline specification state ×
sign`. Equal-weight baseline-state aggregation is supplementary. Bootstrap
resamples latent trajectories within field × generator cells, then aggregates
generators equally.

The estimand is conditional on nondegenerate-range accepted trajectories for
bound/asymptote fields. It describes controlled specification fragility, not
intrinsic primitive ranking, real-world calibration frequencies, prediction
utility, or safety.
