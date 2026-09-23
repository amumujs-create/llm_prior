# E15-C0 protected quota result

## Protection status

The discarded-pilot runner streamed per-task C1/C2 paired NRMSE contrasts into variance accumulators only. No raw contrast, contrast mean, sign, policy score, ranking, winner, CRPS, or hypothesis test was persisted or inspected.

## Variance-only result

With the inherited `epsilon=.025` paired-NRMSE half-width target and minimum quota 125, the protected maximum across the six C1/C2-by-exposure cells is:

\[
n_{\rm required}=184{,}957.
\]

The corresponding outcome-free Wilson/binomial attempt calculation is `187,215` proposals. Pilot numerical acceptance was 240/240.

## Status: do not freeze confirmatory quota yet

This result is a valid protected variance calculation, but it is not yet adopted as the E15-C confirmatory quota. The low-exposure C1 variance drives the result. An outcome-free geometry diagnostic already stored in the C0 sweep shows that the smallest low-prefix residual-profile basis norm is approximately \(2.4\times10^{-6}\). Thus some low-prefix residual-shape hypotheses weakly constrain profiled amplitude, which can yield very dispersed future continuations.

This is not evidence about a policy winner or direction. It is a feasibility consequence of the frozen weak-identification geometry. The experiment must either accept the resulting quota or explicitly open a versioned C0/estimator revision; it must not silently relax precision, change grid/noise/exposure, or alter profile regularization after seeing this protected result.

## Artifacts

- Protected quota artifact: `E15C_C0_PROTECTED_QUOTA.json`
- SHA-256: `39b79df05252f7726e5f8759b8507dec3eef47da014b64d4a314eb592c2aebce`
- C0 sweep artifact: `E15C_C0_OUTCOME_FREE_SWEEP.json`
- C0 sweep SHA-256: `c411c93b003507928583eb07836f42d2851c1ac943c4a240bcd5cb6e95690a71`
