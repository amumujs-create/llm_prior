# Frozen protocol — Prior Evaluation Metric Experiment v1

**Status:** frozen before execution  
**Experiment ID:** `prior_evaluation_metric_v1`  
**Purpose:** Test whether pseudo-OOD pointwise error alone is an adequate
selection metric for structural-prior candidates, and compare it against
trajectory/derivative/complexity metrics without forming a post-hoc composite.

## Fixed synthetic contract

- Generator families: `regime_change`, `emergent_curvature`,
  `asymptotic_bound`.
- Observed support: `t <= 0.60`.
- Selection split: inner fit `t <= 0.45`; pseudo-OOD validation
  `0.45 < t <= 0.60`.
- After selection, the selected candidate is re-fit on all `t <= 0.60` data.
- Clean far-OOD evaluation bands: `D1=[0.70,0.80]`, `D2=[0.90,1.00]`, and
  `D3=[1.20,1.30]`.
- Grid: spacing `.01` over `[0,1.30]`; noise applies only to the observed
  prefix.  Every far-OOD target remains evaluation-only.
- Factorial design: 3 families × 3 within-family observability settings ×
  3 noise SDs (`.005,.015,.030`) × 100 independent draws = 2,700 trajectories.

## Candidate set and structural compatibility

All candidates are evaluated for every generator. A candidate is not called
“correct” merely because it has the generator's name.

| ID | Candidate implementation | Compatibility rule |
|---|---|---|
| `P0` | local affine continuation | neutral baseline; excluded from incompatible-prior numerator |
| `PD` | decreasing direction-constrained affine continuation | compatible for all three generators |
| `PC` | decreasing concave-quadratic continuation | compatible for regime change and emergent curvature only |
| `PB` | decreasing asymptotic-exponential continuation | compatible for asymptotic bound only |
| `PT` | decreasing piecewise regime-transition continuation | compatible for regime change only |

“Compatible” here means that the candidate's structural claim is satisfied by
the clean generator; it does **not** assert parameter identifiability or utility.

## Selection metrics (evaluated independently on pseudo-OOD)

All candidates are fit only on the inner-fit data for selection.

1. `mse`: negative pseudo-OOD MSE.
2. `delta_cosine`: cosine similarity of first differences.
3. `delta2_cosine`: cosine similarity of second differences.
4. `derivative_sign`: agreement rate of first-difference signs.
5. `spearman`: Spearman rank correlation of pseudo-OOD values.
6. `bic`: negative predictive BIC, `n log(MSE+eps) + p log(n)`, where `p` is
   the candidate realization parameter count.

Ties are resolved by the fixed candidate order `P0, PD, PC, PB, PT`.
No metric is combined with another and no metric/threshold will be changed after
results are inspected.

## Primary endpoints

For metric `m`, selected candidate `k*_m`, and distance band `d`:

`R_m(d) = RMSE(k*_m,d) - min_k RMSE(k,d)`.

Report mean regret with a 95% bootstrap CI, plus:

- incompatible-selection rate, `P(C[k*_m]=0)`, excluding neutral `P0`;
- pseudo-vs-far winner disagreement rate;
- family-stratified and pooled results.

## Interpretation guardrails

- The experiment tests selection under this candidate library and these
generators; it does not prove a universal derivative metric.
- `O` (structural exposure within the prefix) is distinct from `d` (far-OOD
query distance). This protocol varies both and does not treat one as a proxy
for the other.
- The primary conclusion will compare metrics by regret and harm/compatibility,
not by pseudo-OOD validation score itself.

## Prespecified connection to the next experiments

E2 will use the best **non-pointwise** metric only if its pooled distant-band
regret is lower than MSE and its incompatible-selection rate is not higher. If
that condition fails, E2 remains an MSE-capacity stress test and the negative
result is retained. E3 studies specificity independently. E4 adds a random
monotone archetype only after the candidate-metric finding is recorded.
