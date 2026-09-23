# E16-B CCPP Observational/Tabular External-Validation Semantic Contract v1

## Status and scientific role

This is a **semantics-only** contract.  It freezes no source file, feature
direction, constraint sign, scope endpoint, split coordinate, support cutoff,
model hyperparameter, policy strength, quota, seed, or outcome.

E16-B tests the frozen E15 utilization principle in a real operational tabular
regression setting with partial structural prior knowledge:

> **Preserve unresolved hypothesis diversity, use evidence to guide reduction
> along the dimensions it informs, and avoid premature point collapse.**

It is not a time-series experiment and does not use row order as time.  Its
external-validation role differs from E16-A: E16-A is a physical-mechanistic
candidate on legal hold, whereas E16-B is an observational/process candidate
with an external-knowledge prior audit still required.

## Task definition

The candidate CCPP task is

\[
X=(AT,V,AP,RH)\longrightarrow PE,
\]

where \(AT\), \(V\), \(AP\), and \(RH\) are the four observed ambient/process
covariates and \(PE\) is net electrical energy output.  The intended target is
covariate-support extrapolation:

\[
\mathcal X_{\rm train}\longrightarrow
\mathcal X_{\rm test}\not\subseteq\mathcal X_{\rm train}.
\]

The exact support direction and the definition of out-of-support testing are
open.  They must be selected by a separate source/domain audit using public
process knowledge, not by target-label associations, post-split performance,
or policy outcomes.  Dataset row order is explicitly prohibited as a temporal
forecasting axis.

## Prior anatomy

The intended prior is a partial structural packet:

\[
P_{\rm CCPP}=\{C,\theta,\Omega,q,\pi\},
\]

where:

- \(C\) is a public-knowledge structural statement such as a directional,
  smoothness, or finite-scope relation;
- \(\theta\) denotes unresolved quantitative specification, including slope,
  curvature, or interaction magnitude;
- \(\Omega\) is the public domain/scope over which the statement is warranted;
- \(q\) is provenance and evidential quality; and
- \(\pi\) is a representation for admissible alternatives.

No monotonicity sign, smoothness scale, interaction, or scope is supplied by
this contract.  A correlation, regression coefficient, feature-importance
score, or target-derived partial dependence computed on the CCPP outcomes is
not admissible evidence for creating the prior packet.

The anatomy is deliberately partial: a valid directional or smooth relation
does not imply a complete mapping from \(X\) to \(PE\), nor does it establish
validity outside its public scope.

## External-knowledge boundary

The later domain audit must cite a public source for every supplied prior
component and label each component as one of:

1. **directly supplied structural knowledge** eligible for the prior packet;
2. **quantitative uncertainty** to be represented as alternatives, not fixed
   from labels; or
3. **unresolved/unsupported**, which must not be used as a prior.

The audit must separately document the dataset's source, license/use terms,
measurement definitions and units, collection protocol, and the fact that
provided shuffled dataset versions do not create a temporal ordering.

## Leakage and split contract

The final split procedure will be frozen only after the public domain audit.
It must satisfy all of the following:

- The support coordinate, threshold(s), and any multivariate feasibility rule
  are determined without test-target inspection.
- No held-out test labels enter prior selection, constraint selection,
  hyperparameter selection, policy weighting, calibration, or error scaling.
- Any train/validation/test allocation is made before confirmatory policy
  outcomes are opened.
- If repeated resampling is used, all compared policies share identical rows,
  folds, support regions, preprocessing, and target transforms.
- The support definition is expressed in covariate space rather than inferred
  from observed error or a post-hoc difficulty score.

## Policy semantics

All policies must have matched predictive capacity, common training data,
common preprocessing, and a common candidate family.  They differ only in how
the same prior packet is represented or utilized.

| Policy label | Semantic role |
| --- | --- |
| `free_baseline` | Capacity-matched predictor without the audited structural packet. |
| `hard_constraint` | Enforces the selected public structural statement over its explicitly supplied scope. |
| `soft_constraint` | Uses the same statement as a penalty, with strength fixed before outcomes. |
| `prior_hypothesis_ensemble` | Retains multiple admissible structural specifications/scopes. |
| `evidence_weighted_prior_mixture` | Uses prefix/training evidence to weight the same retained alternatives. |

The final policy set may omit a label only through a pre-outcome implementation
amendment.  It may not add a policy whose capacity, data access, or candidate
family differs from the stated comparison merely because a preliminary result
looks favorable.

## Prospective estimands

The numerical error scale and exact support region remain open.  The following
questions are frozen, but directional predictions remain conditional on the
later domain audit identifying a coherent partial prior and a valid uncertainty
dimension.

\[
B_1=\operatorname{Error}_{\rm retained\ prior\ ensemble}
    -\operatorname{Error}_{\rm hard\ commitment},
\]

testing whether premature collapse of unresolved admissible prior alternatives
costs covariate-support extrapolation accuracy.

\[
B_2=\operatorname{Error}_{\rm evidence\ weighted\ mixture}
    -\operatorname{Error}_{\rm uniform\ prior\ ensemble},
\]

testing whether the evidence used for weighting is informative about the same
prior-uncertainty dimension being reduced.

\[
B_3=\operatorname{Error}_{\rm audited\ prior\ policy}
    -\operatorname{Error}_{\rm free\ baseline},
\]

testing the external incremental value of the partial structural packet under
matched capacity.  \(B_3\) is non-directional at this semantic stage.

No sign, primary cell, inferential unit, bootstrap, quota, or success rule is
frozen until the source and domain audit establish which prior components are
publicly warranted and what uncertainty they leave unresolved.

## Non-claims and next gate

This contract does not claim that CCPP has a globally monotone response in any
feature, that a single-variable support split is adequate, that hard or soft
constraints are valid, or that evidence weighting must improve real tabular
extrapolation.  It provides only a leakage-safe semantic framework.

The only next authorized action is a CCPP source and physical/domain-knowledge
audit.  That audit must establish source provenance/use terms and decide,
without target-label inspection, whether any directional, smoothness, or
finite-scope statement is sufficiently warranted to instantiate the packet.
