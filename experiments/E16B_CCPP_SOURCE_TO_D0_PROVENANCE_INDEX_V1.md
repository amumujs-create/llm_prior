# E16-B CCPP Source-to-D0 Provenance Index v1

## Status

**FROZEN through target-free D0.** Every object below was created without
using target outcomes, except that the original source workbook necessarily
contains its target column. X-only code requests at most `AT,V,AP,RH` and does
not materialize the target column.

## Provenance chain

\[
\text{UCI DOI}\rightarrow\text{official ZIP}\rightarrow\text{XLSX}\rightarrow
\text{Sheet1}\rightarrow\text{source/domain}\rightarrow\text{X-only split}
\rightarrow\text{replay}\rightarrow\text{prior realization}\rightarrow\text{D0}.
\]

| Object | Path or identity | SHA-256 | Git commit | Status | Target accessed |
|---|---|---|---|---|---|
| Official source | UCI DOI `10.24432/C5002N`, official archive ZIP | ZIP `cc7b2a4977c0a44e8221c91d9a7e5746b3c68186cff7e5c61c70af6432b98c7a` | External source | PASS | No analysis |
| Canonical workbook | `Folds5x2_pp.xlsx`, Sheet1 | `ccd490981db2a2f079963b3d9f0aea30d9d338900a0285428dfc6385396f4651` | External source | PASS | Source-only audit handled all columns; later audits do not load target |
| Semantic contract | `experiments/E16B_CCPP_SEMANTIC_CONTRACT_V1.md` | `5a65cc74bcd613b5ad7a678f50c42b34180303a148930d29420cf9be0f1cda64` | `46dc635` | FROZEN | No |
| Source/domain contract | `experiments/E16B_CCPP_SOURCE_DOMAIN_CONTRACT_V1.md` | `a762f4b9036a0acc518d41d66acc29e7e224a872afe27f79059e79e8ed6b42bc` | `03cdba7` | FROZEN | No |
| Source manifest | `results/prior_utilization_e16b/source_acquisition_v1/E16B_CCPP_SOURCE_MANIFEST_V1.json` | `96534c72420df127e3c43b87ae01492d2bb2efe2152409c5586ff0852b9cb391` | `03cdba7` | PASS | Source-structure audit only |
| X-only geometry contract | `experiments/E16B_CCPP_XONLY_GEOMETRY_CONTRACT_V1.md` | `7086871f9063e778d4adbdc8c43c1ec814a2a3c7410c9cb08754e9e8f0d473aa` | `1ff7d10` | FROZEN | No |
| X-only geometry | `results/prior_utilization_e16b/xonly_geometry_v1/E16B_CCPP_XONLY_GEOMETRY_V1.json` | `b1cf100c8453d609816bcc8f2eaa9e3724a7ff540e6de9a541fbec603fbb3753` | `1ff7d10` | PASS | No |
| Split replay | `results/prior_utilization_e16b/xonly_geometry_v1/E16B_CCPP_SPLIT_REPLAY_INTEGRITY_V1.json` | `f6455174876f4aec9e5eb6da261a1563443ed1f5b1a03de7da323a1e47e09f9a` | `8fc0237` | PASS | No |
| Prior-realization contract | `experiments/E16B_CCPP_PRIOR_REALIZATION_CONTRACT_V1.md` | `28cab466020c4681ce6fca5fab94387ee8b660024780d9bb115b80da22b66bb8` | `8fc0237` | FROZEN | No |
| D0 candidate-grid contract | `experiments/E16B_CCPP_D0_CANDIDATE_GRID_CONTRACT_V1.md` | `02fb9fc5ea621b303f5b7b493bdb44ec488602134993e48c00fa641a47f762fd` | `57f9f22` | FROZEN | No |
| D0 construct artifact | `results/prior_utilization_e16b/d0_candidate_grid_v1/E16B_CCPP_D0_CANDIDATE_GRID_V1.json` | `0cab946725de42bbd7a4edb9a34b27d150ea3ebaa70acdf8551d3a62afb96f23` | `57f9f22` | PASS | No |

## Frozen consequences

- Canonical corpus remains Sheet1; the other four workbook sheets are only
  permutation audits and are never concatenated.
- The split is `AT <= q70` train, `q70 < AT <= q85` validation,
  `q85 < AT <= q90` guard, and `AT > q90` confirmatory test. Validation is
  never merged into training.
- The test is labelled **high-AT extrapolation under compound covariate
  shift**, not AT-only extrapolation.
- D0 fixes a 405-candidate monotone continuation reference measure but does
  not fit candidates or score validation/test targets.

## Next gate

The next authorized artifact is the capacity contract. Only after it is
frozen may train targets be opened to determine the train-only target scale,
candidate nuisance fits, and shared train-only ridge selection. Validation
targets remain sealed until all candidate predictions have been fixed.
