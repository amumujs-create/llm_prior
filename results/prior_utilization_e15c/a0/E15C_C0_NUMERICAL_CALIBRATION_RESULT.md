# E15-C0 outcome-free numerical calibration result

## Status

**PASS.** No policy RMSE, CRPS, contrast value, sign, ranking, or winner was calculated, persisted, or used in selection.

The predeclared selection order selected:

\[
\Delta q=0.05,\qquad \rho=0.10,\qquad x_{\rm far}=1.00.
\]

`.05` is the coarsest admissible grid; `.10` is the largest admissible noise ratio; `1.00` is the longest admissible far endpoint.

## Selected-candidate diagnostics

| Exposure | Median \(E_r\) | 5–95% \(E_r\) | Median effective residual continuations | Median uniform-minus-closed distance |
| --- | ---: | ---: | ---: | ---: |
| Low | 0.000090 | [0.00000029, 0.004247] | 19.5 | 0.9447 |
| Medium | 0.002385 | [0.00000915, 0.026112] | 16.0 | 0.3859 |
| High | 0.022289 | [0.001306, 0.151312] | 14.0 | 0.3165 |

All predeclared gates passed:

- `.05` grid: median effective continuation count is at least four for low, medium, and high exposure.
- Evidence medians are ordered `low < medium < high`.
- Adjacent 5–95% evidence intervals overlap.
- Evidence does not universally reach the 0 or 1 endpoint.
- The uniform residual ensemble is not prediction-equivalent to the closed-mechanism condition; its median separation exceeds `delta_cont=.01` at every exposure.
- All deterministic profiles and candidate continuations are finite.

## Interpretation boundary

This calibration establishes a known invariant with a partially identifiable residual-shape axis. It does not estimate policy utility. The very low low-exposure `E_r` is the intended weak-identification condition; the retained continuation counts confirm that residual futures remain nondegenerate rather than collapsing into the closed mechanism.

## Frozen inputs and artifacts

- Sweep artifact: `E15C_C0_OUTCOME_FREE_SWEEP.json`
- Sweep SHA-256: `c411c93b003507928583eb07836f42d2851c1ac943c4a240bcd5cb6e95690a71`
- Candidate-contract SHA-256: `87fc1e2d044c96fdc93daee68be56774573e882fd3cea998feaa7274c687f56d`
- Selection-rule SHA-256: `bddb0e3efd8a03d24282228c7b3b4c3ed7a3f608f4dc1bc65c605ef176dca73e`
