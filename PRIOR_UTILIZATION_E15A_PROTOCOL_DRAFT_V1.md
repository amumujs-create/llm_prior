# E15-A — Regime-prior utilization under onset uncertainty

## Question

Given the same regime-onset knowledge object, which utilization policy produces
the most reliable far-OOD prediction? E15-A changes neither the stated regime
content nor the base predictive family; it changes only how that information is
represented and acted on.

`K = {regime exists, tau in I}` is the shared knowledge object. For exact
knowledge, `I={tau*}`. For interval knowledge, every policy receives the same
support set `I`; a point policy is explicitly an **early-commitment projection**
of `I`, not an information-preserving representation. A uniform density over
`I` is likewise a utilization-policy choice, not information asserted by `K`.

## Scope and held-fixed components

- Prior family: one mechanistic regime change with onset `tau`.
- Common predictive family: the frozen regime continuation family and the same
  nuisance-parameter bounds/optimizer for every policy.
- Same noisy observed prefix, train/test split, noise realization, onset-grid,
  task seeds, and far-OOD evaluation points within each latent task.
- No policy receives future observations, true onset, or a different candidate
  set. The evidence-weighted mixture may use the observed prefix only.
- This is a utilization study. `S`, `E_a`, scope, and completeness are stored
  as descriptors/strata, not optimized endpoints.

## Factors

### Knowledge state

1. `exact`: `I={tau*}`.
2. `narrow`: a valid interval centered on `tau*` with frozen half-width.
3. `broad`: a valid wider interval centered on `tau*`.
4. `existence_only`: the frozen admissible onset domain.
5. `slightly_biased`: same width as `narrow`, shifted by a frozen positive or
   negative offset; `Coverage(I)=1(tau* in I)` and violation distance are
   recorded rather than hidden.

Biased rows are stratified into `covered_biased` and `uncovered_biased`.
When `tau*` is outside `I`, the true onset is not representable by
support-only policies; this knowledge-validity failure is never counted as
wrong-hypothesis collapse.

### Prefix observability

`low`, `medium`, and `high` use frozen observed-prefix endpoints/noise layouts.
They are design factors, not labels copied into analysis; realized regime
evidence is recorded from the prefix.

### Utilization policy

| Policy | Use of the same knowledge object `K` |
|---|---|
| `no_prior` | Common predictive family without onset knowledge. |
| `hard_midpoint` | Deterministically commits to the midpoint of `I`; deliberately discards interval uncertainty when `I` is non-singleton. |
| `evidence_MAP_point` | Selects `tau_MAP=argmax_{tau in grid(I)} p(D_prefix|tau)` and commits to that single onset. |
| `soft_constraint` | Fits the common family with a frozen penalty for leaving `I`. |
| `distributional_prior` | Integrates predictions against a continuous uniform density on `I`, without prefix-likelihood reweighting. |
| `uniform_hypothesis_ensemble` | A frozen discrete onset grid spanning `I`, equally weighted. |
| `evidence_weighted_mixture` | The same discrete grid, reweighted only by prefix likelihood. |

The four central policies form a factorial decomposition:

|  | Point commitment | Uncertainty retained |
|---|---|---|
| No prefix-evidence weighting | `hard_midpoint` | `uniform_hypothesis_ensemble` |
| Prefix-evidence weighting | `evidence_MAP_point` | `evidence_weighted_mixture` |

Thus `evidence_MAP_point` versus `evidence_weighted_mixture` isolates the
benefit of retaining multiple prior-consistent onsets after the same prefix
evidence has been used. For `exact`, uncertainty-retaining policies collapse
by design; this is a representation-equivalence audit, not an expected gap.

The frozen soft objective is
`L = L_prefix + lambda[(tau_L-tau)_+^2 + (tau-tau_U)_+^2`.
It is a soft utilization of the same interval knowledge, not an
information-preserving interval representation.

## Required implementation freezes before execution

1. Regime generator equation, parameter ranges, prefix endpoints, far-OOD
   horizon, noise scale, task quota, and maximum generation attempts.
2. Exact interval half-widths, biased offsets/directions, admissible onset
   domain, and discrete hypothesis grid.
3. Common nuisance-fit objective and optimizer budget. No policy-specific
   tuning, validation selection, or future-dependent calibration.
4. Soft-constraint penalty and mixture likelihood temperature.
5. Catastrophic-failure threshold, distance bins, and wrong-hypothesis-collapse
   definition before results.
6. Latent-task paired bootstrap (`B=5000`); policies and candidate hypotheses
   remain repeated measures within a task.

## Primary outcomes

- Far-OOD RMSE.
- Far-OOD CRPS for policies that yield predictive distributions.
- Worst-group far-OOD error across predeclared knowledge × observability cells.
- Catastrophic failure rate.
- Distance-wise degradation profile.
- Wrong-hypothesis collapse rate for point/mixture policies.
- Mixture entropy and true-onset hypothesis weight, conditional on the prefix.

The primary contrasts are policy contrasts within the same task and knowledge
state. A claim that one policy is preferable must be conditional on the
predeclared onset-uncertainty and observability strata; no universal policy
ranking is sought.

## Predeclared hypotheses

1. With exact or very narrow valid onset knowledge, hard commitment may match
   uncertainty-retaining policies.
2. With broad onset uncertainty and low prefix observability, early point
   commitment may produce more wrong-hypothesis collapse than policies that
   retain multiple onset hypotheses.
3. Lower prefix evidence may favor retaining mixture entropy, but this is an
   empirical hypothesis rather than a sanity gate.

Wrong-hypothesis collapse is defined only for covered knowledge states. For a
mixture it requires both `H(w) < H_collapse` and
`|tau_MAP-tau*| > delta_tau`; point policies use the same onset-error condition
with their unit-mass weight. `H_collapse` and `delta_tau` are numerical freeze
items, not post-result thresholds.

## Interpretation boundary

E15-A evaluates a single event-prior family under controlled onset uncertainty.
It cannot rank shape-prior constraints or mechanistic shared invariants; those
are separate E15-B and E15-C studies. It also cannot establish that a mixture
is universally preferable: it tests whether utilization should depend on the
prior's specification uncertainty and observability.
