# E14 pre-A execution freeze v1

This document closes the numeric and implementation choices required before
E14-A. It authorizes no E14-A run by itself; E14-A remains an integrity-only
sanity stage.

## 1. Primary estimands

- Dimension anchor: `d=1 -> d=3` is a zero-context-to-contextual bridge to
  E13. It is **not** called energy-matched dimension scaling.
- Primary matched dimension contrast: `d=3 <-> d=8`, additive background,
  no heterogeneity, log-amplitude RMS `sigma_g=.20`.
- Interaction contrast: `d=8`, additive vs pairwise vs entangled,
  `sigma_g=.20`, no heterogeneity.
- Heterogeneity contrast: `d=8`, additive background, none/moderate/strong;
  `kappa={0,.25,.50}` for bounded native fields and log-scale
  `sigma={0,.10,.20}` for positive amplitude fields.

The precise functions, normalization, admissible-interval rule, and rejection
rule are in the protocol's **Frozen context-field generator** section. They
are scientific generator parameters and may not be changed after E14-A.

## 2. Paired-group quota and exhaustion

A base cell is `intended packet x generator x eta x requested full-scope
stratum` (`8 x 3 x 3 x 3 = 216` cells). Each primary branch receives **6
accepted paired latent groups per base cell**. A group includes the complete
matched branch family required by that contrast; it is accepted only when all
members pass exact realized-core-envelope equality and requested/measured
scope agreement. Thus each primary branch targets 1,296 accepted groups.

`MAX_GROUP_PROPOSALS=2000` per base cell is fixed. Accounting records proposed
groups, accepted groups, whole-group `P_star` mismatch, persistent-base
failure, core-invariance failure, scope mismatch, semantic/checker failure,
numeric-field rejection, and exhaustion. A cell that exhausts is reported as
an E14 feasibility limitation; it is not filled by changing a scientific
range or by borrowing a group from another cell.

## 3. Predeclared combined corner

One supplementary stress contrast is fixed before results:

`(d=8, entangled, strong heterogeneity)` versus its matched
`(d=8, additive, no heterogeneity)` baseline.

It receives **3 accepted paired groups per base cell**, using the same
`MAX_GROUP_PROPOSALS=2000` and all primary matching rules. It is never pooled
with the three primary axis estimands and is described as a combined-corner
stress test only.

## 4. Inherited frozen artifacts

| Contract | Frozen source |
|---|---|
| Canonical atoms / E13 evidence template including `eta={.20,.50,.80}` | commit `3d126d7`, `experiments/preflight_e13_scope_aware.py`, blob `e7e905d5f374845dcc4d95cc648f47d1f2a15f6b` |
| E13 prefix-noise scale | commit `8ea0a9c`, `experiments/run_e13_corrected.py`, blob `ed0ddddb6e16a58c5a167d2384f8e308427d20e2`; E14 replaces independent draws with the paired master-noise field while retaining `.01 R_ref` scale |
| Scope semantics | commit `655c5d0`, `E13_EXTENDED_SCOPE_ORACLE_SEMANTICS_V1.md`, blob `55c30421d36e422ed86951d5708cc2e44f546ea2` |
| Scope intervention contract | commit `655c5d0`, `E13_SCOPE_GENERATOR_FREEZE_V1.md`, blob `c1bcdb424a63789035d67e9b89831c63c5fbe754` |

Scope horizons are `(.85,.90,1.00,1.10,1.20)`; strata are limited
`H*<=.90`, intermediate `H* in {1.00,1.10}`, and persistent = no failure
through `1.20`. Requested and measured strata are stored separately and only
measured equality accepts a group.

## 5. Uncertainty and manifest

Primary confidence intervals use **B=5,000** paired-latent-group clustered
bootstrap resamples, seed `20261014`. Candidate subsets never form independent
bootstrap units. The post-E14-A manifest records group IDs, base and branch
seeds, master-noise seed, master-bank seed, context-field parameter values,
realized RMS/max displacement, exact `P_star`, scope audit, and all rejection
accounting; its SHA-256 is frozen before E14-B/C/D.

No effect direction, effect size, ESS pattern, or state frequency is an E14-A
acceptance criterion.
