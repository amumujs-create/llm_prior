# PPT storyboard

## Recommended 4-slide arc

### Slide 1 — The problem is not merely prior retrieval

- Use `figures/fig04_experiment_logic.png`.
- Headline: **“A true prior is not automatically a usable prior.”**
- Say: A retrieval system can identify a plausible mechanism, but the observed
  prefix may not yet contain the evidence needed to estimate its parameters.
- Do not claim that this is proven on real data.

### Slide 2 — Generic prior observability causes a utility phase change

- Use `figures/fig01_observability_to_utility.png`.
- Headline: **“Across three generic structures, utility turns positive only after evidence appears.”**
- Define y-axis on slide: `RMSE(fallback) − RMSE(prior)`; above zero is helpful.
- Emphasize the low-O negative region and high-O positive region.
- Result to cite: family-level O→utility Spearman is 0.568 / 0.346 / 0.943;
  this is development evidence from 1,260 synthetic trajectories.

### Slide 3 — Admission is a separate, testable problem

- Use `figures/fig02_admission_rates.png` and/or `figures/fig03_score_diagnostic.png`.
- Headline: **“Validation admission must detect observability—not just select a low prefix loss.”**
- Present both uniform and tail-weighted rules as *development baselines*, never
  as a finalized solution unless all family-level diagnostics pass.
- v1 conclusion: neither rule is a general admission solution. In particular,
  tail weighting rejects only 50.6% of zero-observability priors and accepts
  only 13% of high-observability regime-change priors.

### Slide 4 — Research program and falsification rules

- Reuse `fig04` or make a simple arrow from `EXPERIMENT_LOGIC.md`.
- Sequence: Generic prior value → Observability/admission → Retrieval candidate
  recall → richer simulators → real data.
- Safe claim: The v1 laboratory establishes the need to model observability.
- Unsafe claim: “RAG improves real extrapolation” or “the admission problem is solved.”

## Admission-v2 add-on slides

### Slide 5 — Admission should predict utility, not observability alone

- Use `figures/fig07_admission_v2_logic.png`.
- Headline: **“Observability is evidence; useful extrapolation is the decision target.”**
- Explain that `O_true` is excluded from the classifier. The model sees only
  prefix evidence and is trained to distinguish helpful from harmful priors.

### Slide 6 — Safety–coverage trade-off on locked synthetic seeds

- Use `figures/fig05_v2_coverage_harm_risk.png`.
- Headline: **“Evidence-aware admission cuts harmful-prior admission: 65.0% → 20.9%.”**
- Pair it with the coverage change, 63.3% → 56.3%; never present the safety gain
  without this abstention cost.
- Qualifier: v2 is synthetic development evidence with a held-out seed split,
  not a real-data or final-method claim.

### Slide 7 — Identifiability is an essential evidence axis

- Use `figures/fig06_v2_evidence_coefficients_labeled.png`.
- Headline: **“A plausible, visible structure can still be unsafe when its parameters are unstable.”**
- Coefficients are descriptive of the development model, not causal rankings.

## Figure provenance captions

Every figure should carry: “Synthetic generic-prior development study; family
parameters fitted from prefix only; clean far-OOD tail withheld from selection.”
