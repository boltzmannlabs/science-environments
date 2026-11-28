# Task 04 — achievements and comparison

| Objective | Achievement | Evidence | Limitation |
|---|---|---|---|
| Predict product | **Met** | Top-1 = target, score 1.0, RDKit canonical match | Target was supplied as structural input; not independent discovery |
| Recover routes | **Met with caveat** | Five valid Suzuki/Negishi routes | Exact reactant pair not in top five |
| Recommend conditions | **Partially met** | Ten conditions; water/dioxane 100–110 °C; 32.338% native yield | Base/catalyst identities generic; three service failures |
| Pd-NHC catalyst ranking | **Partially met** | Eight named Pd-NHC families from local optimizer | Design candidates only; no experimental best-catalyst validation |
| Maximize predicted yield | **Partially met** | C1 selected by composite; nominal C9 rejected for low feasibility | Yield weakly discriminating; no matched measurement |
| Minimize loading retaining yield | **Not met** | Loading encoded at 0.5/2/5 mol%; frozen yields attached | Yield model ignores loading; retention uncomputable |
| Identify side products | **Met** | Over-coupling, homocoupling, protodehalogenation candidates | Model-based, not measured |
| Traceable, non-fabricated execution | **Met** | Full tool trace; nulls preserved; frozen report | 3 HTTP 429 failures recorded |
| Experimental validation | **Not met** | Persistent campaign created, 6 experiments reserved | No lab measurements; withheld benchmark not accessed |

## Major findings

1. Correct product connectivity was obtained in the top-ranked forward prediction.
2. Synthetically plausible Suzuki/Negishi routes and the canonical Suzuki side-reaction classes were recovered.
3. The exact benchmark reactant pair was absent from the top-five retrosynthesis routes; the direct branch had to be preserved separately.
4. High nominal yields can be artifacts: reversing reactant order produced up to 77.420% for catalyst-free records.
5. The Pd-NHC constraint was met only by a locally supplied optimization tool with explicit `condition_space`, not by the yielding tools.
6. Catalyst loading can be encoded in `equivalents`, but the frozen ReactionT5 yield model is structurally blind to loading, so yield retention cannot be inferred.

## Comparison outcome

No literature or experimental number for this exact reactant pair was accessed. Therefore we report general literature consistency for reaction class, catalyst family and side products, and leave experimental comparison metrics null. No superiority claim is justified.
