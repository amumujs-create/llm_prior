# E10 — Prior Scope / Validity Horizon (draft v1)

## Purpose

E10 asks a different question from E9. For a **supplied locally valid
structural prior**, over what future domain does its declared constraint remain
valid? The object is scope, not conditional information, prediction accuracy,
or safe deployment.

`E9: when does a supplied valid prior add information beyond a prefix?`

`E10: until which future horizon does a supplied locally valid prior remain structurally valid?`

The v1 conclusion will remain grammar-relative to the 1D progression-to-scalar
primitive grammar.

## Scope semantics

Fix one observation boundary `b=.40`. For every task and tested horizon `h`,

`V_P(h) = 1` iff the supplied constraint passes its raw validity check over
**the whole closed interval** `[b,h]`; otherwise `V_P(h)=0`.

Raw threshold checks may be nonmonotone: a direction check can fail at one
horizon and later exceed its percentage threshold again. E10 therefore derives
a separate contiguous-validity process,

`C_P(h_j) = product_{k<=j} V_P(h_k)`,

and defines the endpoint as the maximum tested horizon before the **first
scope failure**,

`H_valid* = max { h_j in H : C_P(h_j)=1 }`.

It is not the last individual point at which a raw condition happens to
reappear. Once scope fails, `H_valid*` is never recovered. Raw `V_P(h)` is
stored as a supplementary diagnostic precisely so that nonmonotone checker
behavior remains visible rather than silently rewritten.

The frozen candidate horizon grid is

`H={.45,.50,.60,.70,.80,.90,1.00}`.

`H_valid*` is grid-resolved. If validity fails first at `.70`, the actual
scope end lies in `(.60,.70]`; if valid through `1.00`, report
**persistent within the tested domain**, never globally persistent.

## Supplied constraint and primitive-specific validation

Each generated task supplies one primitive-level structural constraint with
its declared sign/bound/onset semantics. The oracle validator sees the **clean
latent trajectory only** for this scope label; observation noise, utility,
prediction engines, fitting, and data-conditioned continuation ensembles are
not part of E10.

| Primitive | E10 validity condition over `[b,h]` |
|---|---|
| Direction | Declared derivative sign holds on at least 95% of dense-grid intervals. |
| Curvature | Declared second-derivative sign holds on at least 90% of dense-grid intervals. |
| Inflection | The primary inflection occurred before `b`; no additional curvature-sign transition occurs in the interval. |
| Turning | The primary turning point occurred before `b`; no additional derivative-sign transition occurs in the interval. |
| Regime | The primary onset occurred before `b`; the latent mechanistic identifier remains the declared post-onset regime. Phenomenological curve checks are supplementary only. |
| Bound | The supplied registered one-sided bound is satisfied at every dense-grid point. |
| Asymptote | Latent-assisted convergence law remains active, with slope decay and approach-to-limit satisfying frozen tolerance. |

Event-type priors therefore never fail merely because their primary event has
not happened yet: all are generated in an already-valid post-event state at
the boundary. The regime/asymptote rows are explicitly mechanistic/latent-
assisted scope labels. They will never be pooled as identical to purely
phenomenological derivative constraints.

## Controlled scope tiers

Each task starts with a trajectory whose supplied primitive is valid on the
first tested interval `[.40,.45]`. A predeclared generator-side scope
intervention then introduces a single primitive-specific violation event after
a chosen validity tier:

| Intended tier | Intended endpoint region | Interpretation |
|---|---|---|
| Local | `.45–.60` | Constraint is valid near the boundary only. |
| Medium range | `.70–.90` | Constraint survives a nontrivial but finite continuation. |
| Persistent-within-domain | `1.00` | No injected violation before the tested endpoint. |

Examples: direction receives a smooth turning/flattening violation; curvature
receives a curvature-sign change; regime receives a second regime switch;
bound crosses the supplied registered bound; asymptote receives a renewed
drift away from its declared limit. The intervention must have compact support
after its declared onset `tau_v`: it must not change the trajectory before
`tau_v`, and must satisfy at least value continuity at the splice. Each
primitive must predeclare whether `C1` or `C2` splice continuity is needed
(curvature requires the stricter rule). The exact parameter values, duration,
and tolerance are frozen by primitive before a full run. They are chosen by
generation, **not** selected using measured `H_valid*`.

## Corpus (proposed freeze)

`7 primitives × 3 intended scope tiers × 3 generator realizations × 30 seeds
= 1,890 independent latent tasks.`

The scope tier is a generator control, not a claim that the three tiers have
equal empirical difficulty across primitives. Generator results are always
reported separately and macro-averaged equally.

## Numeric execution freeze

The exact constants are stored in [E10 frozen configuration](E10_FROZEN_CONFIG_V1.json).
The first tested horizon is `.45`; every accepted task must satisfy its raw
scope checker there. Local violation onset is sampled in `[.52,.57]`, medium
onset in `[.72,.82]`, and persistent-within-domain tasks have no injected
violation through `1.00`. The clean validation grid has 401 points. Direction
and curvature use 95% and 90% sign-fraction criteria; the bound tolerance is
1% of the clean target range. Event-count and latent-mechanism checks are
frozen as specified in the JSON table.

## Predeclared outputs

1. Integrity: accepted task count, validation failures, per-primitive checker
   recovery, and endpoint toy cases.
2. Scope measurement: `V_P(h)` attainment/survival curves and the distribution
   of `H_valid*`, including grid brackets and terminal persistent-within-domain
   fraction.
3. Scope anatomy: primitive × intended scope tier × generator; no global
   primitive ranking.
4. Generator robustness: agreement of scope class and horizon distributions
   across spline/basis/ODE realization families.

## Predeclared interpretation boundary

E10 measures **structural scope only**. It cannot say whether a prior is
informative (E9), complete (E11), robust to misspecification (E12), useful,
safe, or compatible with any realization engine. A prior may have a long
validity horizon yet have little incremental information; a locally valid prior
may still be useful within its scope only after a later deployment experiment.

## Required freeze and sanity before execution

Before execution, write a numeric checker table for each primitive: derivative
tolerances, minimum event duration, dense validation-grid size, onset/limit
metadata convention, splice-continuity order, and local/medium violation
parameter ranges. Then run a small integrity suite verifying: (1) the first
tested interval `V_P(.45)=1`; (2) event-type primary events occur before `.40`;
(3) intended local/medium tasks have the expected grid bracket rather than a
future-selected endpoint; (4) persistent-within-domain tasks retain validity
through `1.00`; (5) raw re-entry cannot recover contiguous `H_valid*`; and
(6) generator labels and clean-oracle validators remain separate from any
future engine/utility code.
