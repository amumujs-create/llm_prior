# E15-B — Shape-prior utilization under finite scope uncertainty

## Question

Given the same directional knowledge object, how should a shape prior be used
when its future validity horizon is uncertain?

E15-B holds the shape content fixed and changes only utilization. It is not a
second event-onset experiment: the latent uncertainty is the horizon through
which a directional constraint remains valid.

## Representative prior

`K = {df/dt >= 0 on a future interval of uncertain endpoint h}`.

`h*` is the endpoint through which monotonicity is warranted, not the first
turning point or the first time that decrease begins. The clean truth is
nondecreasing through `h*`; after `h*` it may continue increasing, flatten, or
later decrease. The supplied knowledge object describes direction but not an
exact, globally valid endpoint. Thus a globally hard monotonic constraint can
become invalid after `h*`, even when it was locally valid throughout its
declared scope.

This directly tests the E10/E13 anatomy distinction:

`validity != scope`.

## Scope precursor and realized scope evidence

Scope candidates must be distinguishable from the prefix without exposing a
direction violation. E15-B therefore uses a generator family with an
in-scope shape precursor, for example

`f'(t)=b[1+gamma(h*-t)]` for `t<=h*`, with `b>0` and `gamma>0`.

Equivalently, the in-scope clean trajectory may be parameterized as
`f(t)=a+b[t+gamma(h*t-t^2/2)]`. It remains nondecreasing throughout the
observed prefix, while its slope pattern supplies information about the scope
endpoint. Post-scope behavior is generated separately and is not used by any
policy to fit or select a scope hypothesis.

To isolate scope uncertainty, `gamma=gamma_0` is a single experiment-wide
constant, not a task-level nuisance parameter. Only `a` and positive `b` vary
by task. Allowing `b`, `gamma`, and `h*` all to vary would confound the scope
endpoint with precursor strength through the same observed linear and quadratic
coefficients.

`E_h` is not computed from the loss of fitting a nested local constraint.
That loss would mechanically favor shorter horizons: an `h_2` constraint
contains an `h_1<h_2` constraint. Instead, a separate prefix-only
scope-precursor likelihood profiles the in-scope trajectory model. For every
full-domain candidate `h_k`, it fits
`f(t)=a+b q_{h_k}(t)`, where
`q_h(t)=t+gamma(h*t-t^2/2)`, by deterministic unconstrained linear least
squares in `(a,b)`. The resulting precursor profile scores define
`w_k^full ∝ exp[-(ell_k-ell_min)]` and
`E_h=1-H(w^full)/log(K_full)`. `E_h` is computed on the full admissible scope
domain, never on the supplied support `H`; it is a continuous descriptor rather
than an additional design label. Thus scope identifiability is separated from
scope enforcement.

The forecast engine is deliberately distinct. It fits the same unconstrained
quadratic continuation family for every policy and changes only directional
enforcement: for a candidate `h_k`, it requires
`f_hat'(t_prefix)>=0` and `f_hat'(h_k)>=0`. Since the derivative of a quadratic
is affine, these two endpoint inequalities guarantee monotonicity on the whole
interval. The small convex constrained least-squares problem is solved by a
deterministic active-set enumeration; there is no optimizer-budget degree of
freedom. `hard_global` replaces `h_k` with the far-horizon endpoint.

## Held fixed

- One frozen synthetic shape family and the same noisy prefix per latent task.
- Same task seeds, forecast grid, model capacity, optimizer budget, and
  validation-free fitting rule across every utilization policy.
- Same stated direction knowledge and same admissible horizon support `H`.
- No policy may see future labels, `h*`, or any post-prefix scope oracle.
- Scope is evaluated on clean truth after prediction; it is never reused for
  policy selection.

## Candidate utilization policies

| Policy | Treatment of the same directional knowledge |
|---|---|
| `free_baseline` | No supplied directional constraint. |
| `hard_global` | Enforces nondecreasing continuation across the whole forecast horizon. |
| `hard_local_MAP` | Enforces the constraint only through one selected horizon in `H`. |
| `soft_global` | Applies a frozen violation penalty across the whole horizon. |
| `slack_distribution` | Marginalizes over a fixed distribution of permissible directional slack. |
| `scope_hypothesis_ensemble` | Retains multiple horizon-constrained continuations uniformly over `H`. |
| `evidence_weighted_scope_mixture` | Retains the same horizon hypotheses and reweights them only with prefix evidence. |

The primary decomposition parallels E15-A but concerns scope rather than onset:

- `D1 = evidence_weighted_scope_mixture - hard_local_MAP`: retention of
  multiple admissible horizons after the same horizon likelihood is used.
- `D2 = evidence_weighted_scope_mixture - scope_hypothesis_ensemble`:
  likelihood weighting while retaining scope uncertainty.

`hard_global` is a predeclared stress condition, not the comparator for the
primary scope-uncertainty estimand: it changes the asserted scope by extending
the directional claim beyond the supplied support.

## Factors

1. **Scope knowledge:** exact local horizon, narrow valid interval, broad valid
   interval, endpoint-unspecified support, covered biased interval, uncovered
   biased interval. On normalized scope width `W_h`, the candidate geometry is
   exact `{h*}`, narrow `h*±.10W_h`, broad `h*±.30W_h`, full-domain unspecified,
   covered bias `±.05W_h`, and uncovered bias `±.15W_h`. Supports are never
   clipped.
2. **Prefix exposure / directional evidence:** candidate B0 exposures end at
   `h*-.30W_h`, `h*-.12W_h`, and `h*-.03W_h`. All prefixes remain in the
   direction-valid region; the continuous prefix-derived `E_h` is reported
   separately.
3. **True scope:** task-specific `h*`, evaluated only after predictions have
   been fixed. It determines coverage and scope violation, not policy input.

The post-scope derivative is generated separately as
`f'(t)=b+r*b*(t-h*)/W_h` for `t>h*`, with frozen balanced modes such as
`r in {-2,0,+1}`. Thus `h*` remains a knowledge-warrant endpoint rather than a
turning point. The clean actual first direction-violation horizon `h_viol` is
stored separately and is right-censored when no violation occurs in the tested
domain.

For each task, the synthetic scale is frozen as
`R_ref=max_{t in Omega_ref} f(t)-min_{t in Omega_ref} f(t)`, with
`Omega_ref=[h*-.30W_h,h*+.80W_h]`. It is used only for task-normalized noise,
NRMSE, and the normalized-slope audit; it is never supplied to a policy. Both
the numerator and denominator of the slope audit use this same window:
`G_slope=W_h max_{t in Omega_ref}|f'(t)|/R_ref`. This common window prevents a
reverse realization's post-scope range from acting as a mode-specific scale.

## Predeclared hypotheses

1. With broad scope uncertainty and weak prefix evidence, retaining multiple
   locally constrained continuations will reduce far-OOD error relative to early
   single-horizon commitment.
2. When evidence identifies the viable scope, likelihood weighting will become
   more useful and retention's advantage will contract.
3. When the supplied directional knowledge has uncertain or finite scope,
   globally hard enforcement can incur post-scope error even when the direction
   was locally valid.

## Primary outcomes

- Far-OOD NRMSE and CRPS on a common post-prefix window.
- Distance-wise degradation.
- Oracle-scored within-scope error on `(common high-prefix end, h*]` and
  post-scope error on `(h*, h_far]`. `h*` is evaluation-only and never enters a
  policy path.
- Scope violation rate and excess post-scope error.
- Worst-valid and Worst-all error, retaining uncovered scope supports as a
  validity-failure stratum rather than hiding them.
- Scope-hypothesis entropy, truth-neighborhood scope mass, and wrong scope
  collapse/commitment for covered supports.

## Required A0 calibration

Before a confirmatory run, discarded-seed E15-B0 must freeze the shape family,
noise ratio, common far-OOD horizon, scope-support geometry, numerical
constraint solver, quota, and maximum attempts without inspecting directional
policy winners or contrast signs. Its primary construct-validity sanity is that
`E_h` changes across prefix exposures with retained overlap; if scope evidence
is absent at every exposure, the generator is inadequate rather than a reason
to tune policy outcomes. B0 additionally verifies that every prefix remains
strictly direction-valid, precursor profiles are finite on the full domain,
distinct scope hypotheses yield nondegenerate forecast solutions, deterministic
constraint residuals are within tolerance, both oracle-scored windows have
enough points, post-scope modes are balanced, and `h*` is never substituted for
the separately stored `h_viol`.

The policy-free numerical selection order is `gamma_0`, then noise ratio, then
far horizon. Candidate `gamma_0 W_h` values are `{2,4,6,8}`; B0 retains only
candidates with finite non-saturated low/high `E_h`, higher median concentration
at greater exposure with retained overlap, stable precursor/KKT diagnostics,
and median effective distinct constrained-solution count of at least four.
At the selected `gamma_0`, the largest noise ratio preserving the same evidence
geometry is selected; the longest horizon meeting finite, window-coverage,
reference-range, and normalized-slope gates is then selected. These choices do
not inspect policy forecast outcomes.

## Interpretation boundary

E15-B can establish a controlled utilization result for the frozen
direction-plus-finite-scope family only. It does not establish a universal rule
for curvature, bounds, or mechanistic invariants; those require separate
representative studies.
