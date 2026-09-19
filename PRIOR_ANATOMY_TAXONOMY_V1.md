# Prior Anatomy Taxonomy v1

## Why a layered taxonomy

“The prior failed” is not a diagnosable statement. This taxonomy separates
failure sources that can, in principle, be experimentally distinguished. It is
not a demand to test all layers simultaneously.

## Twelve separable layers

| Layer | Object / question | Distinct failure |
|---|---|---|
| 1. World truth | What latent mechanism and continuation occur? | The assumed world structure is false. |
| 2. Knowledge source | Paper, physics, expert, LLM/RAG, observation | The source supplied bad or non-transferable knowledge. |
| 3. Prior content | Constraint `C`, e.g. decreasing or one regime | The structural statement is false. |
| 4. Specification | Parameters `theta`: onset, rate, shape, bound | Content is right but its numerical/range detail is wrong. |
| 5. Scope | Domain `Omega`: unit, environment, time/horizon | Content is true only in a smaller region. |
| 6. Belief / provenance | Credence, uncertainty, evidence type, source | Confidence is miscalibrated or evidence is indirect. |
| 7. Evidence / identifiability | What the current prefix determines | The structure may be true but cannot be verified or realized now. |
| 8. Translation / encoding | Natural-language/scientific claim to formal constraint | The semantics were encoded incorrectly. |
| 9. Enforcement / integration | Hard constraint, penalty, projection, anchor, weighting | A correct encoding was imposed inappropriately. |
| 10. Realization engine | Function class able to represent a continuation | The engine cannot express a compatible useful function. |
| 11. Fitting / optimization | Solver, initialisation, budget, regularisation | A suitable engine failed to find its solution. |
| 12. Arbitration / deployment / decision | Composition, selection, context, loss, abstention | Priors were combined/deployed/evaluated wrongly. |

The compact scientific-prior object is

`P = (C, theta, Omega, q, pi)`, where `C` is content, `theta` specification,
`Omega` scope, `q` uncertainty/confidence, and `pi` provenance. `q` is not the
same object as `C`: “decreasing” and “95% confidence in decreasing” must remain
separate.

## Validity, informativeness, and completeness

All three are grammar-relative in v1. Let `G` be the registered prior grammar.

- **Validity / coverage preservation:** `P` is valid relative to `G` and a
  declared scope when the actual continuation remains in its allowed set.
  A weak constraint such as an extremely loose bound can be valid.
- **Informativeness:** conditional sharpness or other restriction relative to
  the data-conditioned reference ensemble. Validity alone does not imply useful
  additional information.
- **Completeness:** how much valid structural information in `G` is absent from
  the supplied prior. The grammar-relative oracle envelope is the conjunction
  of all registered constraints that preserve the actual continuation. Its
  sharpness gap versus the supplied prior measures *missed valid information*
  inside `G`, not knowledge missing from the real world outside `G`.

Therefore “true prior” is avoided in reports when it could imply a unique best
description. Preferred terms are **supplied valid prior**,
**coverage-preserving prior**, **informative valid prior**, and, when one
valid constraint set is nested inside another over the same scope,
**dominating valid prior**. Valid priors need not form a total order; this is
why the intended object is a coverage-preserving information frontier rather
than one universal best prior.

## Four uncertainty types

1. **Existence uncertainty:** is the structure present at all?
2. **Specification uncertainty:** where are onset, scale, bound, and scope?
3. **Realization uncertainty:** which future among all functions satisfying the
   constraint will occur?
4. **Transport uncertainty:** does the statement survive another unit,
   generator, environment, or domain?

This distinguishes task truth from a domain-stable scientific prior.

## Measurement qualifications

The following words are not interchangeable and are not all intrinsic prior
properties.

- **Coverage** is truth *over an explicitly declared scope/horizon*.
- **Logical specificity** is set inclusion among formal constraints.
- **Conditional sharpness** is restriction relative to a declared
  data-conditioned reference ensemble `Q`; it changes with `D` and `Q`.
- **Realization multiplicity** is the size/diversity of allowed continuations;
  it also requires a reference function class and measure. It is related to,
  but not identical with, sharpness.
- **Utility/harm** is deployment-dependent:
  `U(P | translation, integration, engine, optimisation, context, loss)`.
- **Persistence / validity horizon** is a scope property, not merely truth.
- **Fragility** is sensitivity to structured perturbations, which must name
  their type: sign, magnitude, location, scope, missing true constraint, or
  extra false constraint.

## Additional distinctions that remain necessary

- **Mechanistic versus phenomenological truth:** a trajectory can satisfy a
  visible constraint without having the corresponding causal mechanism.
- **Structural versus practical identifiability:** infinite clean data may
  identify a model even when the finite noisy prefix cannot.
- **Evidence directness versus confidence:** direct observation, proxy evidence,
  and external knowledge can have identical numeric confidence but different
  failure modes.
- **Composition versus selection:** `A AND B` studies the joint constraint;
  choosing among A/B/C is an admission/arbitration problem.
- **Logical conflict versus geometric tension:** priors may be inconsistent, or
  jointly feasible but leave a dangerously narrow/unstable realization set.
- **Vocabulary completeness versus proposal recall:** the grammar may lack a
  required primitive even if a proposer exhaustively searches that grammar.
- **Representation invariance versus semantic equivalence:** a valid prior
  should survive unit/coordinate changes; distinct text/formulae may still
  restrict the same continuation set.
- **Value of additional evidence:** not just “insufficient now,” but whether a
  specified new observation would reduce uncertainty enough to change a
  decision.

## Current experimental scope and order

The present Prior Anatomy stage intentionally focuses on layers 1, 3–7:
truth/content/specification/scope/belief/evidence and their measurements.
E9 addresses minimum informational evidence; E10 addresses scope/validity
horizon; E11 will address grammar-relative completeness; E12 will decompose
structured misspecification and fragility.
Translation onward is held separate until the anatomy is understood. The later
Prior Critic is an arbitration/deployment object, not a replacement for this
taxonomy.
