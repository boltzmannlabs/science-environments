# Task 04 — comparison of predictions with literature/benchmark expectations

[Task](../../tasks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Benchmark](../../benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Results](README.md)

Blind rule: withheld measured yields, benchmark ID, original paper and known optimum were not accessed. Literature columns therefore describe **general chemistry expectations**, not an exact-pair experimental comparator. Model scores are not yields.

## Product and routes

| Aspect | Our result | Literature/expectation | Assessment |
|---|---|---|---|
| Top-1 product | `COc1ccc(-c2ccc(C(F)(F)F)cc2)cc1`, model score 1.0, feasibility 0.9934 | Suzuki coupling of the supplied aryl chloride and boronic acid gives this biaryl | **Met** |
| Routes | 5: three Suzuki, two Negishi | Suzuki is the standard biaryl disconnection | **Comparable** |
| Exact supplied pair in ranked routes | No; R2 recovers the boronic acid only | Direct aryl chloride + boronic acid is the obvious disconnection | **Underperformed** |
| Route scores | Null/placeholder | Ranked native confidence expected | **Unavailable** |

## Conditions and catalyst constraint

| Parameter | Our result | General literature | Assessment |
|---|---|---|---|
| Catalyst (internal/Parrot) | Generic "palladium catalyst"; Parrot top-6 had no catalyst; copper only later | Pd with NHC ligand is indicated for aryl-chloride Suzuki | **Partial / weak** |
| Base | Generic "base" | K2CO3, K3PO4 or Cs2CO3 typical | **Missing identity** |
| Solvent (internal top) | water/1,4-dioxane | Aqueous dioxane is standard | **Comparable** |
| Temperature | 100–110 °C (internal); 60–110 °C (design) | Elevated temperature expected for aryl chlorides | **Comparable** |
| Native predicted yield | 32.338% for 8/10 conditions; 47.447% rejected | No matched measurement available | **Unverifiable** |
| Pd-NHC design | 8 named Pd-NHC families from local optimizer | IPr/IPent/PEPPSI/chloro-dimer/indenyl/DMS families are literature-supported | **Met at family level** |
| Catalyst loading | 0.5/2/5 mol% encoded in equivalents | Reduced loading with ≥90% retention is the target | **Encoded, not validated** |
| Loading-aware frozen yield | 8.105–8.886%; identical across loadings for same catalyst/base | Yield model should respond to loading | **Underperformed** |

## Side products

| Predicted class | Example SMILES | Literature expectation | Assessment |
|---|---|---|---|
| Over-reaction | `COc1ccc(-c2ccc(C(F)(F)F)cc2)cc1Cl` | Poly-arylation is known | **Comparable** |
| Homocoupling | `COc1ccc(Oc2ccc(Cl)cc2)cc1` | Aryl-halide homocoupling is known | **Comparable** |
| Protodehalogenation | `COc1ccccc1` + `Cl` | Dehalogenation is known | **Comparable** |
| Demethylation | `Oc1ccc(Cl)cc1` | Less standard for Suzuki | **Lower plausibility** |

## Quantitative summary

| Metric | Observed value | Score meaning |
|---|---:|---|
| Top-1 exact product match | 1 / 1 | canonical identity |
| Forward model score | 1.0 | model confidence-like score |
| Forward feasibility | 0.9934252567071588 | model score |
| Forward candidate count | 30 | ranked list length |
| Conditions returned | 10 | 3 distinct yield values |
| Selected condition yield | 32.33824074268341% | native model field |
| Selected condition feasibility | 0.78 | native model field |
| Selected composite | 0.4813 | derived score × feasibility |
| Rejected nominal high yield | 47.446632385253906% | feasibility 0.20 |
| Order-sensitive invalid-run range | 22.066–77.420% | no catalyst/base |
| Parrot predictions | 15; top log score −1.3208 | log score |
| Pd-NHC design candidates | 8 of 8 Pd-NHC | heuristic scores 0.55/0.75 |
| Loading-aware candidates | 144 compiled; 8 recommended | loadings 0.5/2/5 mol% |
| Loading-aware frozen yields | 9 available, 8.105–8.886% | structure-based only |
| Match experimental yield / MAE / retention | null | withheld data unavailable |

## Overall comparison conclusion

Product prediction, side-product classes and Pd-NHC family generation matched general expectations. Retrosynthesis did not recover the exact supplied pair; internal and external condition tools returned generic chemistry where Pd-NHC specificity mattered. Loading was successfully encoded and varied, but the frozen yield advisor is blind to loading, so yield retention at reduced loading remains unestablished. No experimental superiority is claimed.
