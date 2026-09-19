# E13 Execution Freeze v1

This manifest implements `JOINT_PRIOR_ANATOMY_E13_PROTOCOL_DRAFT_V1.md`
without adding a new axis.

## Corpus

- 8 E11 intended triples × 3 generators × E9 `eta={.2,.5,.8}`
  × 3 controlled scope strata × 10 accepted seeds = 2,160 latent tasks.
- The intended triple is generator intent, not a restriction on the realized
  oracle envelope. Every accepted task retains its unique inclusion-maximal
  compatible coverage-preserving envelope under the unchanged E11 grammar,
  including canonically implied atoms.
- Each task contributes all non-empty true subsets of its realized envelope:
  `N_rows=sum_t (2^{|P_star,t|}-1)`. Freeze this expected count and the envelope
  size distribution from a deterministic accepted-seed preflight before full
  scoring.
- Frozen preflight (`results/joint_prior_anatomy_e13/preflight/summary.json`):
  1,890 four-atom and 270 five-atom envelopes, hence **36,720** primary
  candidate rows; no exhausted cell. The accepted-task manifest SHA-256 is
  `ac2fdc8dea7294fcff3e1347f470b622a47ec7894a7d2f4eb61a28f7d50ce46d`.
  Core-envelope preflight occurs on `Omega_0` before any post-`.80` scope
  intervention, so scope control cannot change envelope membership.
- Core acceptance/measurement domain: `Omega_0=[.40,.80]`; observation prefix
  `[0,.40]`; latent trajectory through `1.20`.
- Maximum attempts: 2,000 per fine cell. Store every rejection and exhaustion
  category specified in the protocol.

## Common scoring convention

Each task has one noisy prefix, one full five-coordinate paired `M=4096` bank,
one likelihood vector, and one fixed sharpness target `Omega_0`. These objects
must be identical over all rows within that task. `ESS<100` is retained as
`measurement_unreliable`; only invalid banks, non-finite ESS, and scorer
failures reject a task.

## Scope and completeness censoring

`H_valid*` is last contiguous valid horizon, beginning at `.80`; no failure
through `1.20` is stored as right-censored `>1.20`, never numerically replaced
by `1.20` for a mean, median, or other endpoint summary. Scope is reported
primarily as the horizon profile `P(C_P(h)=1)`, where `C_P(h)` is contiguous
validity through horizon `h`. For the oracle-full row itself,
`delta_H_scope_status=exact` and `delta_H_scope_value=0` by identity, even if
its own `H_valid*` is right-censored. For proper subsets only, `Delta H_scope`
is exact with two observed endpoints, lower bounded with observed full/censored
subset, unresolved with two censored endpoints, and an integrity failure for
censored full/observed subset.

For nested `Delta S_miss`, exact/non-floor is primary; oracle-only floor is a
lower bound; both floor is unresolved; subset-only floor is an integrity
failure. Informational completeness requires a reliable exact gap `<=.10 nat`.
Report the audit denominator `P(gap_status=exact | C_atom=0, reliable)` beside
every informational-completeness rate.

## Integrity gates

1. Unique maximal oracle envelope under the unchanged E11 grammar, recorded
   intended/envelope/implied atom IDs, and all non-empty core-covering subsets.
2. Candidate-specific `O_P`/`N_obs(P)` and task-context `O*`/`N_obs*` agree
   with the same E9 atom-evidence outputs.
3. Same-task bank, prefix, weights, ESS, fixed target, and score cache agree.
4. Nested sharpness/missing-information and scope-monotonicity invariants hold.
5. Scope/quota/censor/reliability accounting sums exactly to candidate rows.
6. The scorer cannot access clean future truth; oracle scope/coverage code is
   separated from scoring.
7. Primary pooled analysis uses within-task candidate weights
   `1/(2^{|P_star|}-1)` and equal generator weighting; primary strata retain
   oracle-envelope size and omitted-atom count.

No desired joint state or association direction is an integrity gate.
