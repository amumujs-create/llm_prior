# E14 Design Freeze Checklist v1

E14 cannot start a generator or a full run until each item is frozen.

- [x] `Z_ref^max`: 64-point scrambled-Sobol design in `[-1,1]^7`, seed
  `20261014`; use deduplicated nested coordinate projections and one null
  context at `d=1`.
- [x] Context-balanced observation layout: primary `N=49` (`1x49` at `d=1`,
  `7x7` at `d={3,8}`); density control is `49 x |Z_ref^(d)|`.
- [x] Context-balanced evidence aggregation: compute the frozen E9 contrast
  per observed context and take the equal-context mean; `d=1` has one null
  context.
- [x] Common nested bank ladder `4096 subset 8192 subset 16384` and convergence
  criteria against `16384`; ESS is excluded from the bank-selection rule.
- [ ] Exact context-field parameterizations for additive, pairwise, entangled,
  and heterogeneity levels, including mean-zero/RMS matching and bounds that
  preserve the same atom semantics over all `Z_ref`.
- [ ] Multivariate persistent-base acceptance and post-`.80` C2 intervention
  contracts, including post-intervention latent semantic state for regime and
  asymptote.
- [x] Exact paired realized-envelope equality, orthogonal branch backgrounds,
  and matched full-envelope scope as a control; subset extension is the scope
  estimand.
- [ ] Balanced paired-group quota, requested/measured scope acceptance, and
  maximum attempt accounting.
- [ ] Fixed selected combined-corner cells and an explicit declaration that
  they are supplementary.

The following are *not* E14-A gates: monotonic ESS, lower sharpness at higher
complexity, lower completeness, lower evidence, or any desired joint state.
