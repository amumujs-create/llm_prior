# Full Benchmark v1 — Conditional Prior Applicability Map

## Question

This secondary analysis asks whether a prior has a fixed quality, or whether
its realized utility changes with observed-data informativeness, extrapolation
horizon, and problem complexity. The estimated object is therefore
`U(P | D, h, C)`, not a context-free score `Q(P)`.

## Locked-data analysis

No generator, task, candidate, realization engine, target, or scoring rule was
changed. The analysis uses the locked 3,375-task full-v1 output and averages
the two realization engines per task/action. For the main maps it restricts to
non-null `true-full` candidates, so calibration error is not conflated with
data/horizon conditions. The `distance × specificity` map compares
`true-subset`, `true-full`, and `biased-specific` tiers.

The seven frozen LHS coordinates are split descriptively into equally sized
low/mid/high terciles:

- observed support fraction;
- sample count;
- noise ratio;
- mechanism exposure;
- normalized OOD distance;
- `effect_strength`, the protocol's operational identifiability proxy;
- unit heterogeneity.

The three predeclared descriptive interactions are support × noise, exposure ×
effect strength, and distance × knowledge tier. Outputs report coverage,
sharpness, ESS, median raw utility, median normalized utility, beneficial /
neutral / harmful rates, and catastrophic-harm rate.

## Result

The map rejects a simple context-free ranking of the seven primitives. In the
pooled true-full profile, harmful rate ranges from .328 (direction) and .346
(curvature) to .548 (regime) and .616 (turning), despite coverage being 1 for
every row. Thus identical structural truth does not imply a common operating
region or safe realization probability.

The pooled interaction maps do **not** show a universal monotone law such as
"more support always lowers harm" or "farther distance always increases harm."
For example, pooled support × noise harmful rates range from .371 to .518, and
pooled exposure × effect-strength rates range from .429 to .502. This is not a
claim that noise or horizon are protective. The corpus jointly varies several
coordinates and structural mechanisms, so these tables are descriptive strata,
not isolated causal effects. The non-monotonicity is itself a useful warning:
one scalar distance or data-volume rule is not an adequate prior-trust policy.

Accordingly, v1 identifies the conditional-analysis target and candidate
features for a future Prior Critic; it does not train or validate that critic.
Any condition rule selected from these maps must be confirmed in a separately
frozen factorial follow-up rather than promoted directly to deployment logic.

## Artifacts

- `experiments/analyze_full_benchmark_applicability_v1.py`
- `results/full_benchmark_v1/applicability/prior_applicability_profile.csv`
- `results/full_benchmark_v1/applicability/true_full_condition_strata.csv`
- `results/full_benchmark_v1/applicability/complexity_profile.csv`
- `results/full_benchmark_v1/applicability/interaction_support_noise.csv`
- `results/full_benchmark_v1/applicability/interaction_exposure_identifiability.csv`
- `results/full_benchmark_v1/applicability/interaction_distance_specificity.csv`
- `figures/fig30_full_v1_conditional_applicability.png`
