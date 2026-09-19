# E12-A — Specification Fragility under Structured Misspecification

## What was tested

E12-A holds structural content fixed while moving only a numeric specification.
It compares regime onset, inflection location, turning location, lower-bound
level, and asymptotic limit over three baseline specification states and signed
perturbations. The primary estimand is stratified by
`field × baseline specification state × sign`.

This is a prior-anatomy experiment: it uses no prediction engine, RMSE,
utility, selection outcome, or safety label.

## Integrity

The frozen run accepted **450 latent trajectories**, produced **14,850
perturbation rows** and **2,700 signed endpoint rows**, and had zero exhausted
cells. All trajectories passed baseline coverage, paired-bank semantics,
safe-interior, finite-value, and ESS-invariance checks. No bound/asymptote
trajectory required a degenerate-range redraw (`R_ref < .05`).

The candidate bank was paired: `(f_m,z_m)`. Regime used mechanistic candidate
onset metadata; asymptote used latent mechanism/limit/approach-side metadata;
inflection, turning, and bound used the frozen trajectory-level satisfaction
checks. All `Delta S_spec` observations were exact—there were no floor hits.

## Results

![E12-A signed validity and confidently-wrong endpoints](figures/fig40_e12a_signed_endpoints.png)

The validity-break thresholds followed the intended baseline-margin geometry.
For two-sided fields, the near-edge baseline state broke at `.025` toward its
nearer boundary and at `.05` in the opposite direction; the centered state
broke at `.05` in both directions. This is a controlled tolerance result, not
a primitive-intrinsic fragility ranking.

For the one-sided lower bound, negative perturbations relaxed the claim and
remained valid through `.30`. Positive perturbations broke at the predeclared
distinct levels `.025`, `.05`, and `.10` for initial margins `.005`, `.035`,
and `.075`, respectively. This is the expected directional asymmetry of a
one-sided constraint.

Among the 2,430 signed rows where both endpoints were observed,
`epsilon_CW*` equaled `epsilon_break*` in **100%** of cases; the observed
median `Delta_epsilon_CW` was `0`. In this frozen ensemble, every tested
invalid specification was already conditionally sharp enough to meet the
`.10 nat` confidently-wrong criterion. The 270 negative-bound rows with no
validity break are correctly not-at-risk rather than assigned a zero or
censored CW gap.

![E12-A sharpness curves](figures/fig41_e12a_sharpness_curves.png)

Conditional sharpness was not uniform after validity failure. Regime onset and
asymptotic limit stayed nearly flat under displacement; inflection changed only
slightly. Turning-location specifications generally became sharper as the
location moved farther, while lower-bound sharpness increased when the bound
was tightened and decreased when it was relaxed. These are bank- and
field-semantics-dependent patterns, not predictive-harm claims.

## Interpretation boundary

E12-A supports a narrow controlled result: a numerically misspecified valid
specification need not weaken when it becomes invalid. Under the frozen bank
and `.10 nat` rule, invalid specifications immediately met the
confidently-wrong information criterion whenever a break occurred.

This does **not** establish that real scientific priors always become unsafe
at first invalidity. The break endpoint is partly determined by the deliberate
baseline-margin geometry, and the sharpness result is conditional on the
paired ambient-bank distribution and its semantic rules. Prediction utility,
actual deployment harm, structural/content errors, and engine compatibility
remain outside E12-A; they belong to later integration work and E12-B.

## Artifacts

- [E12-A protocol](PRIOR_FRAGILITY_E12A_PROTOCOL_DRAFT_V1.md)
- [E12-A execution freeze](E12A_EXECUTION_FREEZE_V1.md)
- [Paired-bank satisfaction registry](E12A_SATISFACTION_REGISTRY_V1.json)
- `results/prior_fragility_e12a/analysis/` — primary state-stratified curves,
  endpoint summary, floor status, and machine-readable summary.
