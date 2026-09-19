# E12-A — Specification Fragility under Structured Misspecification

## Research question

For a **supplied valid structural prior** whose structural content is held
fixed, how much error in its numerical realization can be tolerated before it
loses coverage, and does the misspecified constraint become sharp while wrong?

E12-A is deliberately prior-only. It contains no prediction realization
engine, RMSE, utility, harm rate, or future-target model selection. Those are
downstream deployment questions.

## Fixed interpretation

`E12-A` changes a numerical statement inside an otherwise unchanged structural
claim. `E12-B` will separately study false structural additions, reversals, and
omissions. E12-A must not be used to claim that a numeric calibration error is
equivalent to a wrong structural family.

All statements are evaluated on the declared scope `Omega=[.40,.80]`; the
observed prefix is `[0,.40]`. The continuation target used for conditional
sharpness is the same fixed `Omega`, so an apparent change in information is
not caused by moving the target domain.

## Frozen field corpus

Only canonical atoms with an unambiguous scalar realization field enter
E12-A-v1. Each base task supplies one valid atom instance and its frozen true
field value `theta*`.

| Structural content held fixed | Realization field `theta` | Parameter range `R_theta` | Fixed specification half-width `w` |
|---|---|---:|---:|
| `regime_postchange` | first regime onset | `.40` | `.025 R_theta` |
| `inflection_concave_to_convex` | inflection location | `.40` | `.025 R_theta` |
| `turning_maximum` | turning location | `.40` | `.025 R_theta` |
| `lower_bound_0` | lower-bound level | task-level clean target range `R_ref` | `.025 R_ref` |
| `asymptote_to_0_from_above` | latent asymptotic limit | task-level clean target range `R_ref` | `.025 R_ref` |

Location ranges are the width of `Omega`; level ranges use the fixed task-level
reference range. Direction and unsigned curvature are intentionally absent:
within the v1 canonical grammar they have no separately declared scalar
realization field. Their content fragility belongs in E12-B, not in a
made-up numeric sweep.

Each specification is an interval constraint:

`P_epsilon: |theta - (theta* + s epsilon R_theta)| <= w`, where
`s in {-1,+1}`. At `epsilon=0`, the supplied specification is valid by
construction. For zero, only one row is written; nonzero magnitudes are
evaluated in both signs.

The predeclared grid is `epsilon in {0,.025,.05,.10,.20,.30}`. It is a
normalized displacement grid, not a claim that these values represent equal
physical error across primitives.

## Corpus and repeated measures

Generate `5 fields × 3 generator families × 30 latent seeds = 450` base tasks.
For every base task, evaluate the same nested master observation realization
and the same 4,096-member full-domain ambient continuation bank at eleven
misspecifications (`0`, plus both signs at the other five magnitudes). The
planned output is **4,950 repeated task-field-perturbation rows**.

Task generation, noisy prefix creation, and ambient bank sampling use separate
fixed seed streams. The prior perturbation is a deterministic transform of the
already accepted task; it cannot alter the latent trajectory, observations, or
bank.

## Measurements

### Oracle-only validity stage

The clean latent trajectory and true scalar field are accessible only here.

- `Coverage_epsilon = I(theta* satisfies P_epsilon)`.
- `D_violation_epsilon` is the normalized amount by which the true field
  falls outside the declared interval:
  `max(|theta*-(theta*+s epsilon R_theta)|-w,0)/R_theta`.

For lower bounds this must also be cross-checked against the trajectory form:
`max_x(L_epsilon-f*(x))_+/R_ref`. The two values must agree up to numerical
tolerance. Event fields use normalized event-location error. The asymptote
field uses the declared latent-assisted limit, and is reported separately from
phenomenological trajectory checks.

### Data-conditioned information stage

The scorer receives only the observed prefix, frozen bank, and declared
`P_epsilon`. It does not receive the clean future, `theta*`, coverage,
violation, prediction, utility, or an engine output.

With the fixed E9/E11 weighting convention, record:

- `S(P_epsilon | D)` and effective sample size `ESS`;
- `Delta S_spec(epsilon)=S(P_epsilon|D)-S(P_0|D)`;
- probability-floor flags and saturation counts.

Primary sharpness interpretation requires `ESS >= 100`. Floor results are
reported as censored/lower-bound quantities, never converted to exact gaps.

## Endpoints and classifications

For each task × sign, the **grid-resolved validity-break threshold** is the
first tested nonzero `epsilon` with `Coverage_epsilon=0`. If no failure occurs
through `.30`, it is right-censored as `> .30`; it is not called infinitely
robust. The two signs remain separate primary endpoints:
`epsilon_break,+*` and `epsilon_break,-*`.

Report by field and sign:

- coverage and violation-severity curves over `epsilon`;
- sharpness and ESS curves over `epsilon`;
- attainment curves `Pr(epsilon_break* <= epsilon)`;
- directional asymmetry, without pooling signs into a false symmetric score.

A row is **confidently wrong** only when all of the following hold:

`Coverage_epsilon=0`, `ESS>=100`, and `S(P_epsilon|D)>=.10 nat`.

This is a diagnostic classification, not a utility or safety label. A valid
but low-sharpness perturbation is weak; an invalid and sharp perturbation is
potentially dangerous in an information-theoretic sense, but E12-A cannot say
how harmful its use would be for prediction.

## Integrity sanity before full run

The sanity suite must check implementation integrity, not preferred scientific
outcomes:

1. `epsilon=0` has coverage one for every accepted base task.
2. The clean trajectory, noisy prefix, and ambient bank are byte-identical
   across all perturbations of a base task.
3. Observed prefix and target `Omega` are invariant over `epsilon`.
4. Oracle coverage/violation code is unavailable to the sharpness scorer.
5. Bound's parameter- and trajectory-based violation distances agree.
6. All `S`, `ESS`, and violation values are finite; floor/ESS rules are logged.
7. Endpoint censoring and signed-grid toy cases are correct.

Neither monotone sharpness nor monotone effective sample size is a sanity gate:
they are empirical outcomes.

## Inference and limits

All curves use base-task clustered bootstrap resampling within field ×
generator cells, followed by equal generator weighting. The primary unit is
the base task, not the 11 repeated perturbation rows.

E12-A estimates fragility of predeclared scalar specifications in this frozen
1D grammar and fixed scope. It does not estimate real-world calibration
frequency, structural-family error, prediction utility, safe admission, or
general prior robustness. E12-B is required before making any statement about
under-specification versus false structural additions.
