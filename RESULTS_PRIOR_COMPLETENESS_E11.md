# E11 — Grammar-Relative Prior Completeness

## Question

Within the fixed declared scope `Omega=[.40,.80]`, how much valid structural
information does a supplied prior omit relative to the **unique
inclusion-maximal compatible coverage-preserving envelope** available in the
frozen E11 canonical grammar?

This is not a search for a single world-best prior. The estimand is explicitly
conditional on a task having a unique maximal compatible envelope in the
frozen grammar.

## Integrity and frozen identity

The full run accepted **720 latent tasks** (`8 intended atom triples × 3
generators × 30 tasks`) and wrote **5,760 candidate/envelope rows**. Every
triple × generator cell reached its requested sample size; there were zero
cell exhaustions, zero nested-floor violations, and no candidate or oracle
floor hits. The integrity suite passed.

The run used the pre-frozen canonical atom library (`137f…6326a`), exact
intended-atom registry (`c739…cd7`), and atom-instance compatibility/scope
registry (`9cf4…d54`). The complete hashes and runner hash are stored in
`results/prior_completeness_e11/run/summary.json`.

## What was measured

Two deliberately separate properties were evaluated.

- **Canonical atom completeness:** `C_atom(P_s)=1` only when the supplied
  canonical atom set exactly equals the oracle envelope.
- **Informational completeness:** `Delta S_miss = S(P_star|D)-S(P_s|D)` is
  practically complete when it is at most `.10 nat`, subject to the primary
  `ESS >= 100` rule.

No prediction model, future RMSE, utility, safety outcome, or engine output
enters E11 scoring. Clean future trajectories were used only during task
generation/oracle validity selection, never during the data-conditioned
sharpness calculation.

## Main result

All 5,040 supplied candidates were atom-incomplete in this deliberately
constructed corpus: supplied candidates are subsets of the intended triple,
whereas the maximal envelope can also contain incidental valid atoms. This is
not an empirical claim that every real supplied prior is atom-incomplete.

More importantly, atom incompleteness did **not** imply information
incompleteness. Across all supplied candidates:

| Status | Rate |
|---|---:|
| Informationally complete (`Delta S_miss <= .10`) | 41.6% |
| Informationally incomplete (`Delta S_miss > .10`) | 48.3% |
| Measurement-unresolved (`ESS < 100`) | 10.1% |

The median missing conditional information was `.104 nat` (mean `.231 nat`),
just above the frozen practical threshold. Thus the same syntactic state — a
missing canonical atom — can mean either conditionally redundant content or a
material omission.

![E11 completeness by supplied size](figures/fig38_e11_completeness_by_supplied_size.png)

As expected in this controlled corpus, one-atom supplied priors omitted more
information on average than pair or intended-triple supplied priors. This is a
sanity-compatible anatomy pattern, not an estimate of a universal law.

## Which omitted atoms mattered conditionally?

The context-dependent mean marginal information was highest for the missing
`turning_maximum` (`.412 nat`) and `inflection_concave_to_convex` (`.352 nat`),
followed by asymptote (`.234`) and convex curvature (`.227`). The lower-bound
atom averaged `.089 nat`, below the predeclared `.10 nat` practical threshold.
These are not intrinsic atom rankings: a marginal value depends on the
already-supplied constraints, observed prefix, and frozen continuation bank.

![E11 marginal missing-atom information](figures/fig39_e11_marginal_information.png)

## Interpretation

E11 operationally supports the distinction:

`validity != canonical content completeness != conditional informational completeness`.

A prior may be coverage-preserving and omit canonical atoms, yet be
informationally complete because the omitted content is redundant after the
observed data and supplied constraints are conditioned on. Conversely, a
coverage-preserving prior can omit a large amount of grammar-relative
conditional information.

This result is limited to the frozen 1D scalar grammar, fixed scope,
controlled generator corpus, and tasks with a unique maximal compatible
envelope. It does not establish world completeness, prediction utility,
calibration robustness, safe deployment, or a best realization engine.

## Artifacts

- [Execution freeze](E11_EXECUTION_FREEZE_V1.md)
- [Canonical atom library](E11_CANONICAL_ATOM_LIBRARY_V1.json)
- [Exact intended atom registry](E11_INTENDED_ATOM_INTENTS_V1.json)
- [Compatibility/scope registry](E11_COMPATIBILITY_SCOPE_REGISTRY_V1.json)
- `results/prior_completeness_e11/analysis/` — cross-classification, size and
  triple summaries, marginal information, and machine-readable summary.
