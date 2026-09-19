# Prior Anatomy Framework v1

## Purpose and scope

This document synthesizes what E9–E12 operationally established about
**structural extrapolation priors** in the frozen 1D progression-to-scalar
grammar. It is not a universal prior theory, a deployment prescription, or a
single prior-quality score.

The central claim is deliberately plural:

> A structural prior is a multidimensional object. Its validity, conditional
> information, observability, scope, grammar-relative completeness, numeric
> specification, and structural content can differ and can fail in different
> ways.

## Prior object

Represent a supplied structural prior as

`P = (C, theta, Omega, q, pi)`.

| Component | Meaning |
|---|---|
| `C` | structural content: canonical atom conjunction / constraint grammar |
| `theta` | numeric specification, such as event location, bound, onset, or limit |
| `Omega` | declared validity scope |
| `q` | calibration/uncertainty or specificity attached to the declaration |
| `pi` | provenance: how the prior was supplied and what supports it |

E9–E12 directly study `C`, `theta`, and `Omega`; `q` is represented only in
controlled specification states and `pi` remains a downstream/open-world
axis. All sharpness statements are conditional on a frozen reference ensemble
and observed prefix `D`.

## Seven axes

| Axis | Question | Operational measure | Evidence / boundary |
|---|---|---|---|
| Validity | Does `P` retain the realised continuation? | Coverage | Required for accepted base priors; does not imply other axes. |
| Informativeness | How much continuation space does `P` remove after `D`? | `S(P|D)` | E9, E11, E12; ensemble- and reliability-conditional. |
| Observability | Does the prefix reveal the structure? | `E_struct`, `E_obs*` | E9; distinct from information onset. |
| Scope | How far does validity persist? | contiguous `H_valid*` | E10; clean-oracle and within tested domain. |
| Completeness | What valid grammar information is missing? | `C_atom`, `Delta S_miss` | E11; grammar-relative and unique-envelope conditional. |
| Specification correctness | Is numeric `theta` correct while content is held fixed? | coverage / violation vs `epsilon` | E12-A; controlled calibration geometry. |
| Content correctness | Is the structural conjunction correct? | omission / addition / reversal operations | E12-B; frozen operation catalog conditional. |

These axes must not be collapsed into a scalar “prior quality.” In particular,
high sharpness may coexist with invalidity; canonical incompleteness may
coexist with informational completeness; and local validity is not persistent
validity.

## Empirically established separations

### E9 — information is not structural observation

E9 separated prior-added information onset `E_add*` from structural-observation
onset `E_obs*`. In the frozen corpus, `E_add*` was attained for 99.3% of tasks
(median `.20` among attained cases), whereas `E_obs*` was attained for 9.6%
(median `.40`). External-informative states dominated reliable measurements.
This supports the operational separation:

`validity != informativeness != observability`.

It does **not** say that 20% support is generally sufficient, that the prior is
safe/useful, or that low observation proves a prior strong. E9 had a substantial
low-ESS tail and did not measure utility.

### E10 — validity is not scope

E10 defines scope by a contiguous first-failure horizon `H_valid*`, not by the
last point that happens to satisfy a percentage checker. Its intentionally
injected local, medium, and persistent-within-tested-domain tiers were recovered
across spline/basis/ODE with 100% coarse-class agreement. The supported
separation is:

`valid now != valid far away`.

This validates the scope measurement apparatus and establishes `Omega` as part
of the prior object. It is not evidence that any primitive is intrinsically more
persistent in real systems, and E9/E10 did not share a corpus; no empirical
information-by-scope quadrant is estimated yet.

### E11 — validity is not completeness or conditional information

E11 distinguished canonical atom completeness from conditional informational
completeness. In its controlled grammar-relative corpus, 41.6% of
atom-incomplete supplied candidates were informationally complete at the
predeclared `.10 nat` rule, while 48.3% were informationally incomplete
(10.1% measurement-unresolved). Therefore:

`validity != canonical content completeness != conditional informational completeness`.

The result is conditional on the fixed grammar, fixed scope, reference ensemble,
and unique inclusion-maximal compatible envelope. It is not world completeness.

### E12-A — numeric invalidity need not weaken a prior

E12-A changed numeric specification while holding content fixed. In all 2,430
observed signed break cases, the invalidity and confidently-wrong endpoints
coincided under the frozen `.10 nat` criterion. The inheritance audit matters:
all 1,350 baseline specification states already had `S(P_0|D) >= .10 nat`.

Thus E12-A supports: `loss of specification validity does not imply loss of
conditional sharpness`. It does **not** show that numeric misspecification
created confidence; the sharp baseline remained sharp after becoming invalid.

### E12-B — structural errors are not one information failure mode

E12-B compared three operations on the accepted frozen corpus:

| Operation | Set relation | Empirical result |
|---|---|---|
| Omission | nested relaxation | `L_omit` median `.452`, IQR `[0,1.350]` nat; magnitude is heterogeneous. |
| Compatible false addition | nested restriction | `Delta S_add` median `.499`, IQR `[0,.803]` nat; magnitude is context-dependent. |
| Signed reversal | non-nested | 19.7% materially decreased, 31.5% near-zero, 48.8% materially increased `Delta S_rev`. |

The signs for omission and addition follow from AND/nested-set semantics; their
magnitudes are empirical. Reversal had strongly source- and context-dependent
variation, not a uniform increase. All 2,250 invalid addition/reversal rows
were classified inherited-sharp: valid baselines and wrong candidates both
exceeded `.10 nat`. Nested addition makes this persistence structurally
consistent; for reversal it is an empirical observation. E12-B therefore does
not show that false content itself generates confidence.

## Three-layer organization

| Layer | Axes | Core question |
|---|---|---|
| Truth & coverage anatomy | validity, scope, specification correctness, content correctness | What does the prior claim, and where/how does it agree with the continuation? |
| Information anatomy | informativeness, completeness | How much continuation space is removed, and what grammar-relative information is absent? |
| Evidence anatomy | observability; later identifiability | What does the observed prefix reveal or determine about the prior? |

Only after these prior-side layers should downstream work evaluate translation,
integration, realization engine compatibility, predictive utility, safety,
selection, LLM proposal, or RAG provenance.

## What remains unresolved

- Joint relationships: E9–E12 generally use different corpora, so they define
  axes but do not estimate every task-level interaction.
- Grammar dependence: v1 excludes scaling, conservation, memory, periodicity,
  multivariate interactions, and open-world primitives.
- Complexity scaling, real-world prevalence, and multidimensional settings.
- Identifiability beyond E9's structural-observation endpoint.
- Calibration/provenance `q, pi`, translation fidelity, integration, engine
  compatibility, utility, harm, and safe abstention.
- Whether an LLM/RAG proposer can propose high-coverage, informative priors in
  unseen structural spaces.

## Downstream handoff

The framework gives a non-circular target for later systems:

`LLM/RAG proposes P -> evaluator estimates applicability of P -> realization engine uses or abstains`.

A downstream evaluator must not equate prior truth with safety. It should
separately assess coverage plausibility, information, evidence/identifiability,
scope, completeness, calibration, and engine/context-specific utility.

## Source experiments

- [E9 results](RESULTS_PRIOR_INFORMATION_LIFECYCLE_E9.md)
- [E10 results](RESULTS_PRIOR_SCOPE_VALIDITY_HORIZON_E10.md)
- [E11 results](RESULTS_PRIOR_COMPLETENESS_E11.md)
- [E12-A results](RESULTS_PRIOR_FRAGILITY_E12A.md)
- [E12-B results](RESULTS_CONTENT_COMPOSITION_FRAGILITY_E12B.md)
