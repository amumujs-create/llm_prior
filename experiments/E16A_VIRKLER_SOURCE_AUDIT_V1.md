# E16-A Virkler Source Acquisition Audit v1

## Disposition

**No source bytes are frozen and no confirmatory split is authorized.**  This
audit establishes the source hierarchy and acquisition gates for E16-A; it is
not a data acquisition, numerical-design, or outcome-analysis artifact.

## Experimental provenance

The original experimental reference is D. A. Virkler, B. M. Hillberry, and
P. K. Goel, *The Statistical Nature of Fatigue Crack Propagation*, *Journal of
Engineering Materials and Technology* 101(2), 148–153 (1979), DOI
`10.1115/1.3443666`.

The primary publication description reports 68 replicate constant-amplitude
crack-propagation tests on 2024-T3 aluminum alloy.  Independent later
documentation of the same experimental corpus describes 68 trajectories with
164 measurement points, common specimen geometry, constant loading, and an
initial crack size of 9 mm.  A technical implementation description further
states that the observations are half-crack length \(a\) versus cycles \(N\)
required to reach that length, from 9 mm to 49.8 mm, at 164 discrete levels.
These statements support the E16-A observation-aligned representation
\(N=N(a)\).

## Candidate hierarchy

| Priority | Candidate | Audit disposition |
| --- | --- | --- |
| 1 | `SimoneHermann/hierRegSDE`, `data/Virkler.rda` | **Primary acquisition candidate, pending byte-level audit.** Documentation specifies 164 rows and 69 columns: one crack-length column and 68 cycle-count trajectories. It credits Eric J. Tuegel for data collected by Prof. B. M. Hillberry. |
| 2 | Original Virkler–Hillberry–Goel paper and experimental documentation | **Required provenance/physics reference.** Used to verify experimental regime and public geometry, not assumed to be a machine-readable release. |
| 3 | Partial package subsets (for example, a 25-test dataset) | **Sensitivity only.** Prohibited as the primary full-corpus source. |
| 4 | `WarrRich/Virkler-Data` figure-digitized reconstruction | **Primary prohibited.** Its README says it was digitized from a photographed book figure and notes that reconstructed paths do not cross even though some original paths do. |

## Candidate-source evidence

- [hierRegSDE Virkler documentation](https://rdrr.io/github/SimoneHermann/hierRegSDE/man/Virkler.html)
  explicitly describes 68 replicate tests, the fixed-length/observed-cycle
  orientation, and a 164-row by 69-column dataframe; it identifies
  `data/Virkler.rda` in the source listing and credits the data lineage.
- [hierRegSDE source listing](https://rdrr.io/github/SimoneHermann/hierRegSDE/f/)
  identifies the packaged `data/Virkler.rda` artifact.
- [Original publication record](https://cir.nii.ac.jp/crid/1363670320755944064)
  records the 68 replicate constant-amplitude tests, 2024-T3 alloy, journal,
  date, and DOI.
- [Later dataset description](https://c3.ndc.nasa.gov/dashlink/static/media/publication/2010_IJPHM_fatigue.pdf)
  describes 68 trajectories with 164 points and constant-loading geometry.
- [Implementation-level experimental description](https://oaktrust.library.tamu.edu/server/api/core/bitstreams/0d20556e-daff-4f39-be68-d2d53f096f0a/content)
  describes the \(a,N\) observation orientation, 9–49.8 mm range, and the
  nonuniform crack-length increments.
- [Digitized-reconstruction README](https://github.com/WarrRich/Virkler-Data)
  documents the photograph-based reconstruction and its trajectory-crossing
  limitation.

## Acquisition gate for the primary candidate

Before source selection can be frozen, acquire a pinned copy of the candidate
data artifact and record all of the following in a new source-manifest
artifact:

1. exact upstream repository commit or immutable release locator;
2. download date and cryptographic SHA-256 of the raw file bytes;
3. package license and any separately stated license/use terms for the
   underlying experimental data;
4. decoded data shape, column mapping, units, crack-length grid, and all
   missing/non-finite/monotonicity findings;
5. verification that it contains 68 complete specimen trajectories at the
   advertised 164 common crack-length levels;
6. comparison of its public geometry/loading metadata with the original and
   later experimental documentation, without altering its values;
7. an explicit determination of whether the package copy is sufficient as the
   primary provenance-linked corpus or whether a more archival full-data
   release must be obtained.

If any of items 3–5 fail or are unavailable, the candidate remains unfrozen;
no split, prefix, model, or policy analysis may proceed.  The figure-digitized
reconstruction must not be substituted merely to unblock E16-A.

## Consequence for protocol status

E16-A semantic policy/estimand definitions are frozen by
`E16A_VIRKLER_SEMANTIC_CONTRACT_V1.md`.  Dataset acquisition, split design,
numerical calibration, quota, and confirmatory execution remain explicitly
open pending this gate.
