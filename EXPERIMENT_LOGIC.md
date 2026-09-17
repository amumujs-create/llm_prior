# Experimental logic: from truth to usable prior

## Problem decomposition

An extrapolation prior has three logically separate properties.

```text
Prior truth  ──does the family match the data-generating mechanism?──┐
                                                                      ├─> Far-OOD utility
Observability ──is its distinguishing evidence in the prefix?────────┘
                                   ↑
                           Admission must estimate this from data alone
```

The purpose is not to show that a parametric curve can fit its own simulator.
The falsifiable issue is whether the **same true family** changes from harmful
to helpful as its identifying evidence crosses the observation boundary.

## Causal test design

Hold the family truth fixed, vary only the amount of its diagnostic structure
exposed before the boundary, then evaluate held-out tail loss.

| Claim | Manipulation | Required measurement | What falsifies it |
|---|---|---|---|
| C1: truth alone is insufficient | move onset/time-scale relative to boundary | oracle utility `RMSE_linear - RMSE_true_family` | utility never declines at low observability |
| C2: observability drives utility | seven-level sweep in each of three generic families | utility trend / Spearman O→utility | nonpositive or unstable family-level association |
| C3: data can decide admissibility | pseudo-OOD score only from prefix | score↔O association, low-O reject rate, high-O admit rate | score cannot separate low/high O |
| C4: a validation design is transferable | compare uniform and boundary-focused scores | gate RMSE and error trade-offs across all families | one score only works by family-specific leakage/tuning |

## Why three families

One transition simulator could be dismissed as a change-point artefact. The
three families isolate qualitatively different evidence: discrete regime
exposure, gradual emergence of curvature, and approach-to-bound curvature.
A replicated sign flip is therefore evidence for an *identifiability problem*,
not for one domain law.

## Method ladder

```text
M0 linear fallback
M1 true-family fit             : upper potential conditional on identifiability
M2 contrast-family fit         : misspecification risk control
M3 pseudo-OOD selection        : candidate-selection stress test
M4 uniform oracle gate         : simple validation admission baseline
M5 tail-weighted oracle gate   : predeclared boundary-sensitive alternative
```

M1 is intentionally not a parameter oracle. If M1 harms at low observability,
the issue is not false scientific knowledge but an inability to infer usable
parameters from the available data. M4/M5 must outperform M0 or improve risk
selectively before they are called an admission solution.

## Decision logic after v1

1. If C1/C2 fail, stop: generic prior observability is not demonstrated.
2. If C1/C2 pass but C3 fails, retain the new problem definition and redesign
   admission; do not proceed to retrieval/RAG.
3. If C1–C3 pass in new independent draws, test whether a retrieval system can
   place the useful family in a candidate set.
4. Only then test richer physical simulators and real data.

This prevents a retrieval system from being credited for a prior that the data
cannot yet responsibly use.
