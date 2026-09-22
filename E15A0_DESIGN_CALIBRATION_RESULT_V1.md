# E15-A0 — Design-calibration result v1

## Scope

This discarded-seed calibration used no policy forecasts, RMSE, CRPS, policy
rankings, contrast means/signs, catastrophic-rate comparisons, or
concentration/commitment outcomes. It assessed only the frozen candidate
generator, evidence geometry, horizon admissibility, and linear-profile
numerics.

Candidate contract SHA-256:
`2f25df1536573ff26c4e8f1595c62ab49618c966e11e04a82148e62620afd5ef`.

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

## Remaining A0 step

Task quota and maximum attempts are not frozen by this artifact. They require
the separately protected, variance-only C1/C2/C3 cellwise calibration. That
adapter must emit only blinded paired-SD upper bounds and required quota, never
policy-loss means, signs, ranks, or winners. Until then, this is a partial A0
geometry/numerics freeze, not the final confirmatory manifest.
