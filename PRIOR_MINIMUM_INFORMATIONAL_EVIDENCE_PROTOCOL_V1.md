# E9 — Difficulty × Minimum Informational Evidence v1

## Question

For a supplied valid structural prior, how much of the same latent trajectory must be
observed before it offers reliable, nontrivial conditional continuation
information? This is deliberately upstream of realization engines and utility.

## Prefix path

Each latent task is generated once on `[0,1]`, then revealed at support
fractions `.20, .30, .40, .50, .60, .70`. Sampling density is fixed at 120
observations per unit progression (rounded), so a longer prefix has both wider
support and the corresponding observation count. For each task, make one master
observation grid `x_k=k/120` through `.70`, set noise SD once to 1% of the
clean `[0,.70]` range, and draw one noise realization. Every prefix reveals a
nested subset of those identical noisy observations; no prefix redraws points
or changes its noise scale. The supplied structural constraint is valid by
construction within the registered grammar; it is not asserted to be the
unique or globally best real-world prior.

## Two difficulty axes

- **Structural separability (a controlled source of practical
  identifiability):** low/medium/high are *predeclared generator parameters*
  governing prefix contrast between the target constraint and registered
  alternative continuations. They are assigned before data generation, never
  from measured `E_struct`; measured `E_struct` is the outcome.
- **Realization freedom:** low/medium/high, operationalized as 1/3/5 active
  uncertain continuation coordinates in a **single shared ambient ensemble**.
  Ensemble basis, coefficient scale, likelihood temperature, and reference
  measure are frozen; only the active-coordinate count changes. This avoids
  conflating DoF with a different sampler or sharpness definition.
The v1 scope is seven singleton primitives, three generator realizations, and
20 deterministic latent draws per primitive × difficulty cell. For every one
latent task, all three nested freedom levels are evaluated:
`T_i -> {d=1, d=3, d=5} -> {s=.20,...,.70}`. They are not separately drawn
tasks.

Future consequence is **not** manipulated in E9. The same latent trajectory
is used for every prefix in its path. Consequence/scope manipulation belongs to
E10, where it can be applied beyond a fixed anchor without changing the E9
prefix history.

## Information-only quantities

For each latent task, draw **one** frozen ambient continuation bank of
`M=4096` samples independently of the candidate prior. Reuse that exact base
bank across all six prefixes and all three freedom levels; only the
prefix-likelihood weights and the nested active-coordinate subset change. The
nested activation order is fixed as `1 subset 3 subset 5 = {z1} subset
{z1,z2,z3} subset {z1,...,z5}`. Each coordinate basis is L2-normalized on the
fixed future grid before applying an equal influence scale, so nominal count is
not confounded by arbitrary coordinate amplitude.

Condition this shared bank on prefix normalized MSE using a frozen temperature,
and compute:

- `S(P|D) = -log P_Q(f satisfies P | D)` with the frozen Laplace/floor rule;
- `ESS = (sum w)^2 / sum w^2`;
- effective parameter dimension
  `d_eff=(tr Sigma_w)^2 / tr(Sigma_w^2)`, where `Sigma_w` is the weighted
  covariance of active ambient coordinates;
- function-space dispersion `V_f=(1/|G|) sum_{x in G} Var_w[f(x)]` on the
  fixed future reference grid `G`.
- structural-evidence score `E_struct`, a frozen prefix-only likelihood contrast
  between the target constraint and its registered alternatives.

For **every** prefix, both the continuation functions and the prior-satisfaction
indicator in `S(P|D_s)` are evaluated on the same fixed target domain
`G=[.70,1.00]` (161 points). Thus sharpness changes are not caused by shrinking
the future region as observed support grows.

Coverage is 1 by construction for the supplied true prior and is retained only
as a checker invariant. No future target, utility, realization engine, or
far-OOD prediction enters any E9 input or endpoint.

## Information lifecycle endpoints

At a support level `s`, prior-added information is present when
`S(P|D_s) >= .10` and `ESS_s >= 100`; structural observation is present when
`E_struct,s >= .80`.

- `E_add*` is the first prefix with prior-added information, irrespective of
  whether the data yet observes the structure.
- `E_obs*` is the first prefix with `E_struct >= .80`.
- `E_joint*` is the first prefix satisfying all three conditions.
- `E_red*` is the first prefix at or after `E_joint*` with `E_struct >= .80`,
  `S(P|D) < .10`, `ESS >= 100`, and the same three redundancy conditions at
  the immediately next available prefix. It marks that data has made the
  prior's *additional* restriction practically redundant; it does not mean the
  prior became false.

These endpoints need not exist or occur in a universal order because
conditional sharpness is not assumed monotone. Missing endpoints are
right-censored beyond `.70`.

All endpoints are grid-resolved tested onsets, not exact continuous thresholds:
if first success is `.40`, report `.30 < E* <= .40`; success at `.20` is
left-censored `E* <= .20`; no success by `.70` is right-censored `E* > .70`.
Report attainment curves `P(E* <= s)` rather than treating censored values as
observed at `.70`; if 50% are censored, report `median > .70`.

The operational conditions comprising `E_joint*` are:

1. `S(P|D_s) >= .10` (practically nontrivial conditional restriction);
2. `ESS_s >= 100` (sampler reliability); and
3. `E_struct,s >= .80` (the relevant structure is observed rather than supplied
   only as external truth).

Missing endpoints are not collapsed to one label. A task is
`informational-null-at-tested-prefix` only when `ESS_.70 >= 100` and
`max_{s<=.70, ESS_s>=100} S(P|D_s) < .10`. If `ESS_.70 < 100`, it is
`sampler-unresolved-at-tested-prefix`, irrespective of earlier low-sharpness
prefixes. A task with no `E_joint*` but final reliable measurement is
`joint-unresolved` unless it meets the stricter informational-null rule.
The components are always reported separately; composite labels are operational
states, not claims that their constructs are identical.

At each reliable prefix, classify the lifecycle state without using future
outcomes: **external-informative** (`S>=.10, E_struct<.80`), **observed+
informative** (`S>=.10, E_struct>=.80`), **observed+redundant** (`S<.10,
E_struct>=.80`), or **unresolved** (neither criterion). Prefixes with
`ESS<100` receive a separate measurement-unreliable flag rather than a state.

Record redundancy re-entry
`R_reentry = I[exists s > E_red*: S(P|D_s)>=.10 and ESS_s>=100]`, so a first
redundant episode is not silently treated as persistent redundancy. `E_red*`
is identifiable only at `.20` through `.60`: redundancy first seen at `.70`
cannot be confirmed without a subsequent prefix and remains right-censored.
If no prefix follows a confirmed `E_red*` (for example `.60` uses `.70` as its
confirmation), re-entry is right-censored/NA rather than recorded as zero.

## Outputs

Report the distributions of `E_add*`, `E_obs*`, `E_joint*`, and `E_red*` by
primitive and difficulty axis; their right-censoring and unresolved-reason
rates; component trajectories (`S`, `ESS`, `E_struct`, multiplicity); and
lifecycle-state transitions. E9 does not test engine utility, future
consequence, prior scope, or fragility; those belong to later E10/E11.

## Frozen design constants and inference

The primitive-independent separability generator coefficient is fixed at
`eta in {.20, .50, .80}` for low/mid/high, where `eta` is the pre-generation
mixture weight of the registered structural alternative's prefix component; it
is never selected from observed `E_struct`. The common ambient-coordinate
influence scale is `.10`; temperature is `.02`; and the fixed future grid has
161 equally spaced points from `.70` to `1.00`.

All uncertainty intervals and within-task DoF contrasts use 5,000 paired
nonparametric bootstrap replicates over latent task IDs. Each resampled task
retains its complete `{d=1,3,5} × {six prefixes}` trajectory; prefixes or DoF
levels are never independently resampled.
