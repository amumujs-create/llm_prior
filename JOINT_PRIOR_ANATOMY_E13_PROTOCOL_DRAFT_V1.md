# E13 — Joint Prior Anatomy Map

## Question

E9–E12 established separate operational axes using separate corpora. E13 asks
the next question on a **shared latent task**:

> Which combinations of validity, conditional information, structural
> observability, scope, grammar-relative completeness, numeric specification
> correctness, and structural-content correctness actually co-occur?

E13 estimates a joint map. It does not construct a total prior-quality score,
fit a prediction engine, or make a utility/safety claim.

## Why a new shared corpus is necessary

Rows from E9–E12 must not be pooled into a correlation matrix: their latent
tasks, scopes, generators, candidate banks, and acceptance rules differ. E13
instead generates one latent task and derives all candidate-prior rows from
that same task, prefix, clean continuation, paired ambient bank, and frozen
canonical grammar.

## Prior object and axes

For `P=(C, theta, Omega, q, pi)`, E13 records the following without reducing
them to one score.

| Axis | Row-level measure | Source semantics |
|---|---|---|
| Validity | coverage on clean continuation | E11/E12 oracle separation |
| Informativeness | `S(P|D)`, ESS, `N_survive`, `p_weighted` | frozen paired bank and fixed target grid |
| Observability | `E_struct` and thresholded `E_struct>=.80` | E9 structural-evidence checker |
| Scope | contiguous `H_valid*` | E10 first-failure rule |
| Completeness | `C_atom`, `Delta S_miss` | E11 unique-envelope rule |
| Specification correctness | valid / numeric-misspecified / not-applicable | E12-A field semantics |
| Content correctness | full / omission / false addition / reversal | E12-B operation catalog semantics |

`q` and `pi` are stored as declared metadata only in v1; calibration
provenance and open-world source reliability are not estimated.

## Shared-task design

### Base tasks

- Start from the eight E11 intended canonical triples and the three frozen
  generator families.
- Use one master clean trajectory, one master noisy observation grid, and one
  paired `M=4096` ambient bank per latent task.
- Reveal the common prefix `[0,.40]`; score continuation constraints on one
  fixed target grid. Scope uses the same clean trajectory and the E10
  contiguous horizon checker.
- Retain E11's canonical atom library, compatibility/scope registry, and
  unique inclusion-maximal compatible envelope rule.
- Vary predeclared structural separability and nested realization freedom to
  create evidence/multiplicity variation. These are generator controls, not
  universal difficulty scales.
- Independently inject local, medium, and persistent-within-tested-domain
  scope tiers. Scope is a controlled axis; E13 must not claim primitive
  persistence rankings from those tiers.

The final count and parameter ranges are deliberately **not frozen** in this
draft. They must be set only after a joint-measurement sanity suite shows that
all inherited checkers agree on the same latent task and common domains.

### Candidate rows derived from each base task

For each accepted base task, derive only candidates whose semantics apply;
non-applicability is recorded rather than filled with a fabricated value.

1. `P_full`: supplied valid intended composition.
2. Valid under-specific candidates: each singleton/pair subset of `P_full`.
3. Grammar envelope `P_star`: the unique maximal compatible
   coverage-preserving canonical envelope.
4. E12-B candidates: pre-frozen omission, compatible false-addition, and
   signed-reversal operations from a new E13 operation catalog.
5. E12-A candidates: numeric perturbations only for fields whose canonical
   instance has a frozen numeric specification. Other candidates receive
   `specification_status=not_applicable`.

This produces valid/incomplete, valid/complete, numeric-invalid,
content-invalid, local/persistent, observed/unobserved, and
informative/redundant states without claiming that every Cartesian combination
is logically or semantically feasible.

## Measurement rules

### Domain alignment

Before running, E13 must freeze one common target domain for sharpness,
validity, completeness, and structural evidence. The scope scan may extend
beyond that domain only as a separately labelled `H_valid*` measurement;
it must never silently change the satisfaction domain used for `S(P|D)`.

### Oracle/scorer separation

Clean future data are available only to generation/validation code for
coverage, scope, canonical-envelope selection, and violation severity. The
sharpness scorer receives only the noisy prefix, paired bank `(f_m,z_m)`, and
declared candidate prior. Utility, predictor outputs, RMSE, harm, and future
targets are prohibited from scoring.

### Reliability and censoring

- Preserve `ESS>=100` as the primary reliable-information condition.
- Record low-ESS as `measurement_unreliable`, not as weak/informational-null.
- Preserve floor lower/upper/unresolved rules by candidate relation:
  nested relaxation, nested restriction, or non-nested shift/reversal.
- Store `N_survive` and `p_weighted` for every candidate row.

## Predeclared joint analyses

No composite score or primitive leaderboard is allowed. All results are
descriptive, acceptance-conditioned, and clustered by latent task.

1. **Joint-state occupancy.** Report frequencies of feasible states, e.g.
   valid/informative/unobserved/incomplete; valid/redundant/persistent; or
   invalid-but-sharp with numeric versus content error labels.
2. **Pairwise and conditional maps.** Report conditional proportions and
   uncertainty for preregistered relations:
   - `P(S>=.10 | coverage=1)`;
   - `P(E_struct>=.80 | S>=.10, reliable)`;
   - `P(H_valid*>=h | S>=.10)` for predeclared horizons;
   - `P(Delta S_miss<=.10 | C_atom=0, reliable)`;
   - `P(S>=.10 | invalid, specification_status/content_operation)`.
3. **Association display.** Use a mixed-type association table (binary,
   ordinal, and continuous axes reported with their appropriate statistic),
   not a misleading all-Pearson correlation matrix.
4. **Conditional stratification.** Stratify all central findings by intended
   composition, generator, scope tier, separability control, and realization
   freedom before any equal-weight summary.
5. **Inference.** Use latent-task clustered/hierarchical bootstrap with
   equal-weight generator aggregation. E13 supports association, not causal
   claims about a control unless a separate factorial confirmation is run.

## Integrity sanity before full run

1. One base task produces byte-identical observations, bank, weights, and ESS
   for every derived candidate row.
2. Every axis uses its frozen checker and records its semantic type
   (phenomenological, mechanistic, or latent-assisted).
3. `P_full` coverage is one; envelope coverage is one; E12-B candidates meet
   their planned coverage pattern; inapplicable E12-A fields are explicitly
   absent rather than imputed.
4. Nested sharpness inequalities and all non-nested floor rules pass toy cases.
5. The same candidate's `S(P|D)` is invariant when requested by more than one
   derived analysis (e.g., E11 and E12-B view).
6. Scope first-failure logic and fixed-domain sharpness remain separated.
7. Joint-state counts, missingness, and reliability labels sum exactly to the
   accepted candidate rows.

## Interpretation boundary

E13 can establish which axis combinations occur in this frozen shared corpus
and which associations remain after declared stratification. It cannot show
real-world frequencies, identify one best prior, prove causal effects from
descriptive controls, establish complexity scaling, or determine predictive
utility/safety. Those are E14+, external validation, and downstream
integration questions.

## Success criterion

E13 succeeds if it turns the E9–E12 anatomy from a list of separately defined
axes into a reproducible shared-task joint map while preserving their distinct
semantics and reliability conditions.
