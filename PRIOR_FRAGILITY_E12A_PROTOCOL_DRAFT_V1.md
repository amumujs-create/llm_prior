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
| lower-bound relation (source atom: `lower_bound_0`) | bound level `L` | task-level clean target range `R_ref` | one-sided margins `.005/.035/.075 R_ref` |
| asymptote-from-above relation (source atom: `asymptote_to_0_from_above`) | asymptotic limit `theta_lim` | task-level clean target range `R_ref` | `.025 R_ref` |

`lower_bound_0` and `asymptote_to_0_from_above` are frozen **source atom IDs**
from the canonical grammar, not literal claims that every perturbed numerical
specification remains at zero. E12-A keeps the structural content as a
lower-bound or asymptote-from-above relation while moving its numeric level.
Location ranges are the width of `Omega`; level ranges use the fixed task-level
reference range. Direction and unsigned curvature are intentionally absent:
within the v1 canonical grammar they have no separately declared scalar
realization field. Their content fragility belongs in E12-B, not in a
made-up numeric sweep.

### Baseline validity margin is an explicit controlled variable

A centered interval would make the validity-break endpoint a design constant:
with `c_0=theta*` and `w=.025 R_theta`, every two-sided field would first fail
at the same grid location. E12-A therefore does **not** center every valid
baseline specification on the true value.

For every location/limit field, define a valid baseline interval center `c_0`
such that `r_0=(theta*-c_0)/w` is one of the predeclared values
`{-0.8, 0, +0.8}`. The supplied baseline is
`P_0: |theta-c_0|<=w`, and a signed perturbation moves only its center:

`P_epsilon: |theta-(c_0+s epsilon R_theta)|<=w`, where `s in {-1,+1}`.

The resulting initial margin is
`m_0=w-|theta*-c_0|=w(1-|r_0|)`. Thus the break endpoint measures
**tolerance conditional on a declared, valid initial margin**, not an intrinsic
property of a primitive. At `epsilon=0`, every supplied specification remains
valid by construction. Zero is written once per margin state; nonzero
magnitudes are evaluated in both signs.

The predeclared grid is `epsilon in {0,.025,.05,.10,.20,.30}`. It is a
normalized displacement grid, not a claim that these values represent equal
physical error across primitives.

## Corpus and repeated measures

Generate `5 fields × 3 generator families × 30 latent trajectories = 450`
latent trajectories. For each trajectory, evaluate all three frozen baseline
margin states and then the same master observation realization and 4,096-member
full-domain ambient continuation bank at eleven misspecifications (`0`, plus
both signs at the other five magnitudes). The planned output is **14,850
repeated trajectory-margin-perturbation rows**.

Task generation, noisy prefix creation, and ambient bank sampling use separate
fixed seed streams. The prior perturbation and baseline-margin state are
deterministic transforms of the already accepted trajectory; neither can alter
the latent trajectory, observations, likelihood weights, or bank.

## Measurements

### Oracle-only validity stage

The clean latent trajectory and true scalar field are accessible only here.

- For two-sided location/limit fields,
  `Coverage_epsilon = I(|theta*-(c_0+s epsilon R_theta)|<=w)` and
  `D_violation_epsilon=max(|theta*-(c_0+s epsilon R_theta)|-w,0)/R_theta`.
- **Lower bound is a different one-sided statement**, not a unique true
  parameter. Its baseline declared value is `L_0=min_Omega f* - m_0`, with
  `m_0/R_ref in {.005,.035,.075}`; its perturbation is
  `L_epsilon=L_0+s epsilon R_ref`. Bound coverage is exclusively
  `I[f*(x)>=L_epsilon for all x in Omega]`, and its violation severity is
  `max_x(L_epsilon-f*(x))_+/R_ref`. A negative bound shift can remain valid by
  becoming weaker; no parameter-interval equivalence is asserted or tested.

Event fields use normalized event-location violation. The asymptote field uses
the declared latent-assisted limit, and is reported separately from any
phenomenological trajectory check.

### Data-conditioned information stage

The scorer receives only the observed prefix, frozen bank, and declared
`P_epsilon`. It does not receive the clean future, `theta*`, coverage,
violation, prediction, utility, or an engine output.

With the fixed E9/E11 weighting convention, record:

- `S(P_epsilon | D)` and effective sample size `ESS`;
- `Delta S_spec(epsilon)=S(P_epsilon|D)-S(P_0|D)`;
- probability-floor flags and saturation counts.

Primary sharpness interpretation requires `ESS >= 100`. Since the prefix,
bank, and likelihood weights are fixed within a latent trajectory, **ESS must
be identical across every margin, sign, and epsilon row for that trajectory**;
any deviation is an integrity failure, not an empirical curve. Floor results are
reported as censored/lower-bound quantities, never converted to exact gaps.

## Endpoints and classifications

For each trajectory × baseline-margin state × sign, the **grid-resolved
validity-break threshold** is the first tested nonzero `epsilon` with
`Coverage_epsilon=0`. If no failure occurs through `.30`, it is right-censored
as `> .30`; it is not called infinitely robust. The two signs remain separate
primary endpoints:
`epsilon_break,+*` and `epsilon_break,-*`.

For two-sided fields, this endpoint is expected to reflect the predeclared
margin geometry. It is therefore reported as a controlled tolerance check,
not as a primitive ranking. The scientifically open part of E12-A is what
happens to conditional sharpness and violation severity **at and beyond that
known validity boundary**, including sign asymmetry and confidently-wrong
states. The one-sided bound has inherently asymmetric validity geometry.

The **signed confidently-wrong onset** `epsilon_CW,s*` is the first tested
`epsilon` satisfying `Coverage_epsilon=0`, `ESS>=100`, and
`S(P_epsilon|D)>=.10 nat`. If validity breaks but no such row occurs through
`.30`, the endpoint is right-censored as `> .30`; if validity never breaks,
the endpoint is not-at-risk / not applicable. Comparing `epsilon_CW,s*` with
`epsilon_break,s*` distinguishes immediate sharp-but-wrong failure from an
initially invalid-but-weak period.

Report by field and sign:

- coverage and violation-severity curves over `epsilon`;
- sharpness curves over `epsilon` and a separate ESS-invariance audit;
- attainment curves for both `Pr(epsilon_break* <= epsilon)` and
  `Pr(epsilon_CW* <= epsilon)` within their applicable risk sets;
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
   across all margin states and perturbations of a base trajectory.
3. Observed prefix and target `Omega` are invariant over `epsilon`.
4. Oracle coverage/violation code is unavailable to the sharpness scorer.
5. `ESS` is identical across all margin/sign/epsilon rows of one trajectory.
6. Location/event truths are generated in the safe interior `[.54,.66]`; at
   maximum displacement plus interval half-width they cannot cross the
   `Omega=[.40,.80]` boundary. No clipping is allowed.
7. Bound coverage is tested only by its function-level inequality.
8. All `S`, `ESS`, and violation values are finite; floor/ESS rules are logged.
9. Endpoint censoring and signed-grid toy cases are correct.

Sharpness need not be monotone and is an empirical outcome. ESS equality is an
integrity gate because weights are fixed before any prior-satisfaction mask is
applied.

## Inference and limits

All curves use latent-trajectory clustered bootstrap resampling within field ×
generator cells, followed by equal generator weighting. The primary unit is
the latent trajectory, not the three margin states or 11 repeated perturbation
rows.

E12-A estimates fragility of predeclared scalar specifications in this frozen
1D grammar and fixed scope. It does not estimate real-world calibration
frequency, structural-family error, prediction utility, safe admission, or
general prior robustness. E12-B is required before making any statement about
under-specification versus false structural additions.
