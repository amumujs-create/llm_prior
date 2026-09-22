# E15-A0 — Design-calibration result v1

## Scope

Policy outcomes were never inspected or used directionally. Protected paired
NRMSE contrasts were computed only internally for variance-based quota
calibration; their values, means, signs, rankings, and winners were never
exposed or persisted. The calibration otherwise assessed only the frozen
candidate generator, evidence geometry, horizon admissibility, and
linear-profile numerics.

Candidate contract SHA-256:
`b4f09caf4706e07db9888f8e97a330adbba73895f232a1de6538da59e8dc7c33`.

The corresponding numerical-calibration result SHA-256 is
`7eb7c25c69d95da5e2628d848f80417c235005a76e8bf35f159957741ed2e7af`.

## Candidate generator and acceptance

- Normalized onset domain: `[0, 1]`; observation domain: `[0, 1]`.
- `a ~ Uniform[-.25, .25]`; `|b| ~ Uniform[.25, .55]` with balanced sign.
- `c=kappa*b`, `kappa=1`, and common `s0=.05W_tau`.
- Requested/accepted discarded pilot tasks: `200/200`.
- Proposals: `480`; boundary/exposure rejections: `280`; no other rejection
  category occurred.

The accepted pilot therefore passed the generator-only finite-range and
nondegenerate-regime gates without clipping.

## Evidence geometry and noise decision

`E_tau` was computed from the full admissible onset grid, independently of any
supplied knowledge interval. Median `(low, medium, high)` values were:

| `rho=sigma/R_ref` | Low | Medium | High |
|---|---:|---:|---:|
| `.01` | `.089` | `.184` | `.751` |
| `.025` | `.024` | `.089` | `.381` |
| `.05` | `.005` | `.025` | `.103` |
| `.10` | `.001` | `.007` | `.025` |

`rho=.025` is selected for the confirmatory numerical contract: it is the
largest candidate that retains a visibly diffuse-to-concentrated exposure
gradient while keeping central low/high overlap (low 5--95%: `.000--.118`;
high 5--95%: `.129--.531`). At `.05` and `.10`, even high-exposure evidence is
nearly diffuse; at `.01`, low/high central distributions no longer overlap.

## Horizon and linear-profile numerics

All candidate horizons `.40W_tau`, `.60W_tau`, and `.80W_tau` had:

- finite rate `1.00`;
- post-onset admissibility rate `1.00`;
- normalized-slope admissibility rate `1.00`.

The longest candidate, `.80W_tau`, is selected. Its median post-onset fraction
was `.617`, median `R_ref` on the common far-OOD window
`(tau*+.10W_tau, tau*+.80W_tau]` was `.567`, and its normalized maximum slope
median was `1.439` (95th percentile `1.439`).

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
- Final confirmatory quota: `125` latent tasks.
- A0 feasibility: `200/480` accepted, with 95% Wilson lower acceptance
  probability `.373394`.
- Frozen maximum proposals: `432`, the smallest integer for which
  `P[Binomial(432, .373394) < 125] = 9.76e-5 < 1e-4`.

The current protected quota-result SHA-256 is
`d4c633c0d22e00d419df127cc2f5f0d93218ba5e332670d9e288846165aa543e`.
The frozen confirmatory manifest SHA-256 is
`c13519c7e7f5e8c0b4af4d8a550d5b36a4735de60354c2a998e6c0017bf736b3`.
E15-A0 is complete: its discarded tasks are excluded from confirmatory E15-A.
