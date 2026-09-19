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
  identifiability):** low/medium/high prefix contrast between the target
  constraint and registered alternative continuations. It is not called effect
  strength and is reported separately from all other axes.
- **Realization freedom:** low/medium/high, operationalized as 1/3/5 active
  uncertain continuation coordinates in a **single shared ambient ensemble**.
  Ensemble basis, coefficient scale, likelihood temperature, and reference
  measure are frozen; only the active-coordinate count changes. This avoids
  conflating DoF with a different sampler or sharpness definition.
- **Future consequence:** low/medium/high, operationalized by a frozen
  continuation-divergence multiplier `.5/1.0/2.0` after the observed boundary.
  This is recorded for later E10/utility linkage but does not enter E9's
  information endpoint.

The v1 scope is seven singleton primitives, three generator realizations, and
20 deterministic latent draws per primitive × difficulty cell.

## Information-only quantities

For every prefix, sample `M=4096` candidate continuations independently of the
candidate prior, condition them on prefix normalized MSE using a frozen
temperature, and compute:

- `S(P|D) = -log P_Q(f satisfies P | D)` with the frozen Laplace/floor rule;
- `ESS = (sum w)^2 / sum w^2`;
- structural-evidence score `E_struct`, a frozen prefix-only likelihood contrast
  between the target constraint and its registered alternatives.

Coverage is 1 by construction for the supplied true prior and is retained only
as a checker invariant. No future target, utility, realization engine, or
far-OOD prediction enters any E9 input or endpoint.

## Information lifecycle endpoints

At a support level `s`, structural observation is present when
`E_struct,s >= .80`; reliable conditional information is present when it also
has `S(P|D_s) >= .10` and `ESS_s >= 100`.

- `E_obs*` is the first prefix with `E_struct >= .80`.
- `E_joint*` is the first prefix satisfying all three conditions.
- `E_red*` is the first prefix at or after `E_joint*` with `E_struct >= .80`,
  `S(P|D) < .10`, and the same redundancy condition at the immediately next
  available prefix. It marks that data has made the prior's *additional*
  restriction practically redundant; it does not mean the prior became false.

These endpoints need not exist or occur in a universal order because
conditional sharpness is not assumed monotone. Missing endpoints are
right-censored beyond `.70`.

The operational conditions comprising `E_joint*` are:

1. `S(P|D_s) >= .10` (practically nontrivial conditional restriction);
2. `ESS_s >= 100` (sampler reliability); and
3. `E_struct,s >= .80` (the relevant structure is observed rather than supplied
   only as external truth).

If `E_joint*` does not exist, it is right-censored at `> .70` and called an
informational-null-at-tested-prefix task. The three components are always
reported separately; the composite is an operational decision label, not a
claim that they are identical constructs.

## Outputs

Report the distributions of `E_obs*`, `E_joint*`, and `E_red*` by primitive and
difficulty axis; their right-censoring rates; component trajectories (`S`,
`ESS`, `E_struct`); and the
relationship of future consequence to these information-only quantities without
using it in the definition. E9 does not test engine utility, prior scope, or
fragility; those belong to later E10/E11.
