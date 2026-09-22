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

- Prior family: one mechanistic regime change with onset `tau`, represented on
  normalized time `u=(t-tau_min)/W_tau`.
- Common predictive family: the frozen regime continuation family and the same
  fixed transition width and deterministic linear profile solve for every
  policy.
- The `a/b/c` ranges are generator sampling ranges only. Conditional on each
  fixed onset hypothesis `tau_k`, `a/b/c` are profiled by unconstrained,
  deterministic linear least squares; generator ranges are not fitting bounds.
- To isolate onset uncertainty, E15-A fixes `c=kappa*b` with `kappa=1`; only
  `a` and `b` are profiled at a candidate onset. The transition width is the
  common constant `s_0=.05W_tau`.
- Same noisy observed prefix, train/test split, noise realization, onset-grid,
  task seeds, and far-OOD evaluation points within each latent task.
- No policy receives future observations, the true onset, or support beyond
  `I`. Discrete policies use one common frozen onset grid on `I`; the
  continuous distributional policy uses a separately frozen numerical
  quadrature over that same support. The evidence-weighted policies may use
  the observed prefix only.
- This is a utilization study. `S`, `E_a`, scope, and completeness are stored
  as descriptors/strata, not optimized endpoints.

## Factors

### Knowledge state

1. `exact`: `I={tau*}`.
2. `narrow`: a valid interval centered on `tau*` with frozen half-width.
3. `broad`: a valid wider interval centered on `tau*`.
4. `existence_only`: the frozen admissible onset domain.
5. `covered_biased`: narrow-width interval shifted by `+/- .05W_tau`.
6. `uncovered_biased`: narrow-width interval shifted by `+/- .15W_tau`.
   `Coverage(I)=1(tau* in I)` and violation distance are recorded rather than
   hidden.

Biased rows are stratified into `covered_biased` and `uncovered_biased`.
When `tau*` is outside `I`, the true onset is not representable by
support-only policies; this knowledge-validity failure is never counted as
wrong concentration/commitment.

### Prefix exposure

`low`, `medium`, and `high` use a common frozen noise scale and vary only
prefix exposure. With onset-domain width `W_tau`, their prefix endpoints are
`tau*-0.20W_tau`, `tau*-0.05W_tau`, and `tau*+0.10W_tau`, respectively.
Task acceptance restricts `tau*` so these endpoints remain in the admissible
observation domain. These are exposure design factors, not labels copied into
analysis and not a claim about realized observability. Realized regime evidence
or observability is independently measured from the noisy prefix using the
frozen evidence statistic / profiled likelihood separation. Thus
`prefix exposure != realized observability`.

### Utilization policy

| Policy | Use of the same knowledge object `K` |
|---|---|
| `free_onset_baseline` | Common regime continuation family with no supplied onset support; it freely selects an onset over the admissible onset domain. |
| `hard_midpoint` | Deterministically commits to the midpoint of `I`; deliberately discards interval uncertainty when `I` is non-singleton. |
| `evidence_MAP_point` | Uses the common profiled prefix likelihood on the frozen grid, then commits to its single MAP onset. |
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
benefit of retaining multiple prior-consistent onsets after the same onset
likelihood has been used. For `exact`, uncertainty-retaining policies collapse
by design; this is a representation-equivalence audit, not an expected gap.

When `existence_only` spans the full admissible onset domain,
`free_onset_baseline` and `existence_only` `evidence_MAP_point` are expected to
be representation-equivalent. This is an audit, not a primary policy contrast.

For every frozen grid hypothesis `tau_k`, all evidence-using policies first
compute the identical profile score
`ell_k = min_(a,b,c) NLL(D_prefix | tau_k, a,b,c,s_0)`, using the same fixed
transition width `s_0` and deterministic linear least-squares rule.
`evidence_MAP_point` uses
`tau_MAP = argmin_k ell_k`; `evidence_weighted_mixture` uses
`w_k=exp[-(ell_k-ell_min)] / sum_j exp[-(ell_j-ell_min)]`. Therefore C1 differs
only in point commitment versus retention of the same likelihood-derived
weights, not in evidence or nuisance fitting.

The frozen soft objective is
`L=NLL_prefix+lambda[((tau_L-tau)_+/h_n)^2+((tau-tau_U)_+/h_n)^2]`, with
`lambda=1`. It is a soft utilization of the same interval knowledge, not an
information-preserving interval representation.

## Required implementation freezes before execution

1. Regime generator equation, nuisance-parameter ranges, fixed transition
   width `s_0`, prefix endpoints, far-OOD horizon, noise scale, task quota,
   and maximum generation attempts.
2. The following normalized numerical choices, where
   `W_tau=tau_max-tau_min`: narrow half-width `.10W_tau`, broad half-width
   `.30W_tau`, covered bias `+/- .05W_tau`, uncovered bias `+/- .15W_tau`,
   hypothesis-grid spacing `.025W_tau`, and wrong-onset tolerance
   `delta_tau=.05W_tau`.
3. Common noise-normalized linear least-squares profile rule and frozen
   design-matrix condition-number audit. No policy-specific tuning, validation
   selection, nonlinear optimizer, or future-dependent calibration.
4. Noise-normalized Gaussian prefix NLL. The soft objective is
   `L=NLL_prefix+lambda[((tau_L-tau)_+/h_n)^2+((tau-tau_U)_+/h_n)^2]`, with
   `lambda=1`; evidence-mixture weights use the untempered likelihood `T=1`.
5. Normalized entropy `H_tilde=H(w)/log(K)` for `K>1`, collapse threshold
   `H_tilde<.25`, normalized far-OOD catastrophic threshold
   `NRMSE_far=RMSE_far/R_ref>.50`, and distance bins covering forecast thirds
   `[0,1/3)`, `[1/3,2/3)`, and `[2/3,1]`.
6. Latent-task paired bootstrap (`B=5000`); policies and candidate hypotheses
   remain repeated measures within a task.
7. The continuous `distributional_prior` uses deterministic Gauss--Legendre
   quadrature with `N_quad=201` nodes on the same support `I`; it does not use
   a separate support or data-dependent quadrature rule. For exact support
   `I={tau*}`, it is evaluated directly as the degenerate distribution
   `delta(tau-tau*)`, rather than by a zero-width quadrature map.
8. No onset support interval may be clipped. A task is accepted only if both
   `[tau*-.30W_tau, tau*+.30W_tau] subseteq [tau_min,tau_max]` and the full
   low-to-high exposure-endpoint range
   `[tau*-.20W_tau, tau*+.10W_tau]` lie inside the frozen observation domain.
   The acceptance region is their intersection; failures are rejected and
   recorded, not repaired by boundary clipping.
9. `R_ref=max_{t in Omega_eval} f_clean(t)-min_{t in Omega_eval} f_clean(t)`.
   It is a synthetic evaluation-scale constant only: it is never supplied to
   a policy or fitted model. For a fixed noise ratio `rho=sigma/R_ref`, every
   latent task receives task-specific noise `sigma_i=rho*R_ref,i`, computed once
   from its clean reference trajectory on the frozen common reference horizon.
   The same `sigma_i` and standardized noise realization are shared by that
   task's prefix-exposure conditions; a candidate horizon never rescales noise.

## Realized onset evidence

Prefix exposure is a design factor; realized onset evidence is a continuous
task-level descriptor. It is computed independently of the supplied knowledge
interval, using the full admissible-domain frozen grid and the common profiled
scores `ell_k`:

`w_k^full=exp[-(ell_k-ell_min)] / sum_j exp[-(ell_j-ell_min)]`,
`E_tau=1-[-sum_k w_k^full log(w_k^full)]/log(K_full)`.

`E_tau` is onset-evidence concentration: values near zero indicate diffuse
prefix likelihood across admissible onsets, while values near one indicate
strong likelihood concentration. It is not thresholded into another design
factor. Primary effect modification is assessed continuously, for example by
the C1 paired contrast versus `E_tau`.

## Primary outcomes

- Far-OOD RMSE.
- Far-OOD CRPS for every policy. Point policies use the common observation
  noise predictive distribution `Normal(y_hat, sigma^2)`; mixture policies use
  the corresponding mixture predictive distribution.
- Worst-group far-OOD error across predeclared knowledge × prefix-exposure
  cells, with realized evidence reported separately.
- `Worst-valid`: worst-group error restricted to covered prior-support rows.
- `Worst-all`: worst-group error including uncovered biased rows.
- Catastrophic failure rate.
- Distance-wise degradation profile.
- Wrong concentration/commitment rate for point/mixture policies.
- Mixture entropy and truth-neighborhood mass `W_truth`, conditional on the
  prefix.

The prespecified primary contrasts within the same task and knowledge state
are: (C1) evidence mixture minus evidence-MAP point, isolating uncertainty
retention after identical onset-likelihood use; (C2) evidence mixture minus
uniform ensemble, isolating onset-likelihood weighting while retaining
uncertainty; and (C3) evidence-MAP point minus hard midpoint, isolating
onset-likelihood selection after point commitment. All other policy comparisons
are secondary. A claim that one policy
is preferable must be conditional on onset-uncertainty, prefix-exposure, and
realized-evidence strata; no universal policy ranking is sought.

## Predeclared hypotheses

1. With exact or very narrow valid onset knowledge, hard commitment may match
   uncertainty-retaining policies.
2. With broad onset uncertainty and low realized prefix evidence, early point
   commitment may produce more wrong commitment than policies that retain
   multiple onset hypotheses.
3. Lower realized prefix evidence may favor retaining mixture entropy, but this is an
   empirical hypothesis rather than a sanity gate.

Wrong concentration/commitment is defined only for covered knowledge states.
For a mixture, **wrong collapse** requires both `H_tilde(w) < .25` and
`|tau_MAP-tau*| > delta_tau`; for a point policy, **wrong commitment** uses the
same onset-error condition with its unit-mass weight. Exact (`K=1`) rows are
excluded from entropy-based collapse classification. Truth-neighborhood mass is
`W_truth=sum_{k:|tau_k-tau*|<=delta_tau} w_k`, avoiding an arbitrary demand
that `tau*` lie exactly on the discrete grid.

For `exact` support, the representation-equivalence audit applies to
`hard_midpoint`, `evidence_MAP_point`, `distributional_prior`,
`uniform_hypothesis_ensemble`, and `evidence_weighted_mixture`. A finite-
penalty `soft_constraint` is explicitly excluded from that equality audit.

## E15-A0 design-only calibration

Before the confirmatory run, an independent, discarded-seed E15-A0 pilot fixes
the remaining numerical generator and computation contract. It must not inspect
or compare the seven-policy prediction outcomes, rankings, RMSE, CRPS, or
collapse rates.

E15-A0 may inspect only: (1) generator admissibility and numerical stability;
(2) the spread and overlap of `E_tau` across the three prefix-exposure settings
at one common noise scale; (3) a common far-OOD horizon with post-onset support
and no numerical saturation; (4) the frozen linear-profile design-matrix
condition number; and (5) paired-contrast variance solely to choose a task
quota for a prespecified confidence-interval half-width. It then freezes the
regime equation, nuisance ranges, `s_0`, `sigma/R_ref`, far-OOD horizon, task
quota, maximum attempts, and all seeds/rules in a manifest. The E15-A0 tasks
are excluded from E15-A.

For sample-size calibration, E15-A0 may access only the variance (or standard
deviation) of prespecified paired loss contrasts on discarded pilot tasks.
Contrast means and signs, policy-specific means, rankings, cell-wise winners,
hypothesis tests, catastrophic-rate differences, CRPS comparisons, and
wrong-concentration/commitment comparisons are masked and unavailable. A
variance-only initial quota may use `n≈(1.96*s_delta/epsilon)^2`, followed by a
clustered-bootstrap precision check, where neither the mean nor sign of the
contrast is revealed.

Before any protected variance is accessed, E15-A0 freezes a target 95% CI
half-width `epsilon` for the paired far-OOD `NRMSE=RMSE/R_ref` contrast. The
primary quota cells are `C1/C2/C3 × knowledge state × prefix exposure`, limited
to covered knowledge states; uncovered-biased rows remain in `Worst-all` but do
not determine the core utilization-contrast quota. Exact-support rows are a
representation-equivalence audit with degenerate contrasts and are excluded
from this precision calculation. The final quota is the largest blinded
cellwise requirement. Given the A0 generator acceptance count,
`max_attempts` is then the smallest `N` with
`P[Binomial(N,p_L)<n_confirm]<1e-4`, where `p_L` is the conservative 95%
Wilson lower acceptance bound. Neither calculation may access a contrast mean,
sign, policy ranking, or winner.

## Interpretation boundary

E15-A evaluates a single event-prior family under controlled onset uncertainty.
It cannot rank shape-prior constraints or mechanistic shared invariants; those
are separate E15-B and E15-C studies. It also cannot establish that a mixture
is universally preferable: it tests whether utilization should depend on the
prior's specification uncertainty, prefix exposure, and realized evidence.
