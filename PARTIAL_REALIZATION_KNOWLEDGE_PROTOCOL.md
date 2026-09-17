# Partial Realization Knowledge Sweep protocol v1

## Question

Which externally supplied realization constraints are useful for far-OOD
extrapolation, and how accurate must they be? The point is to specify what a
later retrieval system must return beyond a structural family label.

## Scope fixed before execution

The experiment is deliberately run at `O=.90`, the highest exposure point of
the previous extension. At this point the matching family is useful but still
has a material gap to the parameter oracle. This isolates residual realization
uncertainty; it does not estimate a complete exposure-by-knowledge interaction.

- Families: regime change and emergent curvature.
- 200 independently generated noisy-prefix tasks per family, seed `20260926`.
- Prefix `t <= .60`, Gaussian noise SD `.015`; clean far-OOD tail `t > .70` is
  evaluation-only.
- Consequential fields are **onset** `τ`, **scale** (`k2`), and **shape**
  (`α`). The initial rate is always fitted from the prefix.
- Every base trajectory and noisy prefix is reused across conditions, enabling
  paired condition comparisons.

## Knowledge-subset sweep

For every family, evaluate:

1. family only;
2. each singleton: onset, scale, shape;
3. each pair: onset+scale, onset+shape, scale+shape;
4. onset+scale+shape.

An externally supplied field is fixed during the prefix fit; all unsupplied
fields are estimated only from the prefix. Thus the all-fields / exact condition
is the parameter-oracle reference, but it is not full-information oracle:
initial rate remains estimated from data.

## Retrieval-precision sweep

For each nonempty knowledge subset, evaluate retrieval-noise tiers `r = 0,
.05, .10, .20, .40` using independent zero-mean perturbations:

- onset: `τ_retrieved = clip(τ + ετ, .001, .999)`, with
  `ετ ~ Normal(0, sτ²)` and `sτ = {0, .02, .05, .10, .20}`;
- scale: `k_retrieved = clip(k * (1 + εk), .001, 2)`,
  `εk ~ Normal(0, r²)`;
- shape: `α_retrieved = clip(α * (1 + εα), 1.01, 4)`,
  `εα ~ Normal(0, r²)`.

At `r=0`, retrieved fields are exact. The different onset scale is explicit:
its error is in time units; scale and shape use relative retrieval error. This
is a synthetic approximation to an external source returning a constraint with
finite accuracy, not a model of a particular RAG system.

## Primary and secondary outputs

Primary for each subset × precision condition:

```text
G_partial = RMSE(partial knowledge) − RMSE(parameter oracle)
```

Report its paired bootstrap 95% interval (2,000 resamples), along with the
fraction of the exact family-to-parameter gap closed:

```text
gap closure = (RMSE(family only) − RMSE(partial))
              / (RMSE(family only) − RMSE(parameter oracle)).
```

Secondary outputs: far-OOD RMSE, utility against affine fallback, and
knowledge-precision → utility curves. Field importance is interpreted **within
each family**; no cross-family equality of information is assumed.

## Decision logic

- A field or subset that closes a large fraction of the gap at feasible
  retrieval noise is a required target for later scientific retrieval.
- If a subset helps only at exact precision, RAG output must represent its
  uncertainty rather than act as a point-parameter oracle.
- If the important subset differs by family, the retrieval schema and admission
  should be prior-conditioned.
- This development experiment identifies an information specification. It does
  not evaluate retrieval quality or validate RAG.
