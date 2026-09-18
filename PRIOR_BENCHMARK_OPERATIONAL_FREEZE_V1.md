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
- **Latent-assisted operational asymptote label**: in the final 20% versus preceding 20%, median
  absolute slope and median distance to latent limit each fall by >=50%.
  Latent asymptotic mechanism truth is stored separately.

Phenomenological regime Delta-BIC searches normalized change locations
`.15,.16,...,.85`. The single model is quadratic (`k=3`). The two-segment model
uses continuous hinge basis `1,x,x^2,(x-tau)_+,(x-tau)_+^2` (`k=5`): value
continuity is enforced, while slope and curvature may change. Use
`BIC=n*log(max(RSS/n,sigma_floor^2))+k*log(n)`, where
`sigma_floor=1e-6*max(Ry,1e-8)`. Delta-BIC is single minus the minimum
two-segment BIC. Both segments retain at least 15% of points.

## 2. Conditional Sharpness estimator

Primary ensemble `Q_spline` and robustness ensemble `Q_basis` each use
`M=4096` candidate continuations, generated independently of the candidate
prior. Prefix loss `L_m` is the raw-target-scale prefix **MSE** (not SSE and not
target-range-normalized MSE), so sampling density does not mechanically sharpen
the weights. It gives weights
`w_m=exp(-(L_m-min L)/(2T))`, where
`T=noise_sd^2 + (.01 range(y_obs))^2`. Rescale weights to sum to `M`.

For every estimate record
`ESS=(sum_m w_m)^2/sum_m w_m^2`. `ESS<100` is a predeclared measurement-quality
warning, not an exclusion rule; all primary results remain included and are
accompanied by an `ESS>=100` sensitivity analysis.

Use Jeffreys/Laplace smoothing `a=b=.5`:

`p_hat=(sum_m w_m I_m + .5)/(M+1)`.

Set probability floor `p_min=1/(10M)` and
`S=-log(max(p_hat,p_min))`. Primary robustness is Spearman rank correlation
between `Q_spline` and `Q_basis` sharpness; pass criterion `rho>=.80` overall
and `rho>=.70` within each primitive. Record the rate of numerical violations
of `S(A AND B)>=S(A)-1e-8`; sanity pass requires zero.

Phenomenological and mechanistic sharpness are separate. Mechanistic sharpness
requires a paired `(trajectory, latent mechanism)` ensemble.
This v1 definition has `S_max=-log(1/40960)=10.6204`. Its absolute values are
not comparable to exploratory sharpness values around 24–25; the scale restarts
for benchmark v1.

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

For size-2/3 truth, `true-subset` is a seeded nonempty proper subset at weakest
logical specificity. For singleton truth it is the same primitive at its
weakest logical level, never the empty prior. `true-full` contains all intended
true primitives at medium-correct specificity. `biased-specific` is narrow;
its signed bias tier is balanced. Mixed and fully-wrong use medium specificity.
The code key remains `true-subset`; singleton cases are called `true-weaker`
or `under-specific true` in papers and reports.

The sanity suite additionally creates four **measurement-validation-only**
candidates from the same true constraint: broad-correct, medium-correct,
narrow-correct, and narrow-biased. They use the widths and bias grid in Section
6, are never included in the six-action benchmark set, and cannot affect full-v1
candidate balance. They exist only to test nested coverage/sharpness behavior.

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

Full-v1 data conditions use a frozen Latin hypercube with seed `42000` and the
following independent coordinates:

- observed-support fraction: uniform `[.35,.70]`;
- observed sample count: log-uniform `[24,120]`, rounded to the nearest integer;
- noise SD divided by clean observed-target range: log-uniform `[.001,.05]`;
- mechanism exposure: uniform `[0,.90]` within the primitive's valid exposure
  definition;
- OOD distance normalized by training-support width: log-uniform `[.05,1.00]`;
- unit/instance heterogeneity coefficient of variation: uniform `[0,.25]`;
- identifiability/effect-strength fraction of the primitive's declared valid
  range: log-uniform `[.05,1.00]`.

Degenerate clean observed-target ranges below `1e-8` are floored only for
normalization and flagged. Coordinate transforms and rounding are applied
before the task seed is used to instantiate a generator.

Sanity suite: 40 tasks per primitive per generator realization at zero noise,
dense 81-point support, normalized near-OOD distance `.10`; seeds
`41001,41002,41003` for spline, basis, ODE realizations.

Full v1 after sanity pass: 100 tasks per registered composition cell, five
seeds `42001..42005` with 20 tasks/seed. Register 7 singleton, 12 compatible
pairs, 8 compatible triples, and 20% null tasks. Data conditions are sampled by
a frozen Latin-hypercube design rather than a full factorial. Splits are fixed:
parameter OOD, held-out composition, held-out primitive, and held-out generator.

The 27 non-null cells yield 2,700 non-null tasks. Null tasks are 20% of the
final total: `N_null=675`, `N_total=3375`.

The 3,375 tasks form one immutable **benchmark corpus**. Parameter OOD,
held-out composition, held-out primitive, and held-out generator are metadata
views/evaluation protocols over that corpus, not four subdivisions that alter
the anatomy summaries. Their frozen definitions are:

- parameter OOD: seven coordinate-specific views compare that coordinate's
  lowest 10% plus highest 10% against its central 60%, with the intervening
  20% as a guard band. A supplementary joint view trains only where all seven
  coordinates are central and tests tasks where at least one coordinate is in
  a tail; all remaining tasks are guard;
- composition OOD: the final 20% of registered size-2/3 compositions after
  sorting by SHA-256 of the canonical composition string;
- primitive OOD: `inflection` and every composition containing it are held out;
- generator OOD: ODE realizations are held out from spline/basis development.

These partitions are for future proposer/evaluator generalization tests. The
prior-anatomy benchmark reports all corpus tasks with the predeclared strata.

Uncertainty uses 5,000 paired hierarchical bootstrap replicates: resample
registered primitive/composition cells with replacement, then resample tasks
within selected cells, retaining candidate and realization-engine pairing.
Percentile 95% intervals are primary. Headline effects use normalized utility
`u=U/max(RMSE_baseline,1e-8)` and macro-average cells equally; raw-RMSE utility
and task-weighted pooled intervals are supplementary. The practical boundaries
for normalized utility are `-.02` and `+.02`.

Pairwise compatibility does not register triples. Enumerate triples
lexicographically with seed `40017`. A triple is feasible only when spline,
basis, and ODE constructors each produce 20/20 checker-valid trajectories,
allowing at most 1,000 attempts per trajectory. Register the first eight
feasible triples before computing the final protocol hash.

### Null-task generators

Null status is assigned before model fitting and never from observed utility.
Store two non-pooled labels:

- **Structural null:** the registered grammar has no structurally valid,
  informative primitive for the continuation. Generate it with a separate
  out-of-grammar smooth generator: a seeded mixture of 4–6 compact radial-basis
  components plus a chirp term, with no latent regime switch or finite-limit
  mechanism. Accept a draw only when the clean 401-point trajectory:

1. has at least two robust `f'` sign changes and at least two robust `f''` sign
   changes under the Section 1 tolerances;
2. fails the global direction and curvature persistence thresholds;
3. fails the exactly-one inflection and exactly-one turning-point definitions;
4. has phenomenological regime `Delta BIC<10` and no mechanistic regime label;
5. fails the operational asymptote test; and
6. has no registered nontrivial bound constraint supplied by the latent
   specification.

- **Informational null:** at least one weak registered constraint has structural
  coverage 1, but every such coverage-preserving candidate has conditional
  sharpness `<.10` under both frozen continuation ensembles. These are generated
  from ordinary in-grammar tasks with deliberately uninformative prefixes.

The `.10` threshold therefore defines only informational nulls and is never
used to create structural-null truth. This prevents sharpness-based evaluation
from receiving a structurally circular null label. If no accepted draw is found
in 2,000 seeded attempts, record a generator failure; do not relabel the task
or use utility to decide nullness. Neither label claims that every imaginable
scientific prior is absent.

## 9. Sanity pass gates

Correct weak/strong coverage >=.95; wrong coverage <=.05; correct narrow median
sharpness exceeds broad; biased narrow has lower coverage and higher sharpness
than broad; conjunction monotonicity violations zero; cross-generator truth
agreement >=.95; mechanistic/phenomenological labels remain separate; null
abstention and weak-prior actions are distinguishable. Failure blocks full v1.

The broad/narrow checks use only the sanity-only auxiliary candidates defined
in Section 5. Null validation requires >=95% of structural-null draws to satisfy
all six structural conditions, >=95% of informational-null draws to satisfy
coverage plus the two-ensemble `<.10` rule, and zero utility-based relabeling.

Cross-generator agreement uses paired latent structural specifications: the
same sign, event count, normalized location, segment scope, and magnitude tier
are supplied to spline, basis, and ODE constructors. The same 40 specifications
are checked across all three generators. Sanity evaluates benchmark validity,
not predictive performance.
