# Experiment rules

## Scope and separation

1. 이 폴더의 evidence는 **generic synthetic evidence**다. PP-X 또는 다른
   repository의 method performance·real-data conclusion으로 인용하지 않는다.
2. 외부 dataset, package-specific code, PP-derived hyperparameter, dataset name을
   selector API에 전달하지 않는다.

## Frozen v1 contract

1. Seed `20260919`, boundary `.60`, tail endpoint `t > .70`, Gaussian noise SD
   `.015`, family당 7 sweep level × level당 60 trajectory를 실행 전에 고정했다.
2. **Generative-family oracle**은 full-information oracle이 아니다. Correct
   **family label만** 알려 주고, parameter는 observed prefix에서만 fit한다.
3. Far-OOD clean tail·tail statistic·family identity·true observability는 어떤
   admission score에도 사용할 수 없다.
4. Methods are: linear fallback, generative-family-oracle fit, contrast-family
   fit, uniform pseudo-OOD candidate selection, uniform generative-family gate,
   and tail-weighted generative-family gate.
5. Uniform gate is `A_uniform > 0`, where A is pseudo-OOD MSE improvement against
   linear fallback. Tail-weighted gate uses prespecified weights `.10/.25/.65` for
   the three chronological pseudo-OOD windows. No threshold is tuned on endpoint data.

## Evidence statuses

- `development`: result used to understand a mechanism or design a later protocol.
- `frozen_confirmation_pending`: code and rule are frozen, awaiting new independent
  draws or real evidence.
- `confirmatory`: a frozen rule evaluated once on genuinely unseen evidence.
- `negative`: a prespecified claim failed.

v1 is `development` even when a result is positive.

## Frozen v2 contract

1. v2 is specified in `ADMISSION_V2_PROTOCOL.md` and uses a new seed (`20260920`),
   a 4,500-task grid, and a held-out seed split. It is a new version, not a v1 edit.
2. Utility sign on the clean far-OOD tail is the admission-training label. It may be
   used only on v2 train seeds to fit the evidence classifier and only after prefix
   features are fixed. Test-seed labels are evaluation-only.
3. `O_true` is mechanism analysis only and is prohibited from the v2 feature matrix.
4. Do not adjust evidence primitives, feature transforms, classifier, or the `.50`
   threshold after reading locked test metrics; create v3 instead.

## Versioning and integrity

1. Never overwrite v1 results, figures, protocol, or the meaning of a v1 method.
2. Any change to family equations, sweep levels, seed, noise, split, candidate menu,
   score, gate threshold, metric, or acceptance rule requires `v2` in a new output
   directory.
3. Retain negative results and report them in `RESULTS_V1.md` and the PPT storyboard.
4. A rule inspired by v1 must be tested on a new seed and new parameter draw; it may
   not be presented as confirmation on v1.

## Exposure / identifiability extension

1. `exposure_identifiability_extension_v1` is a separate development experiment;
   it does not alter Oracle Decomposition v1.
2. Its generator, high-exposure grid, seed, bootstrap rule, and convergence
   threshold are frozen in `EXPOSURE_IDENTIFIABILITY_EXTENSION_PROTOCOL.md` before
   results are inspected.
3. “Convergence” is only a practical, generator-scoped statement: upper paired
   bootstrap 95% interval for the family-to-parameter RMSE gap is at most `.01`.

## Partial realization knowledge sweep

1. `partial_realization_knowledge_sweep_v1` is a separate development study at
   `O=.90`; it answers a knowledge-ablation question, not a complete
   exposure-by-knowledge interaction.
2. The frozen protocol defines the fields, all subset conditions, retrieval
   perturbations, seed, and paired bootstrap outputs before execution.
3. Treat noisy retrieved values as uncertain constraints. Do not describe the
   exact all-fields condition as a deployable RAG result.

## Required result record

Every version must save: generator config, split, seed, true observability definition,
method rules, per-level utility, bootstrap interval, score-label association, admit and
reject rates, result figures, and a prose decision record.
