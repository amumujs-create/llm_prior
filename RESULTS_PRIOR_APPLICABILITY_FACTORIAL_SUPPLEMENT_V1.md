# E8 Supplement — A2 Absolute-Horizon / C2 Bias-Symmetry Results

## Integrity

The frozen A2/C2 protocol generated 5,040 latent tasks and 15,120
engine-conditioned records with zero solver failures. The raw-record SHA-256 is
`ab446bc29d83a56aa8f33a244cbb458175952df07f662210fc4ffa6a1183fcfb`.
All primary rates use 5,000 within-stratum bootstrap replicates and the robust
target remains harmful in either realization engine.

## A2 — fixed absolute forecast gap

Holding the physical forecast gap at `.21` does **not** remove the support
association. Robust-unsafe rates are `.73/.69/.58` at support `.35`,
`.74/.71/.70` at `.525`, and `.77/.72/.69` at `.70` for noise
`.001/.01/.05`, respectively. Thus the original E8-A pattern was not solely an
artifact of absolute-horizon growth under normalized distance.

This is still not a universal "more support is unsafe" law: increasing support
also reveals a later prefix of a nonstationary generator. The valid conclusion
is narrower: observed-support amount is not a sufficient scalar safety
statistic, even after holding the absolute future gap fixed in this scope.

## C2 — signed bias

Bias direction materially changes risk. Robust-unsafe rates for negative versus
positive narrow bias are `.774/.788/.771` versus `.729/.705/.681` at OOD
distances `.10/.40/.80`. The bootstrap intervals for negative bias are
non-overlapping with positive bias at `.10` and `.40`; see the summary table.

Therefore E8's biased-specific result cannot be reduced to "narrow specificity
is bad" or to a single unsigned calibration-error magnitude. Within this
parameterization, **calibration direction is an additional prior-quality
axis**. Positive bias remains unsafe, but negative bias is worse in the tested
conditions.

## Consequence

E8 is now closed as a context/engine study: future work should represent
context, realization engine, and *signed or otherwise structured calibration
error*, rather than use one global specificity or data-volume threshold.
The next independent question is E9: when a true structural prior begins to
provide meaningful conditional continuation information, before utility or an
engine is involved.

## Artifacts

- [Frozen supplement protocol](PRIOR_APPLICABILITY_FACTORIAL_SUPPLEMENT_PROTOCOL_V1.md)
- `experiments/run_prior_applicability_factorial_supplement_v1.py`
- `experiments/analyze_prior_applicability_factorial_supplement_v1.py`
- `results/prior_applicability_factorial_supplement_v1/analysis/summary_bootstrap.csv`
- `figures/fig32_e8_supplement_a2_c2.png`
