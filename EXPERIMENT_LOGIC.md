# Experimental logic: from family truth to usable structural prior

## Problem decomposition

An extrapolation prior has five logically separate properties.

```text
Family truth ──does the structural family match the generator?──┐
                                                                  ↓
Structural evidence ──is its signature visible in the prefix?───┤
                                                                  ↓
Parameter identifiability ──are onset/scale/shape constrained?──┤
                                                                  ↓
Safe realization ──can this fitted continuation be deployed?─────┤
                                                                  ↓
Far-OOD utility ──is it better than fallback on the hidden tail?─┘
```

The purpose is not to show that a parametric curve can fit its own simulator.
The falsifiable issue is whether the **same true family label**, whose parameters
remain unknown, changes from harmful to helpful as its identifying evidence
crosses the observation boundary. The further question is whether more visible
evidence actually identifies the future-determining realization parameters.

## Causal test design

Hold the family truth fixed, vary only the amount of its diagnostic structure
exposed before the boundary, then evaluate held-out tail loss. This is a
generative-family oracle, not a full-information oracle.

| Claim | Manipulation | Required measurement | What falsifies it |
|---|---|---|---|
| C1: family truth alone is insufficient | move onset/time-scale relative to boundary | generative-family utility `RMSE_linear - RMSE_matching_family` | utility never declines at low observability |
| C2: observability drives utility | seven-level sweep in each of three generic families | utility trend / Spearman O→utility | nonpositive or unstable family-level association |
| C3: data can decide admissibility | pseudo-OOD score only from prefix | score↔O association, low-O reject rate, high-O admit rate | score cannot separate low/high O |
| C4: a validation design is transferable | compare uniform and boundary-focused scores | gate RMSE and error trade-offs across all families | one score only works by family-specific leakage/tuning |
| C5: visibility becomes sufficient identification | extend post-onset exposure to O=.90 | family–parameter realization gap with paired bootstrap | gap remains above predeclared practical threshold |

## Why three families

One transition simulator could be dismissed as a change-point artefact. The
three families isolate qualitatively different evidence: discrete regime
exposure, gradual emergence of curvature, and approach-to-bound curvature.
A replicated sign flip is therefore evidence for an *identifiability problem*,
not for one domain law.

## Method ladder

```text
M0 linear fallback
M1 generative-family oracle fit: upper potential conditional on identifiability
M2 contrast-family fit         : misspecification risk control
M3 pseudo-OOD selection        : candidate-selection stress test
M4 uniform family-oracle gate  : simple validation admission baseline
M5 tail-weighted family-oracle gate: predeclared boundary-sensitive alternative
```

M1 is intentionally not a full-information oracle. If M1 harms at low observability,
the issue is not false scientific knowledge but an inability to infer usable
parameters from the available data. M4/M5 must outperform M0 or improve risk
selectively before they are called an admission solution. Admission's target is
therefore expected utility of a realized prior, `P(U_P > 0 | D_obs)`, rather
than posterior family correctness.

## Decision logic after v1

1. If C1/C2 fail, stop: generic prior observability is not demonstrated.
2. If C1/C2 pass but C3 fails, retain the new problem definition and redesign
   admission; do not proceed to retrieval/RAG.
3. If C1–C3 pass in new independent draws, test whether a retrieval system can
   place the useful family in a candidate set.
4. Only then test richer physical simulators and real data.

This prevents a retrieval system from being credited for a prior that the data
cannot yet responsibly use.

## Extension result: visible does not yet mean identifiable

The independent high-exposure development extension evaluates C5. Family-only
error and realization-parameter error both decline as O rises to `.90`, but the
pre-specified family–parameter gap stays above `.01` for regime change and
emergent curvature. This rejects *practical convergence within this finite
grid* and keeps the relevant distinction explicit:

```text
structural evidence ≠ sufficient parameter identifiability
```

Thus a retrieval stage should aim to retrieve not merely a family label but
constraints on the continuation's onset, scale, shape, or bound; admission then
judges whether remaining uncertainty is safe.

## Partial knowledge result: the retrieval target is family-conditioned

The partial-realization sweep fixes the high-exposure setting where family-only
is useful but remains below the parameter reference. Exact onset+scale closes
97.7% of the gap for regime change; exact scale+shape closes 92.8% for emergent
curvature. Onset alone is nearly uninformative for curvature (3.6%). Retrieval
precision can reverse the benefit of fixing several fields, so the retrieval
output must be an uncertainty-aware constraint, not an unqualified point value.

The next artifact before actual RAG is an information specification: the
candidate record must include structural family, field-level constraints or
ranges, confidence, and provenance. This makes a later evaluation decomposable
into family recall, realization-constraint recall/accuracy, and admission
safety.
