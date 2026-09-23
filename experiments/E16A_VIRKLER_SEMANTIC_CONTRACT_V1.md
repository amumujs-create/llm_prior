# E16-A Virkler Mechanistic External-Validation Semantic Contract v1

## Status and role

This is a **semantics-only** contract.  It freezes no numerical parameter
ranges, prefix locations, train/validation/confirmatory specimen counts,
residual family, split allocation, quota, or source-file checksum.  Those
items require a separate provenance and numerical-design phase.

E16-A is an external validation of the frozen E15 utilization principle; it
does not introduce a new synthetic prior-utilization rule:

> **Preserve unresolved hypothesis diversity, use evidence to guide reduction
> along the dimensions it informs, and avoid premature point collapse.**

The target system is constant-amplitude fatigue crack growth in the Virkler
replicate experiment.  Results will be interpreted as external evidence for,
or against, the predeclared E15 claims—not as a rediscovery or extension of
the E15 synthetic grammar.

## Observational representation

The primary representation is cumulative load cycles as a function of crack
length:

\[
N = N(a).
\]

For target specimen \(u\), the supplied prefix is

\[
D_u^{\rm prefix}=\{(a_i,N_{ui}):a_i\le a_{\rm prefix}\},
\]

and observations at larger crack lengths are held out as extrapolative
targets.  This orientation follows the reported experimental measurement
structure: crack-length levels are specified and the cumulative cycles to
each level are recorded.  The primary target is the latent/recorded specimen
trajectory \(N_u(a)\), not an arbitrary reparameterization as \(a(N)\).

## Prior object and anatomy

The external mechanistic prior packet is

\[
P_{\rm mech}=\{\text{Paris-type crack-growth structure},\;
\theta=(C,m),\;\Omega,\;q,\;\pi\}.
\]

The Paris-type mechanism is represented in its observation-aligned inverse
form:

\[
\frac{da}{dN}=C[\Delta K(a)]^m,
\qquad
\frac{dN}{da}=\frac{1}{C[\Delta K(a)]^m},
\qquad
N(a)-N(a_0)=\int_{a_0}^{a}\frac{ds}{C[\Delta K(s)]^m}.
\]

This contract distinguishes:

- **mechanistic structure:** the Paris-type dependence;
- **specification uncertainty:** \(\theta=(C,m)\), potentially with other
  predeclared public geometry constants required to evaluate \(\Delta K\);
- **specimen-specific discrepancy:** \(r_u(a)\), if retained after source and
  design audit;
- **scope:** the observed constant-amplitude crack-growth regime.

A nonzero discrepancy is not, by itself, a violation of the mechanistic
prior.  The closed model \(r_u(a)=0\) therefore adds a **completeness
assumption** beyond the supplied structural mechanism.

## Task and leakage contract

One specimen is one latent task.  All allocation is specimen-level:

\[
\text{population-training specimens}\;\perp\;
\text{validation specimens}\;\perp\;
\text{held-out confirmatory specimens}.
\]

Population-training specimens may be used only to construct a predeclared
population distribution or discrete candidate set for \((C,m)\), and any
residual representation.  No future observation from a confirmatory specimen
may enter population-prior construction, candidate weighting, model fitting,
hyperparameter selection, or scoring-window selection.

For each confirmatory specimen, policy fitting and weighting may access only
its prefix and the frozen public prior packet.  Its future crack-length levels,
future cycle counts, failure-boundary targets, and scoring windows are
inaccessible until prediction is fixed.  Any preprocessing that removes,
interpolates, or aligns observed levels must be frozen without inspecting
confirmatory future outcomes.

## Policy semantics

All policies will be instantiated on a common, frozen candidate family and
common prefix data.  Policy labels have the following meanings:

| Policy | Meaning |
| --- | --- |
| `free_baseline` | Prefix-only flexible model with no Paris-type mechanistic prior. |
| `mechanism_MAP` | Select one admissible \((C,m)\) hypothesis using prefix evidence. |
| `mechanism_uniform_ensemble` | Retain admissible mechanistic hypotheses with uniform weights. |
| `mechanism_weighted_mixture` | Retain the same hypotheses and weight them with prefix likelihood. |
| `mechanism_plus_residual_ensemble` | Shared mechanism plus a retained family of unresolved specimen discrepancy continuations. |
| `closed_mechanism` | Set \(r_u(a)=0\); a secondary completeness stress policy. |

The final residual and free-model capacities must be specified together in a
later execution contract.  No policy may gain access to specimen future data
through a different residual basis, candidate grid, or preprocessing path.

## Frozen estimands and prospective directions

The scale and exact extrapolation window remain open, but every compared
policy will use the same target specimen and window.

\[
A_1=\operatorname{NRMSE}_{\rm mechanism\ ensemble}
     -\operatorname{NRMSE}_{\rm mechanism\ MAP}.
\]

**Primary prospective prediction:** for early or insufficiently identifying
prefixes, \(A_1<0\).  This tests E15's strongest claim in the external
mechanistic setting: avoid premature point collapse of unresolved mechanistic
specification futures.

\[
A_2=\operatorname{NRMSE}_{\rm mechanism+residual}
     -\operatorname{NRMSE}_{\rm closed\ mechanism}.
\]

**Primary prospective prediction:** \(A_2<0\).  This tests the E15-C
validity-versus-completeness claim externally.

\[
A_3=\operatorname{NRMSE}_{\rm mechanism+residual}
     -\operatorname{NRMSE}_{\rm free\ baseline}.
\]

\(A_3\) is a secondary, non-directional incremental-value question.  It is
not an input to selecting a source, split, numerical design, or policy
capacity.

## Source hierarchy and acquisition gate

No confirmatory split may be created before a machine-readable full-corpus
source is acquired and audited.  The intended hierarchy is:

1. A provenance-linked, machine-readable full 68-specimen by 164-level
   dataset (primary candidate; reported hierRegSDE lineage).
2. The original Virkler experimental publication/documentation for physics
   and provenance verification.
3. Partial package data, such as a 25-specimen subset, for sensitivity only.
4. Figure-digitized reconstructions for sensitivity only; they are prohibited
   as the primary external-validation corpus.

The source audit must freeze the exact bytes and SHA-256, upstream locator,
license or use terms, provenance chain, units, crack-length grid, specimen
count, missingness/monotonicity structure, and whether the stated 164 by 68
layout is directly supplied or reconstructed.  It must explicitly reject a
figure-digitized reconstruction as the primary corpus when its documentation
acknowledges trajectory changes relative to original figures.

## Non-claims

This contract does not assert that Paris law is exact for every specimen, that
all \((C,m)\) variation is identifiable from an early prefix, that the
mechanism-plus-residual policy must beat a capacity-matched free model, or that
the E15 principle is universal.  It only predeclares how these questions will
be tested after source and numerical contracts are frozen.
