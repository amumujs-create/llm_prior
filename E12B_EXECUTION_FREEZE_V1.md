# E12-B Execution Freeze v1

## Corpus and estimand

- Scope: `Omega=[.40,.80]`; observed prefix: `[0,.40]`.
- Eight intended E11 triples × three generator families.
- Request 30 accepted tasks per intended triple × generator cell, with a
  maximum 1,000 attempts per cell.
- The estimand is conditional on accepted tasks for which **every** frozen
  operation in [E12B_OPERATION_CATALOG_V1.json](E12B_OPERATION_CATALOG_V1.json)
  meets its planned coverage/falsity and compatibility rule.

The expected accepted full corpus has 720 baseline tasks, 4,410 operation rows,
and 5,130 scoring rows total. Exhaustion is reported, never filled by another
cell or silently dropped.

## Compatibility and acceptance

The catalog builder checks the E11 contract-relevant compatibility fields
(named source library, scope, global semantics, and compatibility rule) before
using its registry-derived syntactic pairwise checker. Every realised task then
rechecks clean coverage/falsity for all catalog operations. Omission must be
coverage preserving; additions and reversals must be compatible but false.

## Scoring and audit

For each base task, all rows share one observed prefix, paired 4,096-member
bank, likelihood weights, and fixed target domain. The scorer receives no
future target, utility, engine, RMSE, or harm value. Each row stores
`S`, `ESS`, `N_survive`, `p_weighted`, floor status, coverage, and its exact
operation atoms. Finite-bank support is audited; floor states are not treated
as exact infinite sharpness.

## Integrity sanity

`--mode sanity` requests one accepted task per cell. It hard-fails if source
hashes disagree, catalog counts differ, coverage/falsity fails, ESS/weights
change across a base task, operation rows lack finite support audits, or the
sanity row count differs from the catalog-derived expectation. Only after this
passes may `--mode full` request 30 accepted tasks per cell.

## Interpretation

Coverage patterns are integrity invariants. Primary outputs stratify by
intended composition × operation type × target/source atom × generator.
False-addition analyses are primary by added atom; their pooled result is
supplementary because seven of eight catalog additions are `regime_postchange`.
