# Prior Primitive–Composition Benchmark v1 — Operational Freeze

**Status:** frozen before sanity-suite outcomes. Threshold changes after this
point require a new protocol version. Implementation bug fixes must be logged.

## 1. Clean-trajectory truth checker

All phenomenological labels use the clean trajectory on 401 equally spaced
target-domain points. Derivatives use Savitzky–Golay order 3, window 21; ten
edge points are excluded. Let `Rx` and `Ry` be target-domain ranges.

- `eps1 = .01 Ry/Rx`; `eps2 = .02 Ry/Rx^2`.
- Direction: required derivative sign on >=95% of valid points and median
  magnitude beyond `eps1`.
- Curvature: required second-derivative sign on >=90% of valid points and
  median magnitude beyond `eps2`.
- Inflection: exactly one robust `f''` sign change; both sign segments span
  >=10% of target points, persist >=8% of the domain, and exceed `eps2`.
- Turning point: exactly one robust `f'` sign change with the same span and
  persistence rules using `eps1`.
- Mechanistic regime: latent generator switch plus change in local derivative
  or curvature >=20% of its pre-switch robust scale; both regimes span >=15%.
  Phenomenological regime is stored separately using two-segment versus single
  local-quadratic `Delta BIC >=10`, with segments >=15%.
- Bound: all clean values satisfy the supplied one-sided bound within
  `.01 Ry` tolerance.
- Asymptote operational label: in the final 20% versus preceding 20%, median
  absolute slope and median distance to latent limit each fall by >=50%.
  Latent asymptotic mechanism truth is stored separately.

## 2. Conditional Sharpness estimator

Primary ensemble `Q_spline` and robustness ensemble `Q_basis` each use
`M=4096` candidate continuations, generated independently of the candidate
prior. Prefix losses `L_m` give weights
`w_m=exp(-(L_m-min L)/(2T))`, where
`T=noise_sd^2 + (.01 range(y_obs))^2`. Rescale weights to sum to `M`.

Use Jeffreys/Laplace smoothing `a=b=.5`:

`p_hat=(sum_m w_m I_m + .5)/(M+1)`.

Set probability floor `p_min=1/(10M)` and
`S=-log(max(p_hat,p_min))`. Primary robustness is Spearman rank correlation
between `Q_spline` and `Q_basis` sharpness; pass criterion `rho>=.80` overall
and `rho>=.70` within each primitive. Record the rate of numerical violations
of `S(A AND B)>=S(A)-1e-8`; sanity pass requires zero.

Phenomenological and mechanistic sharpness are separate. Mechanistic sharpness
requires a paired `(trajectory, latent mechanism)` ensemble.

## 3. Practical utility

Raw `U=RMSE_baseline-RMSE_prior` is always retained. Per task,
`delta=.02*RMSE_baseline`: beneficial if `U>delta`, neutral if
`|U|<=delta`, harmful if `U<-delta`. Baseline RMSE below `1e-8` is floored at
`1e-8` only for threshold construction.

## 4. Primitive compatibility matrix

Codes: `C` compatible globally, `K` conditional on segment-local semantics,
`I` incompatible when both claims are global. Diagonal is `C`.

| | Dir | Curv | Infl | Turn | Regime | Bound | Asym |
|---|---|---|---|---|---|---|---|
| Direction | C | C | C | K | K | C | C |
| Curvature | C | C | K | K | K | C | C |
| Inflection | C | K | C | C | K | C | C |
| Turning | K | K | C | C | K | C | C |
| Regime | K | K | K | K | C | C | C |
| Bound | C | C | C | C | C | C | C |
| Asymptote | C | C | C | C | C | C | C |

`K` compositions must name segments explicitly; otherwise they are rejected.
All v1 priors are AND conjunctions.

## 5. Candidate balance

Every non-null task has exactly six actions: abstain plus one each of
`true-subset`, `true-full`, `biased-specific`, `mixed true+false`, and
`fully-wrong`. Null tasks use abstain plus five matched-strength non-informative
or wrong candidates. Candidate order is randomized by task seed.

## 6. Knowledge perturbations

All widths and biases use normalized valid parameter range. Broad/medium/narrow
half-widths are `.30/.15/.05`. Bias centers use signed normalized errors
`0,.05,.10,.20,.30`; signs are balanced. Location, rate, curvature magnitude,
bound, and asymptote fields use their own declared valid ranges before
normalization. Provenance and confidence fields are placeholders in v1 and do
not enter realization.

## 7. Realization-engine fairness

Constrained spline and 8-unit constrained neural-basis engines receive the same
train data, candidate, split, maximum 2,000 optimizer evaluations, and three
fixed initializations. Record parameter count, wall time, convergence, and
solver failure. A headline utility direction is `concordant` only if both
engine mean effects have the same sign and neither 95% CI crosses the opposite
practical-effect boundary.

## 8. Aggregation and sample plan

Headline aggregation is macro-average across primitive/composition cells;
task-weighted pooled results are supplementary. Always report primitive,
composition size, generator, distance, noise, and knowledge-quality strata.

Sanity suite: 40 tasks per primitive per generator realization at zero noise,
dense 81-point support, normalized near-OOD distance `.10`; seeds
`41001,41002,41003` for spline, basis, ODE realizations.

Full v1 after sanity pass: 100 tasks per registered composition cell, five
seeds `42001..42005` with 20 tasks/seed. Register 7 singleton, 12 compatible
pairs, 8 compatible triples, and 20% null tasks. Data conditions are sampled by
a frozen Latin-hypercube design rather than a full factorial. Splits are fixed:
parameter OOD, held-out composition, held-out primitive, and held-out generator.

## 9. Sanity pass gates

Correct weak/strong coverage >=.95; wrong coverage <=.05; correct narrow median
sharpness exceeds broad; biased narrow has lower coverage and higher sharpness
than broad; conjunction monotonicity violations zero; cross-generator truth
agreement >=.95; mechanistic/phenomenological labels remain separate; null
abstention and weak-prior actions are distinguishable. Failure blocks full v1.
