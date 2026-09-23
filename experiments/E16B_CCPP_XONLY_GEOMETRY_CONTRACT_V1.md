# E16-B CCPP AT-Tail X-Only Geometry Contract v1

## Status

**FROZEN.**  This artifact fixes a single prospective covariate-support split
for E16-B.  It uses no target values, target-derived summaries, model fits,
policy fits, or predictive outcomes.

The canonical source is Sheet1 of the byte-audited UCI CCPP workbook recorded
in `E16B_CCPP_SOURCE_MANIFEST_V1.json`.  The audit code reads only the four
feature columns `AT`, `V`, `AP`, and `RH`; it requests at most four workbook
columns, so the target column is not materialized.

## Frozen AT support split

Quantiles use `numpy.quantile(method="linear")` over canonical Sheet1 `AT`:

| Boundary | AT value (deg C) |
|---|---:|
| \(q_{70}\) | 24.79 |
| \(q_{85}\) | 27.96 |
| \(q_{90}\) | 29.24 |

The split is:

| Partition | Definition | Rows |
|---|---|---:|
| Train | \(AT\le q_{70}\) | 6,699 |
| Validation | \(q_{70}<AT\le q_{85}\) | 1,436 |
| Guard band | \(q_{85}<AT\le q_{90}\) | 477 |
| Confirmatory test | \(AT>q_{90}\) | 956 |

The guard band is excluded from every fit and tuning decision.  Validation is
never merged into training.  The train maximum is 24.79 deg C and the
confirmatory-test minimum is 29.25 deg C, giving a frozen strict support gap
of 4.46 deg C.

Ties at the boundaries are retained and allocated by the displayed inclusive
rules: 5 at \(q_{70}\), 4 at \(q_{85}\), and 5 at \(q_{90}\).  Exact nominal
70/15/5/10 percentages are therefore not imposed.

## Remaining-covariate audit

The primary support coordinate remains AT, but the test population changes
substantially in the other supplied covariates.  All results below are X-only.

| Feature | Test inside train min--max | Test-median shift / train IQR | Wasserstein-1 / train IQR |
|---|---:|---:|---:|
| V | 1.0000 | +1.4888 | 1.2293 |
| AP | 1.0000 | -0.7559 | 0.7657 |
| RH | 0.9948 | -1.4008 | 1.3401 |

For the joint \((V,AP,RH)\) diagnostic, each coordinate is standardized by
the train median and IQR.  The 95th percentile of train leave-one-out nearest
neighbour distance is 0.1191.  The test-to-train median and 95th-percentile
distances are 0.2497 and 0.7117.  Only 21.23% of confirmatory-test rows lie at
or below that train reference distance.

The frozen classification rule is `compound covariate shift` when this
coverage is below 95%; it is 21.23%.  E16-B must therefore describe the
confirmatory setting as:

> **High-AT extrapolation under compound covariate shift.**

This is an interpretation label, not a criterion for revising the quantile
split.

## Permitted next step

The next pre-outcome task is a prior-realization/specification contract:
define the shared set of candidate continuations satisfying conditional AT
non-increase, and define MAP, uniform-ensemble, and evidence-weighted
policies over exactly that common candidate set.  Model family, capacity,
validation tuning, quota, and all target outcomes remain unfrozen.
