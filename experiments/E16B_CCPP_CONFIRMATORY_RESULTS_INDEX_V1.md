# E16-B CCPP Confirmatory Results Index v1

**Corpus:** 956 frozen confirmatory rows, `AT > 29.24`, evaluated as
high-AT extrapolation under compound covariate shift. All intervals are
5,000-replicate paired empirical-row bootstrap 95% intervals; they do not
claim population-wide uncertainty over all combined-cycle plants.

| Endpoint | Mean | 95% CI | Role |
|---|---:|---:|---|
| \(B_1^{CRPS}=CRPS_U-CRPS_M\) | +0.1370 | [+0.1314, +0.1423] | Primary; **Prospective failure** |
| \(B_2^{CRPS}=CRPS_W-CRPS_U\) | -0.1356 | [-0.1406, -0.1303] | Secondary, non-directional |
| \(B_1^{NRMSE}=NRMSE_U-NRMSE_M\) | +0.2441 | [+0.2344, +0.2534] | Secondary point diagnostic |
| \(B_2^{NRMSE}=NRMSE_W-NRMSE_U\) | -0.2413 | [-0.2503, -0.2320] | Secondary point diagnostic |

The pre-registered primary prediction was negative \(B_1^{CRPS}\). It was
not supported: the interval lies entirely above zero. Thus, for this frozen
CCPP reference measure and strict high-AT compound-shift split, the uniform
405-component predictive mixture was worse by CRPS than validation-selected
MAP. This is an external prospective falsification, not grounds to revise the
candidate grid, reference measure, likelihood scale, or weighting temperature.

The secondary B2 result favors validation weighting over the uniform mixture,
but it has no predeclared success/failure criterion. The NRMSE rows are point
specification diagnostics only; because of the audited affine equivalence,
they do not establish retention of predictive diversity.
