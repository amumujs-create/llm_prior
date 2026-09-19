# Prior Applicability Factorial Confirmation v1 (E8)

## Purpose

The full-v1 conditional map is descriptive because its Latin-hypercube corpus
varies several coordinates simultaneously. E8 tests whether three selected
context pairs alter the realized utility/harm of a supplied structural prior
when all other listed conditions are held fixed. It does not train a Prior
Critic.

## Frozen design

- Scope: seven singleton primitives (`direction`, `curvature`, `inflection`,
  `turning`, `regime`, `bound`, `asymptote`) and the same spline/basis/ODE data
  generators and spline/neural realization engines as full v1.
- Replication: 20 independent deterministic draws per primitive × generator ×
  factorial cell, seed base `81000`.
- Candidate action: `true-full` for the first two factorials. The third uses
  `true-subset`, `true-full`, and `biased-specific` on the same generated task.
- Engine safety is never averaged for a target: records stay engine-conditioned.
  A robust task/action is unsafe if **either** realization engine is harmful.
- Practical class: normalized utility `(RMSE_baseline - RMSE_prior) / RMSE_baseline`;
  beneficial `> .02`, neutral `[-.02,.02]`, harmful `< -.02`; catastrophic harm
  is `RMSE_prior >= 2 × RMSE_baseline`.
- Inference: 5,000 deterministic nonparametric bootstrap replicates over
  latent tasks within each reported stratum. Report raw utility and harmful-rate
  95% intervals. This is a confirmation of selected factors, not a universal
  causal model beyond this generator/engine scope.

## Factorials

All values are normalized as in full v1. The omitted coordinates are fixed as
shown, so each targeted pair is independently manipulated.

| ID | Manipulated factors | Levels | Fixed coordinates |
|---|---|---|---|
| A | support fraction × noise ratio | `.35, .525, .70` × `.001, .01, .05` | `n=72`, exposure `.55`, distance `.40`, effect `.55`, heterogeneity `.10` |
| B | exposure × effect strength | `.10, .45, .80` × `.15, .45, .85` | support `.525`, `n=72`, noise `.01`, distance `.40`, heterogeneity `.10` |
| C | distance × knowledge specificity | `.10, .40, .80` × `{true-subset, true-full, biased-specific}` | support `.525`, `n=72`, noise `.01`, exposure `.55`, effect `.55`, heterogeneity `.10` |

For C, all three candidate tiers are scored on each generated latent task;
specificity is therefore a within-task comparison. The narrow-biased tier uses
the exact frozen full-v1 perturbation (`tau + .20`, rate `×1.5`, bound `+.20`).

## Endpoints and decision discipline

Primary endpoint per cell is engine-conditioned harmful rate. Secondary
endpoints are robust-unsafe rate, catastrophic-harm rate, beneficial rate,
median/mean raw utility, normalized utility, Coverage, conditional sharpness,
and ESS. The result is reported separately by primitive, generator, engine,
and pooled descriptive strata. No feature is admitted to a future Prior Critic
merely because this run is significant; replication across held-out
compositions/generator realizations remains required.
