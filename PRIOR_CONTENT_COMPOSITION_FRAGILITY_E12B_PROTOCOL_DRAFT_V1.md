# E12-B — Content / Composition Fragility under Structural Misspecification

## Question

When a supplied structural prior is wrong in **content**, rather than in a
numeric realization, do omission, compatible false addition, and signed
reversal fail in the same way?

E12-B follows E12-A but does not extend its numeric perturbation grid. No onset,
bound level, event location, or asymptotic limit is moved here.

## Base object and fixed scope

Each base task has a supplied coverage-preserving true canonical composition
`P_full=A∧B∧C` under the frozen E11 grammar, in fixed `Omega=[.40,.80]` with
observed prefix `[0,.40]`. All structural candidates for that task share one
paired full-domain continuation bank `Q={(f_m,z_m)}_{m=1}^{4096}` and one
prefix likelihood-weight vector.

E12-B uses the same semantic distinction as E12-A:

- regime claims require paired candidate regime metadata;
- asymptote claims require paired candidate asymptotic metadata;
- direction, curvature, inflection, turning, and bounds use their frozen
  trajectory-level checkers.

The exact satisfaction registry, signed atom instances, event tolerances, and
compatibility/scope table must be hash-frozen before execution.

## Three deliberately separate structural operations

### Omission / under-specification

For every atom `A` in `P_full`, form `P_omit=P_full\{A}`. It removes a true
constraint without adding a false one.

Under the frozen AND semantics, oracle coverage must be preserved. The primary
quantity is information lost:

`L_omit(A|P_full)=S(P_full|D)-S(P_omit|D) >= 0`.

Omission is not labelled confidently wrong: it is a potentially weak but
coverage-preserving structural statement. Its scientific question is whether
the omitted true atom was conditionally redundant or materially informative.

### Compatible false addition / commission

For a frozen, task-family-specific canonical atom `C_false` that is compatible
with `P_full` but rejected by the clean oracle on `Omega`, form
`P_add=P_full∧C_false`.

This excludes the degenerate case of adding a logically incompatible atom that
no continuation could ever satisfy. `C_false` must be selected from a
predeclared **operation catalog**, not invented after inspecting an individual
task's future. The operation catalog records, for every intended composition,
the exact source atom IDs, candidate false-addition atom ID, semantic scope,
and expected clean-oracle falsity.

Because `P_add` is nested inside `P_full`, `S(P_add|D)-S(P_full|D) >= 0` is a
sanity relation. The relevant diagnosis is whether the false addition becomes
`coverage=0` while retaining `S>=.10 nat`: a structural confidently-wrong
candidate.

### Signed reversal

Where a true atom has a frozen signed counterpart, replace it with that
counterpart while leaving the remaining true atoms unchanged:

- decreasing ↔ increasing;
- convex ↔ concave;
- concave-to-convex inflection ↔ convex-to-concave inflection;
- maximum turning ↔ minimum turning;
- asymptote-from-above ↔ asymptote-from-below.

Reversal is admitted only when the reversed composition remains
**compatible-but-false** with its remaining true atoms. A logically
inconsistent reversal is not a structural-error test and is excluded. Reversal
is not generally nested in `P_full`; it uses the E12-A two-sided floor rule for
`Delta S_rev=S(P_rev|D)-S(P_full|D)` (exact / lower bound / upper bound /
unresolved). Regime and lower-bound have no artificial reversal in v1; they
are covered by compatible false-addition operations instead.

## Corpus and balanced operation catalog

Start from the eight E11 intended triples and three generator families. For
each exact triple × generator cell, request 30 accepted tasks. Before full
execution, a deterministic preflight must build and hash an operation catalog.
Each cell has a fixed maximum of 1,000 generation attempts. The catalog
satisfies all of the following for every planned operation:

1. the supplied `P_full` has clean coverage one;
2. each omission uses an atom actually present in `P_full`;
3. each false addition is grammar-compatible with `P_full`, is not logically
   contradictory, and is clean-oracle false on `Omega` for the controlled
   generator family;
4. each reversal uses a registered signed counterpart and is clean-oracle
   false while remaining compatible with all non-replaced atoms;
5. no operation changes the base clean trajectory, observations, bank, or
   likelihood weights.

The catalog describes an operation family, but every accepted task must repeat
the clean-oracle falsity check for its planned false addition/reversal. If a
candidate is accidentally valid for that trajectory, reject/redraw it with a
separate per-operation rejection count.

The frozen v1 catalog is [E12B_OPERATION_CATALOG_V1.json](E12B_OPERATION_CATALOG_V1.json).
It selects only signed canonical atom instances and records source-library
hashes; it does not access a realised future when choosing an operation.
Its builder executes the compatibility/scope registry contract: the frozen
global-scope semantics and its named atom library are asserted before pairwise
conflicts are checked, and clean-scope conjunction acceptance is rechecked for
every realised task. A change to a contract-relevant registry field (source
library, scope, global semantics, or compatibility rule) therefore hard-fails
catalog construction rather than silently changing compatibility semantics.

If a triple cannot support a required operation, it is not silently dropped.
The catalog must either assign a predeclared valid alternative or explicitly
exclude that operation family and report the denominator. This prevents false
addition difficulty from being confounded with uneven candidate-library size.

The E12-B estimand is explicitly **conditional on acceptance** of tasks for
which every registered operation meets its intended coverage/falsity and
compatibility condition. For every intended triple × generator cell, retain
`attempts`, `accepted`, `accidental_valid_rejects`, `compatibility_rejects`,
`checker_rejects`, `catalog_operation_exclusions`, and `exhaustion`. The
planned coverage pattern (`P_omit=1`, `P_add=0`, `P_rev=0`) is an integrity
invariant of this conditional corpus, not a scientific headline endpoint.

## Oracle and scorer separation

The clean trajectory may be used only to verify coverage and primitive-specific
violation severity during acceptance/validation. The scorer gets only observed
prefix data, the paired candidate bank, and a frozen candidate composition.
No future target, utility, prediction engine, or realization output enters the
scorer.

For every operation record:

- `Coverage` and primitive-specific `D_violation`;
- `S(P|D)`, `ESS`, saturation and floor flags;
- `N_survive` (unweighted satisfying-bank count) and `p_weighted` (weighted
  survival probability) before sharpness flooring;
- the operation-specific sharpness change relative to `P_full`;
- `confidently_wrong=I(Coverage=0, ESS>=100, S>=.10 nat)`;
- exact operation atom IDs, semantic type, and operation-catalog ID.

ESS must be identical across all operations for a base task; any difference is
an implementation failure.

`N_survive` and `p_weighted` are finite-bank support audits, not substitute
measures of sharpness. A floor-hit can reflect a restrictive candidate or
insufficient support in the 4,096-member reference bank; floor-aware changes
therefore remain lower/upper bounds or unresolved according to the frozen
rules below and are never silently interpreted as exact infinite sharpness.

### Inherited versus induced sharpness

For every invalid false-addition/reversal candidate with reliable `ESS>=100`,
classify its relation to the valid baseline (`S_full=S(P_full|D)`) using the
predeclared `.10 nat` threshold:

| Baseline `S_full` | Wrong candidate `S_wrong` | Class |
|---|---|---|
| `>=.10` | `>=.10` | inherited-sharp wrong |
| `<.10` | `>=.10` | induced-sharp wrong |
| `>=.10` | `<.10` | attenuated wrong |
| `<.10` | `<.10` | false-but-weak |

This prevents a high `S_wrong` from being interpreted as sharpness newly
caused by a false atom when the valid baseline was already sharp.

### Frozen floor and violation rules

Omission and false addition are nested; reversal is not.

| Operation | Exact relation | Floor rule |
|---|---|---|
| Omission | `P_full subset P_omit`, so `L_omit=S_full-S_omit>=0` | full-only floor: lower bound; both: unresolved; omit-only floor: integrity violation |
| False addition | `P_add subset P_full`, so `Delta S_add=S_add-S_full>=0` | add-only floor: lower bound; both: unresolved; full-only floor: integrity violation |
| Reversal | non-nested | E12-A four-way exact/lower/upper/unresolved rule |

`D_violation` is stored with an atom-family-specific semantic and never pooled
as a cross-family severity ranking: direction uses wrong-sign derivative
fraction; curvature uses wrong-sign second-derivative fraction; inflection and
turning use event-pattern mismatch; bounds use normalized boundary violation;
regime/asymptote use latent-mechanism mismatch severity. It may be compared
only within the same atom family and operation type.

## Primary comparisons

Primary results stratify by
`intended composition × operation type × target/source atom × generator`.
The three operation types must not be pooled into a single “structural error”
score.

False additions are intentionally unbalanced in v1: seven catalog cells add
`regime_postchange` and one adds `turning_maximum`. Therefore the added-atom
stratification is primary; any pooled false-addition result is supplementary
and must be described as an equal-weight summary of these declared atoms, not
as a general false-addition law.

1. **Omission:** coverage-preservation integrity and `L_omit`; distinguishes
   redundant from materially informative missing content.
2. **False addition:** coverage/falsity integrity, violation severity,
   sharpness gain, and confidently-wrong rate; distinguishes false-but-weak
   from false-and-sharp.
3. **Reversal:** coverage/falsity integrity, violation severity, and censored-aware
   `Delta S_rev`; captures non-nested directional structural error.

## Integrity sanity before full run

1. every `P_full` has coverage one;
2. every omission preserves coverage and cannot increase sharpness beyond
   numerical tolerance;
3. every false addition is compatible but clean-oracle false, rather than
   simply logically impossible;
4. every reversal has a frozen registered counterpart, compatible residual
   composition, and clean-oracle falsity;
5. paired-bank metadata semantics match the hashed registry;
6. prefix observations, target scope, bank, and weights are identical across
   operations of a task, including ESS equality;
7. nested addition/omission sharpness inequalities and non-nested floor rules
   pass deterministic toy cases;
8. operation-catalog exclusions/rejections, including accidental per-task
   validity, are logged by triple × generator × operation.
9. every operation row has finite `N_survive` and `p_weighted`, and every
   floor-hit remains auditable through those two quantities.
10. accepted full-run row counts match the catalog: 24 omission, 8 false-addition,
    and 17 reversal operations × 90 tasks per intent, yielding 4,410 operation
    rows plus 720 `P_full` baseline rows (5,130 total scoring rows), unless a
    cell exhausts its fixed attempt budget and is explicitly reported.

## Interpretation boundary

E12-B will test the asymmetry between **weakening by omission** and
**over-constraining with false structure**. It will not establish prediction
harm, real-world error frequencies, broad structural-family rankings, or LLM
proposal quality. Those remain later integration/evaluation questions.
