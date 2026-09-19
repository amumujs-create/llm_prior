# Prior Primitive–Composition Benchmark v1 — Full Run

**Scope.** This is the frozen 1D progression-to-scalar grammar benchmark, not
a claim about all real-world priors. It tests seven primitives and their
registered compositions under two data-driven realization engines.

## Execution integrity

- Corpus: 3,375 tasks; 2,700 non-null and 675 non-pooled null tasks.
- Scoring: 40,500 candidate-engine records (`6 actions × 2 engines/task`).
- Conditional-sharpness ensemble size: 4,096.
- Solver failures: 0.
- Record verification: passed, including action pairing, finite values,
  abstention invariance, baseline pairing, and coverage-class invariants.

## Headline findings

1. **Truth/coverage and information are not sufficient for safe realization.**
   `true-full` has coverage 1 and higher sharpness than `true-subset` (2.345
   versus .629 pooled), but it still has a 43.2% harmful rate and 12.7%
   catastrophic-harm rate. This run therefore reinforces the distinction
   between structural truth, information, and deployment utility.

2. **Miscalibrated specificity is the most hazardous tested knowledge tier.**
   The narrow-biased candidate has 0 coverage, sharpness 5.727, harmful rate
   57.8%, and catastrophic-harm rate 31.3%. This is the benchmark's
   `confidently wrong` region.

3. **Composition information does not have a universal utility sign.**
   Composition-level `DeltaS` is positive by construction, but `DeltaU` ranges
   from strongly negative to positive. Some additions are redundant; some are
   harmful under the tested realization; and a small subset is beneficial.

4. **Structural and informational nulls justify abstention under this run.**
   Abstention has exactly zero incremental utility/harm by definition. Every
   supplied non-abstain action on informational nulls has a harmful rate of at
   least 58%; structural-null proposals are also frequently harmful. This is
   not a prevalence claim about real nulls—only a benchmark validity result.

## Normalization qualification

The frozen normalized utility is `u=(RMSE_B-RMSE_P)/RMSE_B`. It is intentionally
reported with 5,000-replicate hierarchical bootstrap CIs, but its macro mean is
highly sensitive to tasks whose baseline RMSE is near zero. For example,
`true-full` has mean raw utility +.00489 and median normalized utility +.116,
while its macro normalized mean is negative because of the low-baseline tail.
Therefore every conclusion uses the joint panel: raw DeltaRMSE, median and
macro normalized utility, beneficial/neutral/harmful rates, and catastrophic
harm. A normalized mean alone is not interpreted as a complete effect summary.

## Interpretation boundary

The benchmark establishes an anatomy under the frozen generator/engine pair.
It does **not** establish that any primitive is intrinsically good or useless.
In particular, inflection and turning remain part of the vocabulary: their
utility and information are data-condition-dependent outcomes, not deletion
criteria. Generator robustness tables are reported to identify where a claim
does or does not repeat across spline, basis, and ODE generation.

## Artifacts

- `results/full_benchmark_v1/run/verification.json`
- `results/full_benchmark_v1/analysis/primitive_anatomy.csv`
- `results/full_benchmark_v1/analysis/composition_deltaS_deltaU.csv`
- `results/full_benchmark_v1/analysis/hurdle_map.csv`
- `results/full_benchmark_v1/analysis/knowledge_sensitivity.csv`
- `results/full_benchmark_v1/analysis/generator_robustness.csv`
- `results/full_benchmark_v1/analysis/null_abstention.csv`
- `results/full_benchmark_v1/analysis/hierarchical_bootstrap.csv`
- `figures/fig27_full_v1_anatomy_composition.png`
- `figures/fig28_full_v1_hurdle_map.png`
- `figures/fig29_full_v1_knowledge_null.png`
- [Conditional applicability analysis](RESULTS_FULL_BENCHMARK_V1_APPLICABILITY.md)
- `figures/fig30_full_v1_conditional_applicability.png`
