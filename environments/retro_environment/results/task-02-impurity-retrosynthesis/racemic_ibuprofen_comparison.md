# Recovered racemic-ibuprofen execution and exact reference comparison

Recovered from prior retro_case chat and on-disk records, read-only. This is an executed historical computational run, not a newly submitted job or a physical synthesis. [Sanitized full derivative](racemic_ibuprofen_recovered.json) retains seven original route IDs and all 25 step comparisons, plus SHA-256 fingerprints of source audit/comparison files. No other profile was modified and raw account exports are not published.

Target: supplied parent racemic ibuprofen SMILES `CC(C)Cc1ccc(cc1)C(C)C(=O)O`, PubChem CID 3672. Historical report records RDKit-equivalent root connectivity. Unassigned stereochemistry matches the intended unspecified racemate input but is not an observed 1:1 enantiomer ratio or measured physical-form confirmation.

| Route | Total transformation occurrences | Longest linear sequence | Comparison in inspected literature |
|---|---:|---:|---|
| top0 | 4 | 4 | No exact comparator established |
| top1 | 4 | 4 | No exact comparator established |
| top2 | 5 | 5 | No exact comparator established |
| top3 | 2 | 2 | One carbonate alpha-carbethoxylation analogy; one indirect multi-operation analogy to Boots |
| top4 | 2 | 2 | No exact comparator; one missing listed oxygen-source flag |
| top5 | 6 | 5 | No exact comparator established; branched total differs from linear count |
| top6 | 2 | 2 | No exact comparator established |

## Primary-source comparator mapping recovered from historical review

- [US3385886A, Example 4](https://patents.google.com/patent/US3385886A/en): ester alpha-carbethoxylation and subsequent separately described transformations; patent states 4-isobutyl analogue prepared similarly. Model top3 substrate already has alpha-methyl and differs from the example. Its diester-to-acid arrow compresses multiple literature operations. Thus one analogous step and one indirect comparison, not exact complete route reproduction.
- [EP0337803A1](https://patents.google.com/patent/EP0337803A1/en): ibuprofen process via para-isobutylacetophenone/aryl ethanol and carbonylation. None of the seven model routes reproduces the full target-forming aryl-ethanol carbonylation.
- [US5166418A](https://patents.google.com/patent/US5166418A/en): aryl-substituted alcohol/carbon monoxide ibuprofen process. Same absence of complete model carbonylation comparator; do not combine Boots and carbonylation sequences.

25 recovered step comparisons: zero exact matches in the inspected source set, one analogous transformation, one indirect multi-operation analogy and 23 not assessed across the full literature. This is not a global negative literature verdict. No independent forward, atom-mapping, condition-recommendation or impurity-prediction service was executed in that historical run. Model-internal scores remain model outputs; no measured isolated yield, purity, process cost or superiority is established. The two impurity A/M cases remain separate (19 paths/59 nodes); these seven parent routes must not be counted inside their totals.

[Task](../../tasks/task-02-impurity-retrosynthesis/README.md) · [Benchmark](../../benchmark/task-02-impurity-retrosynthesis/README.md) · [Results](README.md)
