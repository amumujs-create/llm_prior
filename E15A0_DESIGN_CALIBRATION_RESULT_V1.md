# E15-A0 — Design-calibration result v1

## Scope

This discarded-seed calibration used no policy forecasts, RMSE, CRPS, policy
rankings, contrast means/signs, catastrophic-rate comparisons, or
concentration/commitment outcomes. It assessed only the frozen candidate
generator, evidence geometry, horizon admissibility, and linear-profile
numerics.

Candidate contract SHA-256:
`f92531f4258ba0b29e25aa8897b3297e681982da7a22ffe7c2f82c886f2e80f2`.

The corresponding numerical-calibration result SHA-256 is
`d8dc018ac474f65ba83e27fe927e184d9888ea6d04226a0dbee63e9f3eb86033`.

## Candidate generator and acceptance

- Normalized onset domain: `[0, 1]`; observation domain: `[0, 1]`.
- `a ~ Uniform[-.25, .25]`; `|b| ~ Uniform[.25, .55]` with balanced sign.
- `c=kappa*b`, `kappa=1`, and common `s0=.05W_tau`.
- Requested/accepted discarded pilot tasks: `200/200`.
- Proposals: `468`; boundary/exposure rejections: `268`; no other rejection
  category occurred.

The accepted pilot therefore passed the generator-only finite-range and
nondegenerate-regime gates without clipping.

## Evidence geometry and noise decision

`E_tau` was computed from the full admissible onset grid, independently of any
supplied knowledge interval. Median `(low, medium, high)` values were:

| `rho=sigma/R_ref` | Low | Medium | High |
|---|---:|---:|---:|
| `.01` | `.073` | `.133` | `.617` |
| `.025` | `.014` | `.052` | `.154` |
| `.05` | `.003` | `.013` | `.034` |
| `.10` | `.001` | `.003` | `.008` |

`rho=.025` is selected for the confirmatory numerical contract: it is the
largest candidate that retains a visibly diffuse-to-concentrated exposure
gradient while keeping central low/high overlap (low 5--95%: `.000--.078`;
high 5--95%: `.043--.376`). At `.05` and `.10`, even high-exposure evidence is
nearly diffuse; at `.01`, low/high central distributions no longer overlap.

## Horizon and linear-profile numerics

All candidate horizons `.40W_tau`, `.60W_tau`, and `.80W_tau` had:

- finite rate `1.00`;
- post-onset admissibility rate `1.00`;
- normalized-slope admissibility rate `1.00`.

The longest candidate, `.80W_tau`, is selected. Its median post-onset fraction
was `.618`, median `R_ref` was `.822`, and its normalized maximum slope median
was `.956` (95th percentile `1.045`).

The two-column deterministic profile design `[1, t+kappa*g_tau(t)]` was well
conditioned. Across all candidate onsets, noises, and exposure levels its
largest observed condition number was `33.33`, well below the frozen numerical
gate `1e6`; no low-exposure task was rejected because of conditioning.

## Protected quota calibration and final A0 freeze

The separate in-process protected adapter evaluated discarded tasks and passed
each signed paired NRMSE contrast directly to a streaming accumulator. No raw
contrast, policy loss, mean, sign, ranking, or winner was persisted. Each of
the 36 prespecified covered primary cells received 200 discarded tasks. The
adapter persisted only cellwise task counts, paired SDs, one-sided 95% SD upper
bounds, and required quotas.

- Frozen target 95% CI half-width: `epsilon=.025` NRMSE, half of the `.05`
  practical policy-contrast scale.
- Final confirmatory quota: `90` latent tasks.
- A0 feasibility: `200/468` accepted, with 95% Wilson lower acceptance
  probability `.383301`.
- Frozen maximum proposals: `316`, the smallest integer for which
  `P[Binomial(316, .383301) < 90] = 9.54e-5 < 1e-4`.

The current protected quota-result SHA-256 is
`d9f9d07af928ad4aacffbd285da1d5cc7421876b858479c66733ebbc10cbdbe4`.
The frozen confirmatory manifest SHA-256 is
`51a13eb5cc05b19d59299f21fd4f73aa5799eb4bf4a7bd164e673b0391842747`.
E15-A0 is complete: its discarded tasks are excluded from confirmatory E15-A.
