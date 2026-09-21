# E14-A measurement-scaling sanity result v1

**Status: PASS — integrity and measurement support only.** This is not a
complexity-effect analysis.

## Frozen execution artifact

- Completed corpus: 216 base cells, 2,592 accepted paired groups, and 7,776
  branch-condition scorings.
- Common finite-bank size: `M_common = 16384`.
- Selection basis: `largest_frozen_reference_after_any_lower_M_failure`.
- Manifest SHA-256:
  `3afe532c2449d7c9a20f3df7a651d98e51bb995356f24327c77ea9436adafbb1`.
- Machine-readable artifacts are retained under
  `results/complexity_scaling_e14/e14a/`; the large raw manifest is deliberately
  not committed to Git.

## 1. Integrity

- Direct frozen-checker versus atom-AND audit failures: **0**.
- Realized-envelope mismatch, base-persistence failure, scope mismatch,
  semantic failure, numeric-field rejection, and unclassified exception:
  **0** each.
- Exhausted cells: **0**.

The completed run therefore satisfies the frozen implementation and clean
semantic contracts. This statement does not assert a complexity effect.

## 2. Feasibility and rejection accounting

Every one of the 216 base cells and three primary axes supplied its required
four accepted paired groups within `MAX_GROUP_PROPOSALS = 2000`. The run
accepted all 2,592 required groups and recorded no proposal rejection in any
predeclared category. This is an E14 generator-feasibility result, not a
performance result.

## 3. Finite-bank convergence decision

The frozen global rule selects a single common bank size. Across 1,944
convergence cells per lower bank size, 786 cells failed at 4,096 and 563 cells
failed at 8,192. Consequently neither lower size satisfies the required
all-cells criterion. The predeclared largest finite reference bank,
`M_common = 16384`, is fixed for E14-B/C/D.

This does **not** treat 16,384 as ground truth; it is the largest frozen
finite-bank reference required by the stated convergence contract.

## 4. Measurement support at M = 16,384

All nine primary branch conditions had:

- reliability rate (`ESS >= 100`): **1.00**;
- floor-hit rate: **0.00**; and
- exact completeness-gap availability: **1.00**.

The run also saved continuous atom evidence, effective dimension, and
normalized continuation dispersion for every candidate row. Their magnitudes
are measurement-support outputs only at this stage; no directional
dimension/interaction/heterogeneity claim is made here.

## Authorized next step

Freeze the above manifest hash and `M_common = 16384`. E14-B/C/D may now
analyse paired complexity contrasts, retaining clustered paired-latent-group
inference and the predeclared interpretation boundaries.
