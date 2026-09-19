# E9 Execution Freeze v1

This document operationalizes the frozen E9 protocol without adding a new
research variable. It separates generation, observation, and the ambient bank
so implementation errors cannot masquerade as lifecycle results.

## 1. Task generation

- One latent trajectory on `[0,1]` per primitive × predeclared separability
  level × generator × seed.
- Supplied constraint is a valid structural prior for that trajectory; coverage
  is checked only on the fixed target domain `G=[.70,1.00]`.
- Separability is assigned by its frozen generator coefficient before sampling;
  measured `E_struct` is never used to select or relabel a task.

## 2. Observation noise

- Create one master grid `x_k=k/120`, `0<=x_k<=.70`.
- Set one task-level noise scale: `.01 × clean range([0,.70])`.
- Draw one task-level noise vector once.
- Each support `.20,.30,...,.70` reveals only the corresponding nested prefix
  of the same master observations and same noise vector.

## 3. Ambient continuation bank

- Draw one `M=4096` five-coordinate ambient bank per latent task.
- Reuse it unchanged across all prefixes and DoF levels.
- Apply active-coordinate sets `{z1}`, `{z1,z2,z3}`, `{z1,...,z5}`; all
  inactive coordinates are exactly zero.
- Use the same fixed grid `G=[.70,1.00]` with 161 points for every
  continuation, prior-satisfaction check, covariance, and dispersion metric.
- Only prefix likelihood weights and the predeclared active subset may differ.

## Integrity-only sanity suite

Before full E9, gate only these implementation invariants:

1. Observation prefixes are exact nested subsets.
2. The noise realization is identical for shared observations across prefixes.
3. The ambient bank is byte-identical across all prefix/DoF measurements of a
   latent task.
4. Inactive coordinates equal zero.
5. `G` is identical for every measurement.
6. Coverage invariant equals 1 for every supplied valid structural prior.
7. `S`, `ESS`, `d_eff`, `V_f`, and `E_struct` are finite.
8. Endpoint intervals, right-censoring, redundancy confirmation, and re-entry
   censoring pass deterministic toy cases.
9. E9 computations neither load nor receive a future target, RMSE, utility,
   realization-engine prediction, or engine identifier.

No expected direction, effect size, monotonicity, or ordering of `S`, `ESS`,
`d_eff`, or `V_f` is a sanity criterion. Those are E9 results.
