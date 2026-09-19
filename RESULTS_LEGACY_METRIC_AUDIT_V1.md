# Legacy Experiment Common Metric Audit v1

## Purpose

This audit harmonizes stored synthetic experiments under one performance and
safety vocabulary without rerunning their generators. It adds normalized
utility, paired bootstrap CIs for both normalized utility and raw `DeltaRMSE`,
beneficial/neutral/harmful rates, and catastrophic-harm rates whenever stored
paired RMSEs permit direct recovery.

## Coverage

- E1/E2 prior-evaluation metric selection regret
- E5 Calibration × Specificity
- E5b Calibration Tolerance
- Partial Realization Knowledge Sweep
- Exposure / Identifiability Extension (oracle methods and paired gap closure)
- E6 Distance × Residual Trust

The audit uses 5,000 paired bootstrap replicates within each stored comparison
stratum. The practical threshold is the frozen ±2% normalized-utility rule:
beneficial `u > .02`, neutral `|u| <= .02`, harmful `u < -.02`. Catastrophic
harm is `RMSE_prior >= 2 × RMSE_baseline`.

## Important availability boundary

R² and DeltaR² are **not reconstructed** for these legacy artifacts because
their saved JSON records omit target trajectories/predictions and hence SST.
They are recorded as unavailable rather than inferred. R² remains supplementary
for future real-data experiments, with an explicit low-SST flag.

Likewise, Conditional Sharpness cannot be honestly recomputed for E3–E5b from
RMSE-only records. E5b's broad/narrow logical coverage is recoverable from
condition semantics, but its conditional continuation-ensemble sharpness is
not. Existing `prior_quality_audit_v1` remains the coverage/sharpness source
where those quantities were explicitly saved.

## Artifacts

- `experiments/audit_legacy_metrics_v1.py`
- `results/legacy_metric_audit_v1/summary.csv`
- `results/legacy_metric_audit_v1/oracle_gap_closure.csv`
- `results/legacy_metric_audit_v1/selection_regret.csv`
- `results/legacy_metric_audit_v1/coverage_sharpness_availability.csv`
- `results/legacy_metric_audit_v1/manifest.json`
