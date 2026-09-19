# E11 — Grammar-Relative Prior Completeness (draft v1)

## Question

Within one fixed declared scope, how much valid structural information does a
supplied prior omit relative to the most restrictive coverage-preserving
envelope available in the frozen grammar?

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

Use the eight already registered compatible triples from the benchmark grammar:

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

## Oracle envelope

Let `V_G(f,Omega)` be every primitive constraint in the frozen grammar whose
oracle checker accepts the clean latent continuation throughout `Omega`.

`P_star = AND_{P in V_G(f,Omega)} P`.

`P_star` may contain the intended triple plus additional grammar-valid
constraints. This is intentional: an intended-full candidate can still be
grammar-incomplete. Mechanistic regime and latent-assisted asymptote
constraints may enter `P_star` only under their preregistered oracle semantics;
they are flagged and never silently treated as phenomenological labels.

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

For every missing `B in P_star \ P_s`, report immediate marginal information

`Delta S(B|P_s)=S(P_s AND B|D)-S(P_s|D)`.

This is context-dependent and is not assumed to sum to `Delta S_miss`; it
exposes redundancy and interaction rather than replacing the envelope gap.

## Completeness states

1. Valid, incomplete, large missing information.
2. Valid, incomplete, small missing information (omitted constraints are
   conditionally redundant).
3. Intended-full but grammar-incomplete (`P_star` contains additional valid
   grammar constraints).
4. Grammar-complete (`P_s=P_star` or `Delta S_miss` is within frozen numerical
   tolerance).

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
6. no utility, engine, prediction, future-RMSE, or far-OOD target enters
   scoring.

## Interpretation boundary

E11 measures missing structural information **inside a fixed scope and frozen
grammar**. It does not establish that an oracle envelope is the world's best
scientific prior, that it can be identified from available data, that it is
robust to misspecification, or that it improves extrapolation after a
realization engine is chosen.
