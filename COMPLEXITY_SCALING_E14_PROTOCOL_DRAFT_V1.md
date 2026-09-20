# E14 — Complexity Scaling of Prior Anatomy under Matched Structural Content

## 1. Question

> Holding declared prior content and core-validity semantics fixed, how do
> prior informativeness, continuous structural evidence, completeness, scope,
> and measurement reliability change as **realization complexity** increases?

E14 tests whether the anatomy measured in E13 is limited to a one-dimensional
canonical realization. It is not a new prior grammar, a prediction experiment,
or a wrong-prior experiment.

The primary question is deliberately narrower than “does complexity hurt?”:

> **Do prior-anatomy distinctions survive increasing realization complexity?**

## 2. Boundary and invariants

E14 keeps the E13 canonical atom IDs and their frozen semantics:
`direction`, `curvature`, `inflection`, `turning`, `regime`, `bound`, and
`asymptote`. They remain **t-direction structural atoms**. E14-v1 does not add
multivariate, causal, interaction, memory, or dynamics atoms.

Let `x=(t,z)`, where `t` is the distinguished progression/extrapolation
coordinate and `z` is a context vector. Observation support remains `t<=.40`,
and the core declared prior domain is

`Omega_0=[.40,.80] x Z_ref`.

For every complexity condition:

- the intended atom packet, canonical atom library, compatibility registry,
  eta level, and requested full-envelope scope stratum are matched within a
  paired latent group;
- `P_star(Omega_0)` is determined and frozen once from the clean core field;
- candidates are all non-empty true subsets of that realized `P_star`;
- shared candidates within a task receive the same noisy observations,
  paired continuation bank, likelihood weights, and ESS;
- no atom that becomes true only after `.80` is added to `P_star`.

For a **primary paired group**, matched intended content is insufficient. The
realized canonical envelopes must satisfy exact atom-set equality, including
implied and incidental atoms:

`P_star^(c)(Omega_0) = P_star^(baseline)(Omega_0)`.

If any paired condition differs, the entire group is rejected from the primary
paired estimand and the mismatch is retained in cell-level accounting. This
prevents a complexity contrast from silently becoming a prior-content contrast.

E14 excludes RMSE, utility, harm, realization-engine comparison, LLM/RAG,
Prior Critic, false additions/reversals/numeric misspecification, and
path-dependent latent dynamics. Dynamics are a semantic-regime change and are
reserved for a later experiment rather than being called a complexity level.

## 3. Complexity is a vector, not one score

E14-v1 scales three separately manipulated realization axes. No pooled
`low/mid/high complexity` score is reported.

| Axis | Controlled levels | What changes | Primary background condition |
|---|---|---|---|
| Dimensionality | `d in {1,3,8}` total input dimensions | number of context coordinates in `z` | additive, no heterogeneity |
| Interaction | additive, pairwise, entangled | coupling among context effects | `d=8`, no heterogeneity |
| Structural heterogeneity | none, moderate, strong | context variation in numeric realization fields, e.g. `tau(z)` or `rho(z)` | `d=8`, additive |

The primary analyses are orthogonal branches from one matched base, not a
cumulative chain:

`f_0 -> { f_dim(d), f_int(r), f_het(q) }`.

Only predeclared corner cells combining high levels of the three axes are
reported as supplementary stress tests.

For dimension and interaction scaling, the context field is centered and
energy-matched across levels: `E_Z[g(z)]=0` and
`RMS_Z[g(z)]=sigma_g`, with the same frozen `sigma_g` within an axis. Dimension
uses a matched coefficient norm; interaction uses matched total context-field
RMS. Heterogeneity intentionally changes the RMS of fields such as
`tau(z)-tau_0` or `rho(z)-rho_0`, but each field remains mean-zero so the mean
baseline realization is not shifted.

## 4. Context support and atom semantics

`Z_ref^max` is a frozen 64-point scrambled-Sobol design in the seven-dimensional
context cube `[-1,1]^7` (seed `20261014`). For total dimension `d`, use the
deduplicated projection onto the first `d-1` context coordinates as
`Z_ref^(d)`. Thus `d=1` has exactly one null context; it never counts 64
copies of the same empty context. The reference design is used for core
validity, scope, and continuation-bank scoring.

Observation contexts are distinct from oracle reference contexts. Primary
fixed-budget observations use `N=49`: one null context with 49 prefix points
for `d=1`, and the first seven nested `Z_ref^(d)` contexts with seven common
prefix `t` points each for `d in {3,8}`. The supplementary density-compensated
control observes every reference context with the 49-point prefix grid
(`N(d)=49*|Z_ref^(d)|`). Evidence aggregation gives observed contexts equal
weight; oracle validity never substitutes `Z_obs` for `Z_ref`.

Each existing atom checker is evaluated at every `z in Z_ref` under the same
trajectory-only or latent-assisted semantics used in E13. Hence, for an atom
`a`, raw validity at horizon `h_j` is

`V_a(h_j)=I[the frozen checker passes on [.40,h_j] x Z_ref]`.

This means the atom must pass at every frozen reference context; it does **not**
create a new “multivariate atom.” For event atoms, each context must satisfy
the existing event type/count/tolerance rule. Context-varying locations such as
`tau(z)` are permitted only when the same atom remains valid at all reference
contexts.

Contiguous scope remains exactly E13's first-failure construction:

`C_a(h_j)=product_{k<=j} V_a(h_k)`

and for candidate `P`,

`C_P(h_j)=product_{a in P} C_a(h_j)`.

No failure through `1.20` is right-censored; no censored endpoint is converted
to `1.20` for a numerical average. Subset scope is derived from this one
atom-level table, so `C_Pstar(h)=1 => C_Psubset(h)=1` is an integrity
invariant.

## 5. Paired realization construction

For one latent packet and master seed, construct an orthogonal matched family

`f_0 -> { f_dim(d), f_int(r), f_het(q) }`.

The paired conditions share intended structural content, core semantic state,
eta, and requested scope stratum. Complexity changes realization structure,
not what the supplied prior says or which atoms constitute the primary paired
`P_star`. The base field is accepted only if every atom
in the realized core `P_star(Omega_0)` remains persistent through `1.20` over
`Z_ref` before scope intervention.

As in corrected E13, a frozen smooth post-`.80` intervention maps

`(f_base,z_base) -> (f_int,z_int)`

and must preserve the full clean field on `t<=.80` for **every** `z in Z_ref`.
The scorer receives `(f_int,z_int)` only through the clean oracle; it cannot
read requested stratum, proposal target, breaker identity, or intervention
parameters. Full-envelope scope stratum is accepted only when clean-oracle
measurement agrees with the requested stratum.

The full-envelope stratum is therefore a matched control, not a natural
complexity outcome. E14's scope endpoint is **conditional proper-subset scope
extension scaling given matched full-envelope scope**: `C_P(h)` and
`I[C_P(h)=1, C_Pstar(h)=0]` among proper subsets. Full `P_star` survival is
reported as control provenance only.

## 6. Observation, bank, and evidence conventions

### Primary observation-budget condition

The primary comparison fixes the total observation budget `N` across all
dimensions. Observations are allocated by a frozen context-balanced design, so
higher dimension includes the realistic sampling-density cost of representing
more context. A supplementary density-compensated control increases `N` by a
predeclared rule; it separates this sampling-density component from the
dimension comparison but is not pooled with the primary estimand.

### Common continuation-bank rule

Every complexity level uses the same bank size `M` and the same master bank
draws. Bank member `m` begins with one master latent draw `xi_m`, transformed
deterministically into each matched field
`xi_m -> {f_m^dim, f_m^int, f_m^het}`. Thus paired sharpness contrasts do not
contain an avoidable Monte-Carlo-bank difference.

E14-A selects one common `M` from the nested ladder
`4096 subset 8192 subset 16384`, using `16384` as the convergence reference.
The smallest candidate `M` is accepted only if, in every E14-A cell,

- the 95th percentile of `|S_M-S_16384|` is at most `.02 nat`;
- the 95th percentile of exact non-floor
  `|Delta S_miss,M-Delta S_miss,16384|` is at most `.02 nat`;
- floor-state agreement is exactly 100%; and
- within-task candidate sharpness-rank Spearman agreement is at least `.99`.

If none passes, `M=16384` is retained; expanding beyond that ladder requires a
new protocol freeze. ESS is explicitly **not** an `M` selection criterion and
remains a reliability outcome.

The prefix likelihood is an equal-context mean of within-context MSE, so a
density-compensated condition does not mechanically add evidence solely by
adding observations. It uses one task-level clean reference range evaluated
over the frozen core/reference design; prefix-specific normalization is
prohibited.

### Continuous evidence is primary

For each atom, E14 stores continuous `E_a`, computed by the frozen E9
template-contrast rule separately on each actual noisy observed context
`z in Z_obs`, then aggregates as

`E_a = (1/|Z_obs|) sum_z E_a(z)`.

Each observed context therefore receives equal weight regardless of its number
of samples; at `d=1` this is the one null context. `O_P=I[min_{a in P}
E_a>=.80]` remains a secondary state label only. Likewise `S(P|D)` is primary
and `I[S>=.10]` is only a state label. Thresholds are not retuned in response
to E13 saturation.

## 7. E14-A — Measurement-Scaling Sanity

Before any factorial run, execute a small, balanced pilot across every level
of each axis. It may only test implementation integrity:

1. all core candidates have coverage one on `Omega_0`;
2. realized `P_star` is core-frozen, includes implied atoms, and is exactly
   equal across every member of a primary paired group;
3. the base field is persistent through `1.20` at every `Z_ref` context;
4. intervention is core-invariant on `t<=.80` at every reference context;
5. `V_a -> C_a -> C_P` agrees with direct candidate checker evaluation;
6. sharpness and scope nesting hold for all subsets;
7. `S`, ESS, `d_eff`, `V_f`, `N_survive`, and floor state are finite or
   explicitly classified; low ESS remains `measurement_unreliable`, never a
   task-generation rejection;
8. paired master-bank draws, the same selected `M`, equal-context likelihood,
   and context-balanced evidence rule are used at every complexity level;
9. eta enters the actual noisy-prefix evidence path and `E_a` is not copied
   from its label.

No direction of ESS, sharpness, completeness, evidence, or scope change is a
sanity gate.

## 8. Primary endpoints and paired analysis

For each matched latent group and candidate subset, E14 reports paired changes
from its declared baseline condition:

`Delta Y(c)=Y(c)-Y(baseline)`.

Primary outcomes are:

1. **Reliability scaling:** `P(ESS>=100)`, floor rate, `N_survive`, `d_eff`,
   and normalized `V_f`.
2. **Conditional sharpness scaling:** continuous `S(P|D)` and its paired
   contrast.
3. **Completeness scaling:** exact/reliable
   `P(Delta S_miss<=.10 | C_atom=0)` and its audit denominator.
4. **Non-implied conditional-redundancy scaling:** the same completeness rate
   restricted to no-implied-omission candidates, directly comparable to E13's
   59.9% reference result.
5. **Scope-profile scaling:** `P(C_P(h)=1)` and proper-subset extension
   magnitude, never a mean of censored `H_valid*`.
6. **Descriptive joint geometry:** continuous context-balanced `E_a`, `S`,
   exact `Delta S_miss`, and `C_P(h)`.

Latent-task clustered bootstrap remains the only primary uncertainty method.
Within-task candidate weights and equal generator weighting are retained.
Association displays mask the same definitional dependencies as E13: core
validity with all axes, candidate size with `C_atom`, `S` with `Delta S_miss`,
`N_obs` with `O_P`, and subset/full scope direction.

## 9. Execution order and remaining numerical freeze

1. Freeze the scientific generator families, their parameter ranges,
   `Z_ref^max`, `Z_obs`, energy-matching rules, context evidence aggregation,
   and the common bank ladder.
2. Implement matched persistent base families for the three independent axes.
3. Run E14-A measurement-scaling sanity.
4. Freeze the selected common `M`, seeds, accepted paired-task IDs, and paired
   task manifest. A failed E14-A may not motivate in-place changes to scientific
   generator ranges; such a change requires an E14 v1.1 protocol.
5. Run E14-B (dimension), E14-C (interaction), and E14-D (heterogeneity)
   separately; only then run predeclared combined-corner stress cells.

The unresolved numerical values in step 1 are not scientific degrees of
freedom after E14-A. They must be recorded in an execution freeze before the
first full E14 run.

## 10. Interpretation boundary

E14 can show whether E13's operational anatomy remains measurable and how it
changes under these controlled realization-complexity axes. It cannot infer
real-world prevalence, prove a universal curse-of-dimensionality law, estimate
causal effects from pooled associations, validate new multivariate grammar
atoms, or evaluate prediction/utility/safety.
