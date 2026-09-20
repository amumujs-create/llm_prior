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
- The earlier E11-derived 36,720-row preflight is a debug artifact, not the
  final E13 corpus. A new persistent-base scope-aware preflight freezes the
  accepted manifest, envelope-size distribution, and expected row count only
  after clean-oracle measured-stratum acceptance.
- Frozen corrected preflight: 2,160 accepted latent tasks, 34,560 candidate
  rows, zero exhausted cells; manifest SHA-256
  `a45ea724f2442ba919035ff73e65fc643ac732d48e15a550feb9d4b483579298`.
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

## Scope-aware acceptance contract

The post-`.80` intervention is a frozen generation input only. Scope scoring
does not receive its breaker metadata: it receives the resulting clean latent
trajectory and the frozen atom-oracle semantics. The pre/post clean trajectory
must be bit-identical on `x<=.80`; failure is an integrity violation. For
latent-assisted/mechanistic atoms, the scope checker reuses the corresponding
frozen E11 metadata semantics rather than silently substituting a new
trajectory-only rule. Store both `requested_scope_stratum` and
`measured_scope_stratum`; only the latter determines acceptance. The scope-aware
preflight stores intervention metadata, atomwise `C_a(h)`, full `C_Pstar(h)`,
measured `H_valid*`, core-equality audit, and every rejection reason.

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
