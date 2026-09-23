# E16-B CCPP Source and Domain Contract v1

## Status

This contract freezes the source candidate and the qualitative primary prior
packet.  It freezes no raw bytes, cutoff, split allocation, model, policy
strength, residual specification, quota, or outcome.

The official source candidate is the UCI Machine Learning Repository DOI
release:

\[
\texttt{10.24432/C5002N}.
\]

Its disposition is **PASS_PENDING_BYTE_AUDIT**.  Repositories, Kaggle copies,
and other redistributions are prohibited as the primary source.

## Source and rights boundary

UCI describes 9,568 full-load observations collected over 2006–2011, with
features \(AT,V,AP,RH\) and target \(PE\).  It identifies the dataset license
as CC BY 4.0.  The subsequent source acquisition must freeze the official ZIP,
`Folds5x2_pp.xlsx`, and `Readme.txt` by raw-byte SHA-256 and verify that each
of the five workbook sheets is the same 9,568-row multiset in a different
permutation.  Sheet 1 alone will then be the canonical corpus; the other four
sheets are replication audits and must never be concatenated.

Exact duplicates, if any, are an audit count/grouping property at this stage;
they must not be removed before a later, outcome-free numerical-design
amendment.

## Primary prior packet

The sole primary E16-B v1 structural prior is conditional AT non-increase:

\[
\frac{\partial PE}{\partial AT}\le0.
\]

Interpretation:

> Within the full-load CCPP operating envelope, holding the other supplied
> covariates fixed, increasing ambient temperature does not increase net
> electrical power output.

This is supported by combined-cycle thermodynamics: higher ambient
temperature reduces intake-air density and compressor mass flow, reducing gas
turbine and combined-cycle output.  The prior supplies no slope magnitude,
curvature, interaction magnitude, globality beyond the operating envelope, or
policy strength; all remain unresolved specification uncertainty.

The primary support coordinate is \(AT\), and the primary extrapolation
direction is the high-temperature tail.  All four covariates remain model
inputs; defining support along AT does not discard \(V,AP,RH\).  A later
X-only design audit must quantify whether high-AT rows also occupy extreme
regions of the remaining covariates.  If so, the result must be described as
compound covariate shift rather than AT-only extrapolation.

## Explicitly excluded components

- **AP:** externally plausible positive direction, but withheld from the
  primary packet to keep the first external test to one strongly motivated
  structural statement.
- **RH:** configuration-dependent direction; unresolved and excluded.
- **V:** the UCI field is exhaust vacuum in cm Hg, but the sign convention
  cannot be independently mapped to a physical condenser-pressure statement
  at this stage; unresolved and excluded.

Neither an outcome-derived correlation nor any target-derived diagnostic may
be used to promote an excluded component into the packet.

## Required byte-level audit

The next acquisition artifact must record:

1. official DOI/archive locator, acquisition date, ZIP raw-byte SHA-256, and
   each extracted file's SHA-256;
2. license text/locator and UCI citation metadata;
3. workbook sheet names, dimensions, column names, units, missing/nonfinite
   counts, and exact duplicate-row count in each sheet;
4. a canonical row-hash multiset comparison demonstrating whether all five
   sheets are permutations of the same observations;
5. the canonical Sheet 1 SHA-256 and a source PASS/HOLD/REJECT disposition.

No cutoff ladder, split, target transformation, model capacity, or policy
outcome is authorized until the byte-level audit passes.

## Public evidence

- UCI official dataset page and DOI: https://archive.ics.uci.edu/dataset/294/combined%2Bcycle%2Bpower%2Bplant
- UCI records 9,568 full-load observations, the variables/units, five shuffles
  for 5x2 cross-validation comparability, and CC BY 4.0.
- Alhazmy and Najjar, *Energy* (2004), describes reduced air density/mass flow
  and reduced combined-cycle output as ambient temperature rises:
  https://www.sciencedirect.com/science/article/pii/S0306261904000601
- Bakhshayesh et al., *Applied Energy* (2007), documents the same intake-air
  temperature mechanism in a combined-cycle application:
  https://www.sciencedirect.com/science/article/pii/S0196890406003335
