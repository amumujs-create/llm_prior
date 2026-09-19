# E8 — Prior Applicability Factorial Confirmation v1

## Execution integrity

- Frozen protocol hash: `6c99d1d25a5699d47343fe8423234da0da100f4e9d43d77b399589368237d776`
- Latent tasks: 8,820; engine-conditioned records: 22,680.
- Seven singleton primitives × three data generators × 20 deterministic draws
  per factorial cell.
- Two realization engines were stored separately; solver failures: 0.
- Records SHA-256:
  `06a4d6594e86a03411a3f538cc87208d61951aa1bbb931ef22c02e1e34bc0d2b`.
- Inference: 5,000 within-stratum bootstrap replicates.

## What this confirms

This is a controlled confirmation of selected *context dependence* in the
tested generator/engine scope, not a general causal law of extrapolation.

1. **Engine safety cannot be safely collapsed by averaging.** Across all E8
   task/action pairs, the harmful/not-harmful decision disagreed between spline
   and neural realizations in 40.7% (4,617/11,340) of cases. Accordingly, E8
   reports both engine-conditioned harm and a robust-unsafe target: harmful in
   either engine.

2. **Effect strength changes applicability under held-fixed conditions.** With
   exposure held fixed, robust-unsafe rates increase from .60–.61 at effect
   strength `.15` to .70–.71 at `.85`. Mean raw utility changes from positive
   at `.15` to negative at `.45` and `.85`; all corresponding bootstrap CIs
   are available in the summary table. In this generator, the frozen
   effect-strength coordinate is an applicability determinant, not merely a
   label.

3. **Specificity does not dominate uniformly across horizon or engine.** At
   distance `.80`, neural harmful rates are .22 biased-specific, .50 true-full,
   and .33 true-subset, while spline rates are .57, .59, and .56 respectively.
   The robust-unsafe rate remains high for every tier (.69–.77 across tested
   distances). This directly confirms why engine-specific and robust targets
   are safer than an engine-average utility label for a future critic.

## Important qualification

The support × noise factorial is manipulated in full-v1 coordinates: distance
is fixed **relative to support width**. Raising support therefore also changes
the absolute forecast span and the generator's physical progression. Its
robust-unsafe pattern (.56–.80) must not be paraphrased as “more data is more
dangerous,” nor can the reduction at higher noise be paraphrased as noise being
protective. A later fixed-absolute-horizon design is required to isolate those
mechanisms. This result still succeeds at its primary purpose: it invalidates a
context-free prior score and exposes realization-engine dependence.

## Consequence for the Prior Critic

The critic should first be evaluated in two formulations, rather than trained
on an engine average:

- **engine-conditioned:** estimate `P(harm | prefix, candidate, context,
  realization engine)`;
- **robust:** estimate whether either registered realization is harmful.

The three E8 factor pairs are legitimate prefix/context feature candidates;
they are not deployment thresholds. A future held-out composition/primitive
evaluation is still required before claiming prior-space generalization.

## Artifacts

- [Protocol](PRIOR_APPLICABILITY_FACTORIAL_CONFIRMATION_PROTOCOL_V1.md)
- `experiments/run_prior_applicability_factorial_confirmation_v1.py`
- `experiments/analyze_prior_applicability_factorial_confirmation_v1.py`
- `results/prior_applicability_factorial_confirmation_v1/run/records.csv`
- `results/prior_applicability_factorial_confirmation_v1/analysis/factorial_summary_bootstrap.csv`
- `results/prior_applicability_factorial_confirmation_v1/analysis/robust_unsafe_by_task.csv`
- `figures/fig31_e8_applicability_factorial.png`
