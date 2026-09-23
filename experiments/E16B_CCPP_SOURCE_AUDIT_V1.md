# E16-B CCPP Official Source Audit v1

## Disposition: PASS

The official UCI DOI release (`10.24432/C5002N`) passed byte-level and
workbook-structure audit.  It is the frozen E16-B primary source under the
CC BY 4.0 license stated by UCI.  The canonical corpus is **Sheet1 only** from
the audited `Folds5x2_pp.xlsx` workbook.

The ZIP and raw workbook are retained in pinned local source staging for later
numerical-design use.  The source artifact records their cryptographic
identities.  No data rows are committed in this audit; no support cutoff,
split, target transformation, model, policy, or outcome has been computed.

## Byte identities

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| Official UCI ZIP | `cc7b2a4977c0a44e8221c91d9a7e5746b3c68186cff7e5c61c70af6432b98c7a` | 3,674,852 |
| `Folds5x2_pp.xlsx` | `ccd490981db2a2f079963b3d9f0aea30d9d338900a0285428dfc6385396f4651` | recorded in source manifest |
| `Folds5x2_pp.ods` | `5a9b34c94892cb7040ed5dd10209f3a5855c103e7b52ba515842a03ed9971891` | recorded in source manifest |
| `Readme.txt` | `2d79c1fb5a91fa1fcbeb514546d9d3fc354be8e4bf8f4df316445e1e7089c137` | recorded in source manifest |

## Workbook audit

- Five sheets, each with 9,568 rows and five columns:
  `AT`, `V`, `AP`, `RH`, `PE`.
- Every sheet has zero missing and zero non-finite cells.
- The sheets have distinct ordered-row hashes but the same canonical row
  multiset SHA-256:
  `7cdbca849f1730fedb2ee9c7704a5f8c62dfe31174caadc57e1f4839a4963e55`.
  They are therefore permutations, not five independent datasets.
- The canonical Sheet1 contains 41 exact duplicate-row groups and 41 excess
  rows.  They are recorded but not removed.

This verifies the UCI documentation's statement that five shuffles were
provided for 5x2 cross-validation comparability.  Concatenating sheets is
prohibited because it would replicate the same observations five times.

## Domain-prior disposition

The primary packet is frozen as conditional AT non-increase:

\[
\frac{\partial PE}{\partial AT}\le0,
\]

inside the full-load operating envelope and conditional on the remaining
supplied covariates.  It is a qualitative structural statement only; slope,
curvature, interactions, and scope cutoffs remain unresolved.

Ambient temperature is the frozen primary support coordinate and the
high-temperature tail is the frozen extrapolation direction.  `AP` is withheld
despite external directional support; `RH` is excluded as configuration
dependent; and `V` is excluded because the sign convention of the UCI vacuum
scale has not been independently operationalized.  This restricts the first
external tabular packet to one strongly motivated statement.

## Remaining authorized work

The next phase is an **X-only** numerical-design audit: choose an AT cutoff
ladder using feature-space counts, AT gap, and non-target covariate feasibility
only.  Any high-AT co-shift in `V`, `AP`, or `RH` must be measured and carried
forward as a compound-shift diagnostic.  No PE-based cutoff choice, policy
tuning, or confirmatory outcome comparison is authorized yet.

## Linked artifacts

- Semantic framework: `experiments/E16B_CCPP_SEMANTIC_CONTRACT_V1.md`
- Source/domain contract: `experiments/E16B_CCPP_SOURCE_DOMAIN_CONTRACT_V1.md`
- Machine-readable audit: `results/prior_utilization_e16b/source_acquisition_v1/E16B_CCPP_SOURCE_MANIFEST_V1.json`
- Read-only audit script: `experiments/audit_e16b_ccpp_source.py`
