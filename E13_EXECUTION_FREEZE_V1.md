# E13 Execution Freeze v1

This manifest implements `JOINT_PRIOR_ANATOMY_E13_PROTOCOL_DRAFT_V1.md`
without adding a new axis.

## Corpus

- 8 exact-three-atom E11 intended triples × 3 generators × E9 `eta={.2,.5,.8}`
  × 3 controlled scope strata × 10 accepted seeds = 2,160 latent tasks.
- Each task contributes exactly the seven non-empty true subsets of its oracle
  triple: 15,120 primary candidate rows.
- Core acceptance/measurement domain: `Omega_0=[.40,.80]`; observation prefix
  `[0,.40]`; latent trajectory through `1.20`.
- Maximum attempts: 2,000 per fine cell. Store every rejection and exhaustion
  category specified in the protocol.

## Common scoring convention

Each task has one noisy prefix, one full five-coordinate paired `M=4096` bank,
one likelihood vector, and one fixed sharpness target `Omega_0`. These objects
must be identical over its seven rows. `ESS<100` is retained as
`measurement_unreliable`; only invalid banks, non-finite ESS, and scorer
failures reject a task.

## Scope and completeness censoring

`H_valid*` is last contiguous valid horizon, beginning at `.80`; no failure
through `1.20` is stored as right-censored `>1.20`. `Delta H_scope` is exact
only with two observed endpoints, lower bounded with observed full/censored
subset, unresolved with two censored endpoints, and an integrity failure for
censored full/observed subset.

For nested `Delta S_miss`, exact/non-floor is primary; oracle-only floor is a
lower bound; both floor is unresolved; subset-only floor is an integrity
failure. Informational completeness requires a reliable exact gap `<=.10 nat`.

## Integrity gates

1. Exact unique three-atom oracle envelope and all seven core-covering subsets.
2. Candidate-specific `O_P`/`N_obs(P)` and task-context `O*`/`N_obs*` agree
   with the same E9 atom-evidence outputs.
3. Same-task bank, prefix, weights, ESS, fixed target, and score cache agree.
4. Nested sharpness/missing-information and scope-monotonicity invariants hold.
5. Scope/quota/censor/reliability accounting sums exactly to candidate rows.
6. The scorer cannot access clean future truth; oracle scope/coverage code is
   separated from scoring.

No desired joint state or association direction is an integrity gate.
