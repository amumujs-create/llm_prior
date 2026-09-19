# E9 Execution Freeze v1

This document operationalizes the frozen E9 protocol without adding a new
research variable. It separates generation, observation, and the ambient bank
so implementation errors cannot masquerade as lifecycle results.

## 1. Task generation

- One latent trajectory on `[0,1]` per primitive × predeclared separability
  level × generator × seed.
- Supplied constraint is a valid structural prior for that trajectory; coverage
  is checked only on the fixed target domain `G=[.70,1.00]`.
- The full latent future is available **only** in this generation/validation
  stage for the oracle coverage check. After a task is accepted, E9 scoring is
  passed neither future truth nor RMSE, utility, engine output, or engine ID.
- Separability is assigned by its frozen generator coefficient before sampling;
  measured `E_struct` is never used to select or relabel a task.

## 2. Observation noise

- Create one master grid `x_k=k/120`, `0<=x_k<=.70`.
- Set one task-level noise scale: `.01 × clean range([0,.70])`.
- Use this same task-level reference range to normalize every prefix MSE:
  `L_s=(1/n_s) sum_{i<=s}((y_i-f_i)/R_ref)^2`, with
  `R_ref=range(clean[0,.70])`; never use a prefix-specific range.
- Draw one task-level noise vector once.
- Each support `.20,.30,...,.70` reveals only the corresponding nested prefix
  of the same master observations and same noise vector.

## 3. Ambient continuation bank

- Draw one `M=4096` five-coordinate ambient bank per latent task.
- Each bank member is one full-domain function on `[0,1]`, not a function only
  on future `G`; the same function is evaluated on `[0,.70]` for prefix
  likelihood and on `G` for satisfaction/dispersion.
- Reuse it unchanged across all prefixes and DoF levels.
- Apply active-coordinate sets `{z1}`, `{z1,z2,z3}`, `{z1,...,z5}`; all
  inactive coordinates are exactly zero.
- Use the same fixed grid `G=[.70,1.00]` with 161 points for every
  continuation, prior-satisfaction check, covariance, and dispersion metric.
- Only prefix likelihood weights and the predeclared active subset may differ.
- For `d_eff`, if `tr(Sigma_w^2) < 1e-12`, set `d_eff=0`.
- Store raw `V_f`, but headline cross-primitive/generator multiplicity uses
  `V_f_norm=V_f/R_ref^2`, with the frozen task-level `[0,.70]` reference range.

The generator coefficient `eta=.20/.50/.80` is a predeclared separability
*control*, not a claim that low/mid/high have equal empirical difficulty across
primitives. Measured `E_struct` is the observed separability outcome.

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

## Endpoint risk sets and inference

Previously attained endpoints remain valid if a later prefix has low ESS.
`sampler-unresolved-at-.70` is a terminal/endpoint-specific reason, not a
task-wide override. `E_red*` is undefined/not-at-risk if `E_joint*` never
exists; it is right-censored `> .70` only for tasks that entered the joint
risk set but never obtained confirmed redundancy.

Bootstrap uses 5,000 resamples of latent task IDs **within each
primitive × separability × generator stratum**. Generator summaries are then
equal-weight macro averages across the three generators. Task, observation-noise,
and ambient-bank RNG streams use separately derived deterministic seeds.
