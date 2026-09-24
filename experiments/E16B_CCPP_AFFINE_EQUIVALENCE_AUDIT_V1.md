# E16-B CCPP Affine Point-Mixture Equivalence Audit v1

**Status: PASS — frozen before validation, guard, or confirmatory targets are opened.**

Using the 6,699 frozen train targets, all 405 candidate nuisance fits were
replayed with the common ridge \(\lambda_{spec}=10^{-4}\).  Across all 9,568
canonical covariate rows, the uniform candidate point mean and the prediction
of the uniform mean raw specification differed by at most
\(5.773159728050814\times10^{-15}\), below the frozen \(10^{-12}\) tolerance.
Their RMS difference was \(1.3951864863579293\times10^{-15}\).

This is a representation audit, not a predictive-outcome result.  It confirms
that uniform/weighted point means are affine specification summaries.  The
pre-outcome CRPS amendment therefore makes the finite Gaussian mixture—not its
point mean—the primary retained-diversity estimand.

The machine-readable audit is
`results/prior_utilization_e16b/affine_equivalence_v1/E16B_CCPP_AFFINE_EQUIVALENCE_V1.json`.
