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
- E13 uses the dedicated persistent-base and smooth post-`.80` scope generator
  frozen in `E13_SCOPE_GENERATOR_FREEZE_V1.md`; E11's generator is not reused
  as a scope corpus.
- One task receives one master noisy observation grid, one frozen paired
  `M=4096` continuation bank, and one likelihood-weight vector shared by every
  non-empty true subset of its realized envelope. The primary scorer uses one full five-active-
  coordinate ambient-bank convention, consistent with E11/E12; E9's
  `DoF=1/3/5` views are supplementary task metadata rather than parallel E13
  rows. ESS must consequently be byte/numerically identical within a task.
- The E11 canonical atom library and compatibility/scope registry are reused
  unchanged. The intended triple is the generator condition, not necessarily
  the realized envelope size. A task is accepted when it has one unique
  inclusion-maximal compatible coverage-preserving envelope `P_star`.
  Canonically implied or otherwise incidental valid atoms are retained, not
  suppressed. Store `generator_intended_atoms`, `oracle_envelope_atoms`,
  `oracle_envelope_size`, and `implied_atoms=P_star-intended_atoms`.

## 3. All valid subset priors per task

For an accepted oracle envelope of size `k_star`, score every non-empty true
subset on `Omega_0`: `2^k_star-1` candidates. Every candidate has core coverage
one. Its canonical atom completeness is deterministic
(`C_atom(P)=I(P=P_star)`), while
their conditional informational completeness remains empirical:

`Delta S_miss(P)=S(P_star|D)-S(P|D)`.

E11's nested floor rule is retained: if neither candidate is floor-hit, the
gap is exact; `P_star`-only floor-hit gives a lower bound; both floor-hit is
unresolved; and subset-only floor-hit is an integrity violation. The `.10 nat`
informational-completeness label is primary only for reliable, exact rows;
censored gaps are unresolved.

No numeric perturbation, false addition, or reversal enters these rows.
Where applicable, E12-A/B are cited only in final interpretation as evidence
about what happens when this valid-prior anatomy is perturbed into invalidity.

E13 therefore estimates `P(S, O, H, Delta S_miss | V_Omega0=1)`. Validity is
an acceptance condition here, not a varying association axis.

## 4. Joint measurements

| Axis | Measurement | E13 semantics |
|---|---|---|
| Validity | core coverage | every non-empty true-subset row must equal one on `Omega_0` |
| Informativeness | `S(P|D)`, primary threshold `.10 nat` | `ESS>=100` required for reliable interpretation; record `N_survive`, `p_weighted`, and floor state |
| Observability | atom-level `E_a` | reuse E9 checker; record candidate-specific `N_obs(P)=sum_{a in P} I(E_a>=.80)` and `O_P=I(min_{a in P} E_a>=.80)`; store oracle `N_obs*`, `O*` as task context |
| Scope | contiguous `H_valid*(P)` | clean scope scan at `.85,.90,1.00,1.10,1.20`; sharpness remains fixed on `Omega_0` |
| Completeness | `C_atom`, `Delta S_miss` | informationally complete iff reliable, gap-status exact, and `Delta S_miss<=.10 nat` |

Scope is intentionally measured beyond `.80` while sharpness remains on
`.40-.80`; this prevents a moving future target from confounding `S(P|D)`.
The scope scan uses E10's contiguous first-failure rule.

`H_valid*` is the **last contiguous valid horizon**, with `.80` as its initial
core endpoint: first failure at `.85/.90/1.00/1.10/1.20` yields
`.80/.85/.90/1.00/1.10`, respectively. No failure through `1.20` is recorded
as `H_valid*>1.20` (right-censored), never as an exact value `1.20`.
For the `P_star` row itself, `Delta H_scope(P_star)=0` is exact by identity,
even if its `H_valid*` is right-censored. For proper subsets only,
`Delta H_scope=H_valid*(P_subset)-H_valid*(P_star)` follows this rule: both
observed endpoints give an exact difference; observed full plus censored subset
gives a lower bound; both censored is unresolved; censored full plus observed
subset is a nesting integrity violation. “Weak but persistent” means no scope
failure through `1.20`, not `H_valid*>=1.20` as an exact assertion.

Every candidate row stores `delta_H_scope_status={exact,lower_bound,unresolved}`
and either `delta_H_scope_value` or `delta_H_scope_bound`; a censored bound is
never written as an exact numeric difference.

Candidate states use `O_P`, not oracle-wide `O*`: an observable pair `A and B`
is not labelled unobservable merely because omitted oracle atom `C` lacks
evidence. Oracle-wide observability remains a task-level context field.

## 5. Controlled variation and corpus

Reuse E9's frozen structural-separability control `eta` at its existing low,
medium, and high values; do not retune numeric values. Reuse nested realization
freedom only as a stored multiplicity control, not as a primary factorial
quota. Scope variation is balanced by acceptance stratification of the full
envelope `P_star`:

`eta` is a shared task-level evidence-contrast level, not a claim that the
three atoms have equal realised difficulty. Apply the same frozen low/mid/high
E9 `eta` value to each atom's own primitive-specific prefix evidence template
and checker, retaining `E_A,E_B,E_C` separately. Realised evidence values are
outcomes, not selected labels.

| Scope stratum | Full-prior condition |
|---|---|
| Limited | `H_valid*(P_star)<=.90` |
| Intermediate | `H_valid*(P_star)` in `{1.00,1.10}` |
| Persistent-within-tested-domain | no failure through `1.20` |

Every accepted task remains valid on `Omega_0`. Scope stratum is a controlled
map condition—not an estimate of natural scope prevalence.

The frozen full corpus is:

`8 triples × 3 generators × 3 eta levels × 3 scope strata × 10 seeds`

`= 2,160 latent tasks`. A deterministic preflight over accepted task seeds
freezes the realized-envelope-size distribution and expected candidate count:

`N_rows = sum_t (2^{|P_star,t|}-1)`.

The earlier E11-derived envelope preflight is retained only as a debug
provenance artifact. The final expected row count is frozen only after the
dedicated scope-aware persistent-base preflight accepts measured strata.

Each fine cell has at most 2,000 generation attempts. Store `attempts`,
`accepted`, `ambiguous_envelope_rejects`, `scope_stratum_rejects`,
`checker_rejects`, `bank_invalid_rejects`, `nonfinite_ESS_rejects`, and
`exhaustion`. A finite `ESS<100` is never a rejection: retain the task and mark
sharpness/completeness classifications `measurement_unreliable`.

## 6. Primary joint outputs

Do not publish a total score or a naive all-Pearson correlation matrix. The
primary unit is the latent task; its candidates are repeated measures. In every
primary pooled analysis, candidate `P` in task `t` receives within-task weight
`1/(2^{|P_star,t|}-1)`, followed by equal generator weighting. Thus tasks with
larger envelopes do not receive extra pooled influence simply because they
yield more subsets.

### State occupancy

Report feasible joint-state frequencies, including:

1. **Informative but unobservable:** `S>=.10`, reliable, `O_P=0`.
2. **Atom-incomplete but informationally complete:** `C_atom=0`, reliable,
   `gap_status=exact`, `Delta S_miss<=.10`.
3. **Informative but limited-scope:** `S>=.10`, reliable,
   `H_valid*<=.90`.
4. **Weak but persistent:** `S<.10`, reliable, no scope failure through `1.20`.
5. **Observable but informationally redundant:** for an atom-incomplete
   subset, `O_P=1`, reliable, `gap_status=exact`, `Delta S_miss<=.10`.

The absence of a state is also a result; it must not be treated as an integrity
failure.

### Conditional distributions and association map

- `P(S>=.10 | core coverage=1, reliable)`;
- `P(O_P=1 | S>=.10, reliable)`;
- `P(C_P(h)=1 | S>=.10, reliable)` for predeclared horizons;
- `P(Delta S_miss<=.10 | C_atom=0, reliable, gap_status=exact)`;
- `P(gap_status=exact | C_atom=0, reliable)` as the completeness-classification
  audit denominator;
- oracle-envelope-size × omitted-count-conditioned distributions of
  `(S, N_obs, Delta S_miss)` and
  censored-aware scope profiles `P(C_P(h)=1)`. Right-censored `H_valid*>1.20`
  is never replaced by `1.20` for a numeric mean or median.

Use mixed-type association summaries and conditional distributions. Primary
strata are `oracle envelope size × omitted count × eta × scope stratum × generator`;
any pooled summary uses the frozen within-task and equal-generator weights.
Latent-task clustered bootstrap is the
sole primary uncertainty method. Associations are not causal claims because
eta and scope strata are balanced controls.

### Structural/definitional dependency mask

Association displays must label or mask relations fixed partly/entirely by
definition, rather than presenting them as discoveries: core validity with any
axis (all rows condition on coverage one); candidate size with `C_atom`;
`S(P|D)` with `Delta S_miss`; `N_obs(P)` with `O_P`; and subset/full scope
direction under nesting. The empirical association panel is restricted to
non-definitional relations such as `S ↔ O_P`, `S ↔ C_P(h)`,
`O_P ↔ C_P(h)`, and censored-aware `Delta S_miss ↔ C_P(h)`.

## 7. Expected semantics, not discoveries

Subset nesting entails `S(P_star|D)>=S(P_subset|D)` and
`H_valid*(P_subset)>=H_valid*(P_star)` under common atom semantics, horizon
grid, and first-failure rule. Both are integrity invariants. Store
`delta_H_scope_status={exact,lower_bound,unresolved}` and its corresponding
exact value or lower bound; its magnitude/frequency, alongside `Delta S_miss`,
is empirical rather than the inequality direction.

## 8. Integrity sanity before full run

1. `P_star` is a unique maximal envelope under the unchanged E11 grammar;
   realized-envelope size and implied atoms are recorded.
2. All non-empty subsets have coverage one on `Omega_0`.
3. Prefix, bank, weights, and ESS are identical for all rows of a task.
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
