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
- [x] Exact context-field parameterizations for additive, pairwise, entangled,
  and heterogeneity levels, including positive multiplicative modulation,
  `d=1` anchor handling, RMS/bounds, and no-clipping rejection; see
  `E14_PRE_A_EXECUTION_FREEZE_V1.md`.
- [x] Multivariate persistent-base acceptance and post-`.80` C2 intervention
  contracts, including post-intervention latent semantic state for regime and
  asymptote. The clean-field micro sanity passed all 72
  `packet x generator x requested-scope` cells before E14-A.
- [x] Exact paired realized-envelope equality, orthogonal branch backgrounds,
  and matched full-envelope scope as a control; subset extension is the scope
  estimand.
- [x] Balanced paired-group quota, requested/measured scope acceptance, and
  maximum attempt accounting.
- [x] Fixed selected combined-corner cell and an explicit declaration that it
  is supplementary.
- [x] Master paired prefix-noise field, E13 inherited-artifact hashes,
  `B=5000` paired-group bootstrap, and scope-horizon/stratum values.
- [x] Packet-specific heterogeneity-field table and an independent E14-A
  pilot (`4` groups/base-cell/branch), including additive geometry, seed
  namespaces, paired-baseline `R_ref`, and p95/Spearman edge-case rules.
- [x] Master-bank scorer smoke test: shared weights/ESS, AND-derived
  satisfaction, floor-gap states, and direct-candidate audit.

The following are *not* E14-A gates: monotonic ESS, lower sharpness at higher
complexity, lower completeness, lower evidence, or any desired joint state.
