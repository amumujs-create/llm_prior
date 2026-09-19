# E9 — Difficulty × Minimum Informational Evidence v1

## Question

For a true structural prior, how much of the same latent trajectory must be
observed before it offers reliable, nontrivial conditional continuation
information? This is deliberately upstream of realization engines and utility.

## Prefix path

Each latent task is generated once on `[0,1]`, then revealed at support
fractions `.20, .30, .40, .50, .60, .70`. Sampling density is fixed at 120
observations per unit progression (rounded), so a longer prefix has both wider
support and the corresponding observation count. Noise is held at 1% of the
clean prefix range. The target structural prior is true by construction.

## Three difficulty axes

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
20 deterministic latent draws per primitive × difficulty cell.

Future consequence is **not** manipulated in E9. The same latent trajectory
is used for every prefix in its path. Consequence/scope manipulation belongs to
E10, where it can be applied beyond a fixed anchor without changing the E9
prefix history.

## Information-only quantities

For every prefix, sample `M=4096` candidate continuations independently of the
candidate prior, condition them on prefix normalized MSE using a frozen
temperature, and compute:

- `S(P|D) = -log P_Q(f satisfies P | D)` with the frozen Laplace/floor rule;
- `ESS = (sum w)^2 / sum w^2`;
- continuation dispersion / effective realization multiplicity under the same
  weighted ambient ensemble, reported as a diagnostic alongside nominal DoF;
- structural-evidence score `E_struct`, a frozen prefix-only likelihood contrast
  between the target constraint and its registered alternatives.

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

The operational conditions comprising `E_joint*` are:

1. `S(P|D_s) >= .10` (practically nontrivial conditional restriction);
2. `ESS_s >= 100` (sampler reliability); and
3. `E_struct,s >= .80` (the relevant structure is observed rather than supplied
   only as external truth).

Missing endpoints are not collapsed to one label. A task is
`informational-null-at-tested-prefix` only if reliable (`ESS >= 100`) prefixes
remain below the sharpness threshold. A task with no `E_joint*` is
`joint-unresolved`; persistent `ESS < 100` is separately `sampler-unresolved`.
The components are always reported separately; composite labels are operational
states, not claims that their constructs are identical.

At each reliable prefix, classify the lifecycle state without using future
outcomes: **external-informative** (`S>=.10, E_struct<.80`), **observed+
informative** (`S>=.10, E_struct>=.80`), **observed+redundant** (`S<.10,
E_struct>=.80`), or **unresolved** (neither criterion). Prefixes with
`ESS<100` receive a separate measurement-unreliable flag rather than a state.

## Outputs

Report the distributions of `E_add*`, `E_obs*`, `E_joint*`, and `E_red*` by
primitive and difficulty axis; their right-censoring and unresolved-reason
rates; component trajectories (`S`, `ESS`, `E_struct`, multiplicity); and
lifecycle-state transitions. E9 does not test engine utility, future
consequence, prior scope, or fragility; those belong to later E10/E11.
