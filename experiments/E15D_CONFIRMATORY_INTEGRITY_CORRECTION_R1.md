# E15-D v1.2 confirmatory integrity correction R1

## Incident and disposition

Before the initial confirmatory corpus was committed or integrity-frozen, a
mechanical `git diff --check` invocation expanded CRLF diagnostics for the
uncommitted CSV and exposed individual row-level clean-NRMSE values. No
predeclared contrast, aggregate statistic, bootstrap interval, sign, rank, or
winner was computed, reported, or used.

Nevertheless, the initial namespace `e15d-confirmatory-v1.2` is retired. Its
uncommitted files are excluded permanently from all analysis and are not a
confirmatory artifact.

## R1 replacement corpus

R1 changes **only** the confirmatory namespace to
`e15d-confirmatory-v1.2-integrity-r1`. It creates exactly 153 new latent task
IDs 0–152 using the already frozen deterministic seed procedure. It reuses no
old latent task, seed, row, or outcome.

The following are unchanged: selected D0 geometry; clean target; common far
window; candidate grid; policies; estimands; success criterion; protected
quota; bootstrap procedure; and outcome opening order.

## Implementation correction

The R1 writer uses LF (`\n`) line terminators. This prevents a future
whitespace diagnostic from expanding raw CSV lines. Integrity checks use row
counts, keys, hashes, and boolean audits only; no CSV diff check is run before
the corpus is committed.
