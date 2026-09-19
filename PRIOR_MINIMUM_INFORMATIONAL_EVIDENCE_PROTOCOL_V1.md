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

- **Identifiability / effect strength:** `.15, .50, .85` of the primitive's
  frozen valid range.
- **Realization freedom:** low/medium/high, operationalized as 1/3/5 uncertain
  continuation parameters in the candidate ensemble. The same prior constraint
  is checked, but the ensemble contains progressively more unconstrained
  realization degrees of freedom.
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

## Minimum evidence definition

Define the *admissible informational prefix* at a support level `s` only when
all three predeclared conditions hold:

1. `S(P|D_s) >= .10` (practically nontrivial conditional restriction);
2. `ESS_s >= 100` (sampler reliability); and
3. `E_struct,s >= .80` (the relevant structure is observed rather than supplied
   only as external truth).

`E_info*` is the first support in the ordered path satisfying all three.
If none satisfies, it is right-censored at `> .70` and called an
informational-null-at-tested-prefix task. The three components are always
reported separately; the composite is an operational decision label, not a
claim that they are identical constructs.

## Outputs

Report the distribution of `E_info*` by primitive and difficulty axis; the
right-censoring rate; component trajectories (`S`, `ESS`, `E_struct`); and the
relationship of future consequence to these information-only quantities without
using it in the definition. E9 does not test engine utility, prior scope, or
fragility; those belong to later E10/E11.
