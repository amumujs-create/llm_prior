# Prior Benchmark v1.1 — Measurement-Resolvability Sanity Protocol

**Status:** frozen after v1 failure and before v1.1 outcomes. This is a new
protocol version; it does not reinterpret the v1 gate as passed.

## Construct correction

Logical specificity and effective conditional specificity are different:

`P_narrow subset P_medium subset P_broad`

does not imply strict

`S_narrow > S_medium > S_broad`

after conditioning on observed data. If the prefix already restricts the
continuation ensemble inside all three constraints, all three conditional
sharpness values may legitimately approach zero.

## V1.1 endpoints

### A. Logical nesting sanity — validity gate

Using the same weighted samples for all nested candidates:

- constraint-set inclusion must hold exactly;
- `S_narrow >= S_medium >= S_broad` within numerical tolerance `1e-8`;
- conjunction monotonicity `S(A AND B) >= S(A)-1e-8`;
- zero violations are required.

Equality is valid and is not treated as measurement failure.

### B. Empirical resolvability — diagnostic, not a universal pass gate

Repeat each primitive under a separately seeded data-limited condition:

- observed-support fraction `.35`;
- 24 equally spaced prefix observations;
- Gaussian noise SD `.03` times the clean observed-target range;
- normalized evaluation distance `.10`;
- 40 paired specifications per primitive and generator;
- seeds `51001,51002,51003` for spline, basis, and ODE;
- frozen `M=4096`, prefix MSE, temperature, smoothing, floor, and ESS rules.

Report by primitive and sampler:

- `DeltaS_MB=S_medium-S_broad`;
- `DeltaS_NM=S_narrow-S_medium`;
- `DeltaS_NB=S_narrow-S_broad`;
- median and paired 95% bootstrap interval;
- fraction strictly positive and fraction exceeding `.05` nat.

No primitive is forced to exceed `.05`. A persistent near-zero result means its
specificity ladder is logical-only under the tested ensemble, not that the
estimator failed.

### C. Saturation and informational-null diagnostics

Predeclare saturation as `S_narrow<.01` nat. Report the fraction where all
three correct candidates are saturated, separately for the original data-rich
condition and the v1.1 data-limited condition. An **informational null** occurs
when every coverage-preserving registered candidate has `S<.10` in both frozen
ensembles. Report it by primitive; do not pool it with structural null.

### D. Structural-null validation — separate validity gate

Structural-null labels use generator and truth checks only, never sharpness or
utility. Validate the frozen out-of-grammar generator independently. At least
95% of accepted draws must satisfy all structural-null checks, with zero
utility-based or sharpness-based relabeling. Generator exhaustion is reported
as failure, not converted to informational null.

## Decision rule

Full benchmark execution remains blocked unless logical nesting, conjunction,
generator/checker recovery, confidently-wrong behavior, sampler rank
robustness, and structural-null validation pass. Empirical resolvability and
informational-null rates are anatomy results, not universal validity gates.

