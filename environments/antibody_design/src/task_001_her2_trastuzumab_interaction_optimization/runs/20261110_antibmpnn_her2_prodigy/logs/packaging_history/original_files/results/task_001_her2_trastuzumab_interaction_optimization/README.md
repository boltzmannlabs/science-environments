# task_001_her2_trastuzumab_interaction_optimization

This task contains one normalized execution run:

```text
20261110_antibmpnn_her2_prodigy/
```

Scientific run package:

- `20261110_antibmpnn_her2_prodigy/report.md`
- `20261110_antibmpnn_her2_prodigy/candidates.csv` — all 20 generated candidates.
- `20261110_antibmpnn_her2_prodigy/shortlist.csv` — five selected candidates.
- `20261110_antibmpnn_her2_prodigy/designed_sequences.fasta`
- `20261110_antibmpnn_her2_prodigy/metrics.json`
- `20261110_antibmpnn_her2_prodigy/benchmark_comparison.csv`
- `20261110_antibmpnn_her2_prodigy/structures/`
- `20261110_antibmpnn_her2_prodigy/evidence/`

## Result summary

AntiBMPNN generated 20 paired trastuzumab-derived VH/VL variants. All 20 passed framework and disulfide-preservation checks. Five were shortlisted: AB_13, AB_05, AB_20, AB_08 and AB_04.

**Best computational candidate: AB_13**

- ProDIGy ΔG: −10.9 kcal/mol versus reference −9.9.
- Predicted KD: 9.4e−9 M versus reference 5.6e−8 M.
- Interface contacts: 68.
- Clashes: 27 versus reference 26.
- ProtBert thermal-stability score: 52.4.

The binding result is directional only. ProDIGy is not comparable to the published REF15 Rosetta REU benchmark, and REF15 was not computed because Rosetta was unavailable.

## Source execution record

The workflow, code, inputs and provenance are under:

```text
../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/
```

The source-side task package is:

```text
../../src/task_001_her2_trastuzumab_interaction_optimization/
```

Validation: `20261110_antibmpnn_her2_prodigy/evidence/validation.json`.
