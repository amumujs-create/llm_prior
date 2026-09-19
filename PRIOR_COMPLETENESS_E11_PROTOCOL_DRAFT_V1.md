# E11 — Grammar-Relative Prior Completeness (draft v1)

## Question

Within one fixed declared scope, how much valid structural information does a
supplied prior omit relative to the **unique inclusion-maximal compatible
coverage-preserving envelope** available in the frozen canonical grammar?

E11 is not an attempt to name the one true prior. Its object is explicitly
grammar-relative completeness:

`Completeness(P_s | G, Omega, D)`,

where `G` is the seven-primitive 1D grammar and `Omega` is held fixed for every
candidate comparison.

## Fixed scope and data/reference convention

- Declared validity scope: `Omega=[.40,.80]`.
- Observed prefix for conditional sharpness: `[0,.40]` on one frozen noisy
  master grid; the same prefix observations, temperature, and one `M=4096`
  continuation bank are shared by every candidate from the same latent task.
- Conditional-prior satisfaction is always checked on the same target scope
  `Omega`, never on a candidate-specific or shrinking domain.
- E11 has no prediction engine, RMSE, utility, harm, or selection target.

This scope convention is mandatory: comparing a supplied constraint valid only
through `.80` to an oracle envelope scored through `1.00` would confound
missing structural content with scope length.

## Corpus and candidates

Use the eight already registered compatible triples from the benchmark grammar
as **generator intents**:

`direction+curvature+bound`, `direction+curvature+asymptote`,
`direction+inflection+bound`, `direction+inflection+asymptote`,
`curvature+bound+asymptote`, `inflection+bound+asymptote`,
`turning+bound+asymptote`, and `regime+bound+asymptote`.

For each triple, generator, and latent seed, generate a clean trajectory that
preserves the intended triple across `Omega`. Proposed corpus:

`8 triples × 3 generators × 30 seeds = 720 latent tasks.`

For each task, evaluate all nonempty supplied subsets of the intended triple:
three singleton priors, three pairs, and the intended full triple. The
grammar-oracle envelope is evaluated separately. Thus there are eight
candidate/envelope evaluations per task, or 5,760 shared-bank measurements.
Each intended triple × generator cell requests 30 accepted tasks, permits at
most 1,000 deterministic generation attempts, and stores requested tasks,
attempts, ambiguous-envelope rejects, coverage/checker rejects, and exhaustion.
Rejection rates are reported by triple × generator as an integrity diagnostic
for corpus-selection bias, not hidden by redraws.

## Two completeness axes

E11 does not collapse “contains every valid grammar atom” and “leaves little
conditional information missing” into one label.

- **Canonical atom completeness:** `C_atom(P_s)=1` iff the canonical
  atom set of `P_s` equals the canonical atom set of `P_star` on `Omega`.
- **Informational completeness:** assessed from `Delta S_miss` only when its
  sharpness measurement is reliable and non-saturated. With the predeclared
  practical threshold `delta_info=.10 nat`, informationally complete means
  `Delta S_miss <= .10`; informationally incomplete means `Delta S_miss > .10`.

Thus `P_s != P_star` with a small reliable gap is **atom-incomplete but
informationally complete**. This is an expected E11 state, not a contradiction.
All outputs retain `C_atom`, raw `Delta S_miss`, reliability/floor flags, and
the thresholded informational status as separate fields.

## Canonical content atoms and oracle envelope

E11-v1 is **content completeness only**, not specificity completeness. Its
envelope universe is deliberately separate from the old size-≤3 benchmark
composition registry. The frozen
[canonical atom library](E11_CANONICAL_ATOM_LIBRARY_V1.json) contains signed
direction/curvature/event instances, fixed `0` lower/upper bounds, and sided
asymptotes. It contains no oracle-selected interval center, width, onset, rate,
scale, exponent, or parameter precision.

Specificity ladders such as direction-plus-rate range or regime onset intervals
are excluded. The oracle may determine whether a predeclared canonical atom is
valid; it may not construct an atom instance after looking at the future.

Let `V_G_E11(f,Omega)` be every canonical atom from that frozen library whose
oracle checker accepts the clean latent continuation throughout `Omega`.

`P_star` is not constructed by blindly conjoining every individually valid
atom. It is the **unique inclusion-maximal compatible envelope** in the E11
atom universe. Formally, enumerate all compatible subsets `C` of
`V_G_E11(f,Omega)` such that the intended triple is a subset of `C`; retain a
set for which no strictly larger compatible eligible superset exists. A task is
accepted only if this maximal set is unique. If no such envelope exists or two
incomparable maximal envelopes exist, reject and deterministically redraw the
latent task; do not choose an envelope after inspecting sharpness or by atom
count.

This rule ensures that every supplied candidate subset remains contained in the
same task-level `P_star`, preserving the nested probability relation used by
`Delta S_miss`. It also prevents event-type atoms from acquiring incompatible
conjunction semantics merely because each individual checker passed.

`P_star` may contain the intended triple plus additional grammar-valid
constraints. This is intentional: an intended-full candidate can still be
grammar-incomplete. Mechanistic regime and latent-assisted asymptote
constraints may enter `P_star` only under their preregistered oracle semantics;
they are flagged and never silently treated as phenomenological labels.

Every atom in `P_star` is stored with provenance: `intended_atom` if it belongs
to the generator's intended triple, otherwise `incidental_valid_atom`. The
latter is an observed grammar-valid consequence, not hidden generator truth.

Every supplied subset must be verified coverage-preserving on `Omega` before
it is admitted to the corpus. The candidate and `P_star` use the same task,
prefix, scope, and bank.

## Metrics

Conditional sharpness is

`S(P|D) = -log Pr_Q[f satisfies P on Omega | D]`.

The missing valid information of supplied prior `P_s` is

`Delta S_miss(P_s) = S(P_star|D)-S(P_s|D)`.

Interpretation:

- `Delta S_miss≈0`: omitted valid grammar constraints add little conditional
  restriction under this data/reference ensemble.
- large `Delta S_miss`: supplied prior is coverage-preserving but omits
  substantial valid grammar-relative information.

### Measurement reliability and floor saturation

The shared weighted continuation bank records `ESS` for every task. The primary
informational-completeness analysis is restricted to `ESS>=100`; all-task
numbers are explicitly supplementary. A small gap at `ESS<100` is
**measurement-unresolved**, not evidence of informational completeness.

Sharpness uses the frozen Laplace/floor estimate with `M=4096`, `.5`
pseudocount, denominator offset `1.0`, and `p_min=1/(10M)`. Record candidate
and oracle-envelope floor-hit flags. If `P_star` is floor-saturated while
`P_s` is not, `Delta S_miss` is a lower bound: classify informationally
incomplete only if this lower bound exceeds `.10 nat`; otherwise classify the
information status as unresolved. If both `P_s` and `P_star` floor-hit,
informational completeness is unresolved even if the reported difference is
zero. Floor-hit cases are never classified informationally complete from the
truncated sharpness difference.

For every missing `B in P_star \ P_s`, report immediate marginal information

`Delta S(B|P_s)=S(P_s AND B|D)-S(P_s|D)`.

This is context-dependent and is not assumed to sum to `Delta S_miss`; it
exposes redundancy and interaction rather than replacing the envelope gap.

## Reporting cross-classification

Report canonical-atom status and information status as a cross-classification,
never as one four-class label. Examples include:

- atom-incomplete + reliable large gap;
- atom-incomplete + reliable negligible gap;
- intended-full-but-extra-valid + reliable large/small gap;
- grammar-complete + zero gap;
- any structural status + ESS/floor unresolved information status.

None of these states claim completeness outside the frozen grammar: scaling,
memory, conservation, interactions, and other out-of-vocabulary knowledge are
not represented.

## Required execution freeze and sanity

Before a full run, freeze primitive-specific clean-scope truth checkers and
the shared-bank sharpness estimator (including Laplace constants/floor). The
sanity suite must verify:

1. every supplied subset and `P_star` has coverage 1 on `Omega`;
2. the same prefix observations, bank, weights, and `Omega` are reused across
   all candidates within a task;
3. conjunction monotonicity `S(A AND B|D)>=S(A|D)` has zero violations up to
   numerical tolerance;
4. `Delta S_miss>=0` up to the same tolerance;
5. when `P_s=P_star`, `Delta S_miss≈0`;
6. `C_atom` and informational status remain distinct for a synthetically
   redundant missing atom;
7. candidate/oracle floor-hit handling yields lower-bound or unresolved rather
   than false informational-completeness labels;
8. nested floor consistency: `candidate floor-hit AND oracle non-floor-hit`
   occurs zero times, up to the frozen numerical tolerance;
9. every accepted task has one unique inclusion-maximal compatible envelope and records
   intended versus incidental atom provenance;
10. rejection accounting and the fixed 1,000-attempt cap are populated for
    every intended triple × generator cell;
11. no utility, engine, prediction, future-RMSE, or far-OOD target enters
   scoring.

The complete execution semantics, exact intended atom IDs, hash provenance,
unique-envelope-conditioned estimand, and rejection accounting are frozen in
[E11 execution freeze](E11_EXECUTION_FREEZE_V1.md).

## Interpretation boundary

E11 measures missing structural information **inside a fixed scope and frozen
grammar**. It does not establish that an oracle envelope is the world's best
scientific prior, that it can be identified from available data, that it is
robust to misspecification, or that it improves extrapolation after a
realization engine is chosen.
