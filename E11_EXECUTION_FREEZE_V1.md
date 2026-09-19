# E11 Execution Freeze v1

## Estimand

E11 estimates grammar-relative canonical-atom completeness and conditional
missing information **only among tasks with a unique inclusion-maximal
compatible coverage-preserving envelope** in the frozen E11 atom universe. It
does not estimate completeness over all conceivable grammar tasks. Envelope
ambiguity is therefore a representativeness limitation, measured and reported
by intended atom triple × generator cell.

## Frozen identity artifacts

- Canonical atom library: `E11_CANONICAL_ATOM_LIBRARY_V1.json`
- Exact generator intent atom IDs: `E11_INTENDED_ATOM_INTENTS_V1.json`
- Atom-instance compatibility/scope registry:
  `E11_COMPATIBILITY_SCOPE_REGISTRY_V1.json`

Frozen pre-run SHA-256 values:

- canonical atom library: `137f2ece33c161bb04e1f4ba6d7675b88fd2250d963d656f1b45b1251736326a`
- intended atom registry: `c739bf617751bfa7555774ca8c3030b703e1a31223d15f850cb9c040b70b7cd7`
- compatibility/scope registry: `9cf4d826931e56990dc3b533113199402be9a72c384fa7e0318476cc35f95d54`

The execution manifest must record SHA-256 hashes of all three files plus the
runner code. The oracle may select only from these atom instances; it may not
create signed, bound, onset, interval, rate, or shape instances after observing
the clean future.

## Corpus acceptance and accounting

For each exact intended atom triple × generator cell: request 30 accepted
tasks; cap deterministic generation attempts at 1,000. Store requested count,
attempt count, accepted count, ambiguous-envelope reject count,
coverage/checker reject count, other reject count, and exhaustion status.

## Scoring and classification

- `Omega=[.40,.80]`; observed prefix `[0,.40]`; same M=4096 bank and weights
  for all supplied subsets/envelope candidates within a task.
- `C_atom=1` only for exact atom-set equality with `P_star`.
- Primary informational classification requires `ESS>=100`.
- `delta_info=.10 nat`.
- Oracle floor-hit / candidate non-floor-hit: gap is a lower bound; classify
  informationally incomplete only when that lower bound exceeds `.10`, else
  unresolved.
- Both floor-hit: unresolved.
- Candidate floor-hit / oracle non-floor-hit is a nested-consistency failure.

## Integrity-only sanity gates

Exact intended atom IDs match task metadata; all supplied subsets are subsets
of the accepted envelope; atom-library and compatibility hashes match manifest;
coverage is one on Omega; same prefix/bank/weights are reused; conjunction
monotonicity and nonnegative gap hold up to tolerance; floor and ESS cases use
the frozen classifications; and no utility/engine/RMSE/prediction enters
scoring.
