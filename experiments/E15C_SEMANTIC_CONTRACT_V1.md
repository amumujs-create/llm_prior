# E15-C semantic contract v1 — mechanistic invariant plus residual uncertainty

## Scientific question

When a mechanistic invariant is valid and shared but incomplete, should it be fixed as a common backbone while uncertainty is retained only in unresolved residual future realizations?

E15-C tests utilization of a **valid but incomplete** mechanistic prior. It is not a generic physics-versus-ML comparison.

## Frozen semantics

The task family has the abstract decomposition

\[
\dot y(t) = G_{\mathrm{inv}}(y(t)) + r(t),
\]

where `G_inv` is a globally valid, shared mechanistic invariant and `r(t)` is a scenario-specific residual dynamic.

1. **Global validity.** `G_inv` holds for every task and throughout the forecast domain.
2. **Incompleteness.** `G_inv` alone does not determine the trajectory or its future; the residual need not be zero.
3. **Residual is not a prior violation.** A nonzero `r(t)` is permitted by the supplied prior and must not be labelled as a failure of the invariant.
4. **Closed mechanism is overcommitment.** Setting `r(t)=0` adds an unsupported completeness claim. It is therefore an incompleteness stress condition, not the primary prior policy.
5. **No future leakage.** The true residual realization and future labels may be used only for generation and scoring, never for fitting, residual selection, or policy weighting.

## Uncertainty allocation

E15-C distinguishes two evidence targets:

- `E_inv`: evidence about the shared invariant.
- `E_r`: evidence about the residual realization.

The target condition is that the invariant can be well supported while residual futures remain weakly identified. Any uncertainty reduction must be applied only to the dimension actually resolved by prefix evidence.

\[
E_{\mathrm{inv}}\ \text{high},\quad E_r\ \text{low}
\quad\Rightarrow\quad
\text{share }G_{\mathrm{inv}}\text{ and retain residual alternatives.}
\]

## Policy roles

The eventual numerical manifest will define implementation details, but these policy meanings are frozen.

| Policy | Frozen role |
| --- | --- |
| `free_baseline` | Uses no mechanistic invariant. |
| `closed_mechanism` | Forces `r(t)=0`; secondary incompleteness stress condition. |
| `invariant_residual_MAP` | Shares the invariant and selects one residual future using residual evidence. |
| `invariant_residual_ensemble` | Shares the invariant and retains a uniform set of residual futures. |
| `evidence_weighted_residual_mixture` | Shares the invariant and weights the same residual hypotheses using prefix residual evidence. |
| `soft_invariant` | Secondary relaxation policy; does not define a primary estimand. |

## Primary estimands

\[
C1_C = \mathrm{NRMSE}_{\mathrm{weighted\ residual\ mixture}}
       - \mathrm{NRMSE}_{\mathrm{residual\ MAP}},
\]

which isolates retention versus point commitment after using the same invariant and residual evidence; and

\[
C2_C = \mathrm{NRMSE}_{\mathrm{weighted\ residual\ mixture}}
       - \mathrm{NRMSE}_{\mathrm{uniform\ residual\ ensemble}},
\]

which isolates evidence weighting after residual diversity has been retained.

A secondary backbone comparison will match residual capacity between an invariant-plus-residual policy and a free policy. It asks whether the invariant itself stabilizes extrapolation; it is not a replacement for `C1_C` or `C2_C`.

## Interpretation boundaries

- A residual-weighting result concerns whether prefix evidence identifies the **residual future**, not merely whether it supports the invariant.
- A favorable closed-mechanism result in a particular realization does not establish that an incomplete invariant should generally be treated as complete.
- E15-C will not claim that a shared invariant is universally preferable to free learning outside its frozen task family.
- Generator equation, residual family, noise, exposure geometry, fitting capacity, numerical thresholds, quota, and inference details remain unfrozen and must be selected in E15-C0 without inspecting confirmatory policy outcomes.

## Confirmatory hypothesis

> A valid mechanistic invariant should be shared across future hypotheses, while uncertainty should remain in unresolved residual dynamics rather than being collapsed into a closed mechanistic model. Residual concentration is warranted only when prefix evidence identifies the residual realization itself.

## Bridge from E15-A and E15-B

- **E15-A:** evidence identifies an event location that directly determines the future realization.
- **E15-B:** evidence identifies a warranty endpoint but not the realization after that endpoint.
- **E15-C:** evidence may identify the invariant while leaving residual futures unresolved.

The cross-study principle under test is:

> **Prior utilization is anatomy-aware uncertainty allocation: preserve uncertainty when identification is weak, and reduce it only along dimensions that the evidence actually identifies.**
