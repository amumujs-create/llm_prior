# E15-D0 v1.1 execution addendum

## Purpose

This addendum freezes the discarded D0 calibration sample and deterministic
seed mechanism. It supplements `E15D_V1_1_FACTORISED_D2_AND_D0_CONTRACT.md`
and has no authority to alter any semantic, numerical-selection, or
prospective-hypothesis contract.

## Discarded calibration sample

- D0 latent-task quota: **400**.
- D0 uses exactly task IDs `0` through `399` for every numerical candidate.
- The quota is fixed, not adaptive. It supports direct estimation of medians
  and 5–95% evidence-distribution geometry while retaining 20 observations in
  each nominal 5% tail.
- All D0 tasks and every D0 seed are discarded. They must never be reused by a
  confirmatory run, protected quota pilot, or outcome analysis.

## Deterministic seed namespace

The immutable namespace is

`e15d-d0-v1.1-discarded`.

For task ID \(r\), derive the task seed as the first eight bytes of

\[
SHA256(\texttt{"e15d-d0-v1.1-discarded:task:"} \Vert \texttt{r})
\]

interpreted as an unsigned big-endian integer and reduced modulo \(2^{63}\).

One seeded generator supplies the task's standardized latent uniforms and one
master standardized noise path. Candidate supports transform the same latent
uniforms into their proposed coefficient intervals, and all L/S/J prefixes
are nested views of that same master noise path. Candidate evaluation order
must therefore not change any task realization.

## No replacement rule

The polynomial generator is finite on the public domain and D0 does not use an
acceptance-conditioned corpus. If a task or numerical candidate fails a frozen
finite/stability gate, the affected numerical candidate fails D0. The runner
must not replace, resample, skip, or selectively filter task IDs.

## Allowed D0 output

Only aggregated, outcome-free records may persist:

- selected-candidate identifiers;
- per-regime \(E_\kappa,E_\lambda\) medians and 5–95% quantiles;
- joint-continuation distinctness summaries;
- finite and numerical-stability status;
- pass/fail reasons under the frozen selection order;
- source code, contract, and artifact hashes.

The runner must never create policy predictions or persist RMSE, CRPS, D1,
D2, \(D_{\rm dep}\), D3, contrast values, means, signs, rankings, winners,
or any other outcome proxy.
