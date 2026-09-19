# E13 — Joint Prior Anatomy Map

## 1. Question and boundary

E13 asks, on the **same latent task, observed prefix, and continuation bank**:

> How do validity, conditional informativeness, observability, scope, and
> grammar-relative completeness jointly occur among coverage-preserving priors?

It is not an escape from E12's wrong-prior findings. E12-A/B remain separate
perturbation evidence about anatomy **after** numeric specification or content
correctness has failed. E13's primary factorial contains valid priors only.

E13 excludes prediction models, RMSE, utility, harm, LLMs, Prior Critic,
recoverability, and all wrong-prior operations. It makes no scalar prior-quality
score.

## 2. Fixed base-task semantics

- Intended structures: the eight E11 canonical triples.
- Observed prefix: `D=[0,.40]`.
- Core declared scope and every sharpness/completeness target:
  `Omega_0=[.40,.80]`.
- Each latent trajectory is generated through `x=1.20`.
- One task receives one master noisy observation grid, one frozen paired
  `M=4096` continuation bank, and one likelihood-weight vector shared by all
  seven candidate priors. The primary scorer uses one full five-active-
  coordinate ambient-bank convention, consistent with E11/E12; E9's
  `DoF=1/3/5` views are supplementary task metadata rather than parallel E13
  rows. ESS must consequently be byte/numerically identical within a task.
- The E11 canonical atom library and compatibility/scope registry are reused
  unchanged. A task is accepted only if its unique inclusion-maximal compatible
  coverage-preserving envelope is **exactly its intended three atoms**.
  Incidental valid fourth atoms cause redraw and are counted.

The exact-three-envelope restriction intentionally makes completeness legible:
it is a selection condition, not an estimate of real-world envelope sizes.

## 3. Seven valid priors per task

For an accepted oracle envelope `P_star=A and B and C`, score every non-empty
true subset on `Omega_0`:

`ABC; AB, AC, BC; A, B, C`.

All seven candidates have core coverage one. Their canonical atom completeness
is deterministic (`ABC=1`, pairs omit one atom, singletons omit two), while
their conditional informational completeness remains empirical:

`Delta S_miss(P)=S(P_star|D)-S(P|D)`.

E11's nested floor rule is retained: neither candidate at floor yields an
exact gap; `P_star` only at floor yields a lower bound; both at floor are
unresolved; and a subset at floor while `P_star` is non-floor is an integrity
violation. The `.10 nat` informational-completeness label is primary only for
reliable, exact rows; censored gaps are unresolved.

No numeric perturbation, false addition, or reversal enters these seven rows.
Where applicable, E12-A/B are cited only in final interpretation as evidence
about what happens when this valid-prior anatomy is perturbed into invalidity.

E13 therefore estimates `P(S, O, H, Delta S_miss | V_Omega0=1)`. Validity is
an acceptance condition here, not a varying association axis.

## 4. Joint measurements

| Axis | Measurement | E13 semantics |
|---|---|---|
| Validity | core coverage | all seven rows must equal one on `Omega_0` |
| Informativeness | `S(P|D)`, primary threshold `.10 nat` | `ESS>=100` required for reliable interpretation; record `N_survive`, `p_weighted`, and floor state |
| Observability | atom-level `E_a` | reuse E9 checker; record candidate-specific `N_obs(P)=sum_{a in P} I(E_a>=.80)` and `O_P=I(min_{a in P} E_a>=.80)`; store oracle `N_obs*`, `O*` as task context |
| Scope | contiguous `H_valid*(P)` | clean scope scan at `.85,.90,1.00,1.10,1.20`; sharpness remains fixed on `Omega_0` |
| Completeness | `C_atom`, `Delta S_miss` | informationally complete iff reliable and `Delta S_miss<=.10 nat` |

Scope is intentionally measured beyond `.80` while sharpness remains on
`.40-.80`; this prevents a moving future target from confounding `S(P|D)`.
The scope scan uses E10's contiguous first-failure rule.

`H_valid*` is the **last contiguous valid horizon**, with `.80` as its initial
core endpoint: first failure at `.85/.90/1.00/1.10/1.20` yields
`.80/.85/.90/1.00/1.10`, respectively. No failure through `1.20` is recorded
as `H_valid*>1.20` (right-censored), never as an exact value `1.20`.
For `Delta H_scope=H_valid*(P_subset)-H_valid*(P_star)`: both observed
endpoints give an exact difference; observed full plus censored subset gives a
lower bound; both censored is unresolved; censored full plus observed subset is
a nesting integrity violation. “Weak but persistent” means no scope failure
through `1.20`, not `H_valid*>=1.20` as an exact assertion.

Candidate states use `O_P`, not oracle-wide `O*`: an observable pair `A and B`
is not labelled unobservable merely because omitted oracle atom `C` lacks
evidence. Oracle-wide observability remains a task-level context field.

## 5. Controlled variation and corpus

Reuse E9's frozen structural-separability control `eta` at its existing low,
medium, and high values; do not retune numeric values. Reuse nested realization
freedom only as a stored multiplicity control, not as a primary factorial
quota. Scope variation is balanced by acceptance stratification of the full
triple `P_star`:

| Scope stratum | Full-prior condition |
|---|---|
| Limited | `H_valid*(P_star)<=.90` |
| Intermediate | `H_valid*(P_star)` in `{1.00,1.10}` |
| Persistent-within-tested-domain | no failure through `1.20` |

Every accepted task remains valid on `Omega_0`. Scope stratum is a controlled
map condition—not an estimate of natural scope prevalence.

The frozen full corpus is:

`8 triples × 3 generators × 3 eta levels × 3 scope strata × 10 seeds`

`= 2,160 latent tasks` and `2,160 × 7 = 15,120` candidate rows.

Each fine cell has at most 2,000 generation attempts. Store `attempts`,
`accepted`, `wrong_envelope_size_rejects`, `scope_stratum_rejects`,
`checker_rejects`, `bank_invalid_rejects`, `nonfinite_ESS_rejects`, and
`exhaustion`. A finite `ESS<100` is never a rejection: retain the task and mark
sharpness/completeness classifications `measurement_unreliable`.

## 6. Primary joint outputs

Do not publish a total score or a naive all-Pearson correlation matrix. The
primary unit is the latent task; its seven candidates are repeated measures.

### State occupancy

Report feasible joint-state frequencies, including:

1. **Informative but unobservable:** `S>=.10`, reliable, `O_P=0`.
2. **Atom-incomplete but informationally complete:** `C_atom=0`, reliable,
   `Delta S_miss<=.10`.
3. **Informative but limited-scope:** `S>=.10`, reliable,
   `H_valid*<=.90`.
4. **Weak but persistent:** `S<.10`, reliable, `H_valid*>=1.20`.
5. **Observable but informationally redundant:** for an atom-incomplete
   subset, `O_P=1`, reliable, `Delta S_miss<=.10`.

The absence of a state is also a result; it must not be treated as an integrity
failure.

### Conditional distributions and association map

- `P(S>=.10 | core coverage=1, reliable)`;
- `P(O_P=1 | S>=.10, reliable)`;
- `P(H_valid*>=h | S>=.10, reliable)` for predeclared horizons;
- `P(Delta S_miss<=.10 | C_atom=0, reliable)`;
- candidate-size-conditioned distributions of `(S, N_obs, H_valid*, Delta S_miss)`.

Use mixed-type association summaries and conditional distributions. Primary
strata are `candidate size × eta × scope stratum × generator`; any pooled
summary uses equal generator weighting. Latent-task clustered bootstrap is the
sole primary uncertainty method. Associations are not causal claims because
eta and scope strata are balanced controls.

### Structural/definitional dependency mask

Association displays must label or mask relations fixed partly/entirely by
definition, rather than presenting them as discoveries: core validity with any
axis (all rows condition on coverage one); candidate size with `C_atom`;
`S(P|D)` with `Delta S_miss`; `N_obs(P)` with `O_P`; and subset/full scope
direction under nesting. The empirical association panel is restricted to
non-definitional relations such as `S ↔ O_P`, `S ↔ H_valid*`,
`O_P ↔ H_valid*`, and censored-aware `Delta S_miss ↔ H_valid*`.

## 7. Expected semantics, not discoveries

Subset nesting entails `S(P_star|D)>=S(P_subset|D)` and
`H_valid*(P_subset)>=H_valid*(P_star)` under common atom semantics, horizon
grid, and first-failure rule. Both are integrity invariants. Store
`Delta H_scope=H_valid*(P_subset)-H_valid*(P_star)`; its magnitude/frequency,
alongside `Delta S_miss`, is empirical rather than the inequality direction.

## 8. Integrity sanity before full run

1. `P_star` is a unique maximal envelope with exactly three atom instances.
2. All seven subsets have coverage one on `Omega_0`.
3. Prefix, bank, weights, and ESS are identical for the seven rows of a task.
4. Nested sharpness, `Delta S_miss>=0`, and
   `H_valid*(P_subset)>=H_valid*(P_star)` pass numeric tolerance checks;
   `Delta H_scope` is stored as a joint-map field.
5. `S(P|D)` is invariant when requested by completeness and joint-map views.
6. Scope follows contiguous first failure and does not alter the sharpness
   target or provide future truth to the sharpness scorer.
7. E9 atom-evidence scoring receives no future target.
8. Scope quotas and every rejection/exhaustion reason are accounted for.
9. Floor/ESS/reliability labels sum exactly to candidate rows.
10. Scope endpoint and `Delta H_scope` censor states follow the frozen table;
    finite low-ESS rows are retained rather than rejected.

No expected scientific occupancy, monotonicity beyond logical nesting, or
association direction is a sanity gate.

## 9. Interpretation boundary and handoff

E13 can map valid-prior joint anatomy in this frozen grammar. It cannot infer
real-world prevalence, primitive-intrinsic rankings, complexity scaling,
multivariate transportability, prediction utility, safety, or LLM ability.

E9–E11 plus E13 describe valid-prior anatomy. E12-A/B describe how that
anatomy behaves after specification or content correctness fails. E14 should
then test complexity scaling, followed by real-data validation and only then
Prior Critic / LLM-RAG integration.
