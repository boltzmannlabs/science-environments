# BolChem task design notes

**Contribution type:** environment specification and documentation.
Owner: Ankith116. Related issue: #46. Updated 5 November 2026.

## Defined deliverable

Two task contracts plus owner documentation, maintained under
[de novo environment](../../environments/small-molecule-de-novo-design/README.md) and [optimization environment](../../environments/small-molecule-optimization/README.md).
The source list is [references.md](references.md). Agent-facing tasks intentionally
omit literature names, links, historical candidate outcomes and reference-algorithm
instructions. The agent chooses the workflow; the objective and evaluator remain
fixed.

## Scientific design decisions

De novo uses one protein, p38α, with one structural context, 1A9U. It permits
generation/screening/search strategies and applies a common Smina assessment to a
ten-slot final panel. The panel mean is distinct from an up-to-three display
shortlist. Invalid/missing outputs, repeated structures and generation/search
effort remain visible. A generated structure is not automatically chemically novel.

Optimization uses one DRD2 target with original starting molecules tracked
independently. Its default count requires the same candidate to improve both
predicted activity and QED while retaining count-Morgan r2 similarity >0.7 to
the original starting molecule. Reseeding does not reset that comparison.
ADMET guidance and mandatory ADMET success conditions are distinct frozen variants.

The source reviews distinguish the optimization predictor's feature path from the
similarity evaluator: the inspected example uses radius-3, 2048-bit model inputs,
whereas parent similarity uses sparse non-feature count-Morgan radius 2. The
example config is not itself the exact constrained-optimization recipe. Model
loading, original input identities and precise numeric baseline records remain
qualification work.

## Comparison limits

The selected de novo reference reports 100 targets; a single 1A9U result cannot
be compared directly with that full-suite mean. Verify matching case-level inputs,
candidate selection, preparation, descriptors and scoring before a numeric claim.
The current search-selected panel policy also needs an explicit comparison to the
reference's endpoint semantics or a baseline rerun under the common policy.

The optimization reference's full nominal sampling scale is distinct from pilot
experiments. Equal exported rows or final shortlist sizes do not imply equal
generation, scoring, training or reasoning cost. Adding mandatory ADMET conditions
defines a changed task, not an equivalent published score.

## Integration boundary

This specification set complements the wider work tracked in #46. It does not
copy or replace an executable small-molecule runtime, native plugin or specialist.
Existing modified checkouts/branches are outside this contribution. Runtime
integration and performance claims require separate evidence.

## Outstanding questions and dependencies

- Are the exact prepared structural inputs and final scoring adapter qualified?
- Are all chosen optimization references available as verified structures?
- Does the supplied activity model load with its exact feature/output semantics?
- Are sampling and financial ceilings enforceable for each chosen hosted tool?
- Which independent evaluator and frozen baseline apply to the selected run scale?

These are documented uncertainties. No measured/predicted candidate result was
invented or executed to populate this contribution.
