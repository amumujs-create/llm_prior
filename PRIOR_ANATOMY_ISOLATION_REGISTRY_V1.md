# Prior Anatomy Experiment Isolation Registry v1

This registry is an audit index for the E9–E14 anatomy sequence. It does not
replace the execution freezes or results; it makes explicit what each
experiment intended to isolate, what was held fixed, and what it was not
allowed to claim. Earlier E1–E8 development and applicability experiments are
recorded in [EXPERIMENT_NOTE.md](EXPERIMENT_NOTE.md), sections 1–27, with their
own result artifacts.

## Common cross-experiment discipline

- A structural prior is not automatically a utility, safety, prediction, or
  trust claim.
- Clean future truth is allowed for generation and oracle validation only; it
  is not passed to the information scorer unless the experiment explicitly
  concerns oracle scope/coverage.
- Results distinguish construction/integrity invariants from empirical
  quantities. A designed coverage pattern, conjunction direction, or scope
  nesting direction is not reported as a scientific discovery.
- Continuation-bank, observation-prefix, likelihood normalization, floor, ESS,
  censoring, and task-cluster rules are frozen per experiment; comparisons do
  not silently change any of them.
- Every reported conclusion is grammar-, scope-, corpus-, and measurement-
  convention-relative unless explicitly validated elsewhere.

## Isolation matrix

| Experiment | Intended question | Isolated contrast | Held fixed / integrity conditions | Explicit exclusions and claim boundary |
|---|---|---|---|---|
| **E9 Information Lifecycle** | When does one supplied valid structural prior add information beyond an expanding observed prefix, and when does the data absorb it? | Prefix evidence only | Same latent task, true supplied prior, candidate bank, noise realization, task-level MSE normalization, and full-domain ambient bank; inactive coordinates fixed to zero/reference | No utility, engine, future target, safety, scope, completeness, or fragility claim. Endpoint grid resolution/censoring and low-ESS status are recorded, not discarded. |
| **E10 Scope / Validity Horizon** | How far does a locally valid prior remain continuously valid? | Post-boundary clean scope intervention | Frozen atom checker; primary event already before `.40` for event atoms; intervention is local after its onset and does not alter earlier trajectory; clean latent oracle only | Not data evidence, sharpness, utility, or primitive-persistence ranking. Scope tiers are controlled label-recovery conditions, not natural prevalence. |
| **E11 Grammar-relative Completeness** | Given a valid supplied prior and fixed scope, what valid canonical information is missing? | Supplied subset versus unique inclusion-maximal compatible coverage-preserving envelope | Frozen canonical atom-instance library and compatibility/scope registry; common task/data/bank; exact nested sharpness rule; unique-envelope-conditioned acceptance | Not world-completeness or a single “true best prior.” Atom incompleteness and conditional information incompleteness are separate; floor-censored gaps remain unresolved. |
| **E12-A Specification Fragility** | What happens when structural content remains correct but a numeric field is displaced? | Numeric field, sign, magnitude, baseline specification state | Same prefix/bank/weights; field-specific satisfaction semantics; paired latent metadata for regime/asymptote; baseline geometry stratified | Break thresholds are partly designed by interval width/margin, not primitive-intrinsic rankings. No prediction harm, utility, or safety conclusion; invalid-but-sharp is informational only. |
| **E12-B Content / Composition Fragility** | How do omission, false addition, and reversal differ as structural errors? | Error operation type and source/added atom | Future-independent operation catalog; registry-backed compatibility; per-task clean falsity/coverage checks; common task/bank/prefix; finite-bank support audit | Planned coverage (`1/0/0`) is integrity, not a discovery. Addition results are atom-stratified because the catalog is unbalanced; no general false-addition law or utility claim. |
| **E13 Joint Anatomy Map** | How do valid-prior information, evidence, scope, and completeness coexist on the same task? | Candidate subset within the same core-frozen realized envelope | Same task/prefix/bank/weights per subset; core-defined `P_star`; clean `V_a -> C_a -> C_P` scope oracle; measured—not requested—scope acceptance; dynamic true subsets | Core validity is conditioned on; definitional associations are masked. Full scope strata are balanced controls, not natural frequencies. Sparse `O_P` and saturated binary informativeness limit association claims. |
| **E14 Complexity Scaling (draft)** | Do E13 anatomy distinctions remain measurable under matched realization complexity? | Separately: dimension, interaction, heterogeneity | Exact realized `P_star` equality within a paired group; orthogonal branch backgrounds; energy/RMS matching; full-envelope scope matched as control; paired master banks and equal-context likelihood | Not a new grammar, dynamics study, utility/engine/LLM study, or generic full-scope scaling claim. E14-A starts only after field parameterizations and ranges are frozen. |

## What “isolated” means here

The experiments do not claim to isolate every causal mechanism in the world.
They isolate the named contrast **within a frozen synthetic causal construction**.
For example, E11 identifies a marginal restriction conditional on prefix plus
retained content; it does not attribute that redundancy separately to data or
to remaining atoms. Similarly, E13/E14 scope controls prevent full-envelope
scope from being read as a natural prevalence distribution.

## Traceability

- [E9 execution freeze](E9_EXECUTION_FREEZE_V1.md) · [E9 results](RESULTS_PRIOR_INFORMATION_LIFECYCLE_E9.md)
- [E10 results](RESULTS_PRIOR_SCOPE_VALIDITY_HORIZON_E10.md)
- [E11 execution freeze](E11_EXECUTION_FREEZE_V1.md) · [E11 results](RESULTS_PRIOR_COMPLETENESS_E11.md)
- [E12-A results](RESULTS_PRIOR_FRAGILITY_E12A.md) · [E12-B execution freeze](E12B_EXECUTION_FREEZE_V1.md) · [E12-B results](RESULTS_CONTENT_COMPOSITION_FRAGILITY_E12B.md)
- [E13 execution freeze](E13_EXECUTION_FREEZE_V1.md) · [E13 results](RESULTS_JOINT_PRIOR_ANATOMY_E13.md)
- [E14 protocol draft](COMPLEXITY_SCALING_E14_PROTOCOL_DRAFT_V1.md) · [E14 freeze checklist](E14_DESIGN_FREEZE_CHECKLIST_V1.md)
