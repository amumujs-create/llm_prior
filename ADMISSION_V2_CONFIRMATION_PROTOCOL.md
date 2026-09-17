# Frozen admission-v2 confirmation protocol

## Objective

Test whether the fully frozen v2 admission rule reproduces on a disjoint
synthetic data draw. This is not a performance-improvement or feature-search
experiment.

## Integrity lock

The source, protocol, development result, and config hashes are recorded in
`FROZEN_ADMISSION_V2_MANIFEST.json`. Before generating confirmation tasks, the
runner verifies the frozen v2 source hash. No feature, scaler, classifier,
threshold, family generator, utility definition, or endpoint may change.

## Data independence

Development uses `SeedSequence([20260920, family, level, noise, task])`.
Confirmation uses `SeedSequence([20260921, family, level, noise, task])` with
the identical 3 × 6 × 5 × 50 grid. Therefore parameter draws and noise
realizations are disjoint by construction.

## Frozen learning and evaluation procedure

1. Regenerate only the development draw to fit the exact frozen v2 logistic
   pipeline; export the resulting pipeline as an immutable artifact.
2. Generate the new confirmation draw and apply that pipeline unchanged at its
   frozen probability threshold `.50`.
3. Primary endpoint: `Delta FAR = FAR_v2 - FAR_v1`, where
   `FAR = P(admit | U<0)`. Use a paired 10,000-resample bootstrap over harmful
   confirmation tasks; confirmation passes the primary endpoint only when the
   95% CI for Delta FAR is strictly below zero.
4. Secondary endpoints: useful-prior admission, harm risk among admitted,
   coverage, family-specific results, and the observability–utility association.
5. The coverage–risk curve is supplementary descriptive analysis; no threshold
   is selected from it.

## Evidence status

The test is confirmation for the frozen synthetic rule on an independent draw.
It does not confirm real-data performance, retrieval/RAG, or general physics.
