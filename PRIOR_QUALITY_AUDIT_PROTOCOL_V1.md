# Prior Quality Audit v1

This is an analysis layer over E5, not a new predictor-selection experiment.
For each task, form a candidate continuation ensemble by drawing parameters from
the family parameter box and importance-weighting them by prefix likelihood.
This defines a reference continuation distribution conditional on observed data.

Coverage is whether the true realization parameter lies inside a supplied
constraint. Sharpness is `-log(weighted survival probability)` of the
constraint under the prefix-conditioned ensemble. Incremental information is
sharpness relative to family-only (zero by construction here). Conditions are
family-only, broad-correct, narrow-correct, narrow-mild-bias, and
narrow-strong-bias. No composite quality score is formed.
