# E16-B CCPP Final Conclusion v1

## Frozen external result

The preregistered primary contrast was
\(B_1^{CRPS}=CRPS_U-CRPS_M\), predicting a negative value if uniform retention
of all admissible futures improved on validation-selected MAP. Its observed
mean was \(+0.13700838552617803\), with a paired empirical-row bootstrap 95%
interval \([+0.13144014099661291,+0.14232832977382953]\). The interval lies
entirely above zero, so the prospective prediction is a **Prospective failure**.

Thus, under the frozen CCPP reference measure, strict high-AT extrapolation,
and compound covariate shift, uniformly preserving all 405 admissible
predictive components was worse by CRPS than committing to the
validation-selected MAP component.

## Evidence-calibrated allocation

The predeclared secondary contrast was
\(B_2^{CRPS}=CRPS_W-CRPS_U=-0.13555836354572112\), with 95% interval
\([-0.1406314151871323,-0.1302895945934926]\). Validation-informed weighting
therefore recovered nearly all of the uniform-mixture deficit. The frozen
validation evidence had ESS 8.113369930425485 of 405 candidates: it neither
retained the uniform reference measure nor collapsed completely to one
component.

Descriptively, \(CRPS_W-CRPS_M=B_1+B_2\approx+0.00145002198045691\). No
bootstrap interval was preregistered or computed for this derived comparison,
so it is not an equivalence claim.

## Updated interpretation boundary

This external result falsifies the unqualified statement that uniformly
preserving unresolved admissible futures is generally superior to point
commitment. It supports the narrower interpretation:

> Do not collapse uncertainty blindly, but do not preserve all admissible
> hypotheses uniformly either. Use evidence to concentrate probability mass
> toward plausible futures while retaining residual uncertainty where
> justified.

The conclusion is limited to the frozen CCPP candidate reference measure,
Gaussian working likelihood, validation/test split, and high-AT compound shift.
It does not establish universal superiority of evidence weighting, nor does it
retroactively revise any E15 synthetic result.
