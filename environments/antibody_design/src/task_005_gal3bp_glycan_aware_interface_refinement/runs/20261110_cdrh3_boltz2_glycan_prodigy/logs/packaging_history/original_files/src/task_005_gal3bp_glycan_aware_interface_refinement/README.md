# Task 005 source package — Gal-3BP glycan-aware interface refinement

This directory contains the task-level workflow, code inventory, source provenance and execution record. Scientific outputs remain under the paired results directory.

## Task and run identifiers

- Task: `task_005_gal3bp_glycan_aware_interface_refinement`
- Run: `20261110_cdrh3_boltz2_glycan_prodigy`
- Canonical run results: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/`
- Legacy flat results preserved under `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/evidence/legacy_flat/`
- General source/results contract: `../../SRC_AND_RESULTS_GUIDE.md`

## Directory structure

```text
src/task_005_gal3bp_glycan_aware_interface_refinement/
├── README.md                    # this entry point
├── approaches.md                # compared workflows and selection rationale
├── workflow.md                  # selected workflow and actual stage graph
├── SOURCES.md                   # scientific/tool sources and limitations
├── code/                        # code used or retained from the execution
│   ├── 03_design_cdrh3.py
│   ├── 04_prepare_struct.py
│   ├── 05_interface_metrics.py
│   ├── 06_glycan_aware.py
│   ├── 07_prodigy_validate.py
│   ├── 08_consolidate.py
│   └── README.md
├── configs/
│   └── evaluation_thresholds.json
├── sources/
│   └── source_manifest.json
└── runs/
    └── 20261110_cdrh3_boltz2_glycan_prodigy/
        ├── execution.md
        ├── provenance.json
        ├── inputs/
        ├── configs/
        └── logs/
```

The older flat scripts (`design_cdrh3.py`, `prepare_struct.py`, `interface_metrics.py`) are retained for backward compatibility. The numbered copies under `code/` are the organized code inventory for this task.

## Workflow followed

1. Verify BDBV-43 from PDB 7KEW and LGALS3BP from UniProt Q08380.
2. Use BDBV-43 as a paired VH/VL reference scaffold.
3. Protect the framework, VH CDR-H1/H2 and all VL residues; design only VH CDR-H3.
4. Generate 20 local ProteinMPNN designs and retain 17 unique designs.
5. Select cand11, cand7 and cand17 for structure prediction.
6. Predict full-length LGALS3BP complexes with Boltz2 for the reference and three candidates.
7. Compute matched interface metrics using the thresholds in `configs/evaluation_thresholds.json`.
8. Approximate the E1 region by BACK-domain residues 260-360 and evaluate a simplified glycan at Asn362.
9. Run Prodigy on antibody chains A/B versus antigen chain C.
10. Consolidate candidate metrics, benchmark caveats and ranking into the results package.

The selected workflow was an AntiBMPNN-style protected-framework design. The platform AntiBMPNN submission itself was not completed because its partial-validation approval prompt timed out. Therefore the executed candidate set uses the retained local ProteinMPNN designs; no unexecuted platform output is claimed.

## Main results

- cand17 ranked first overall by the combined retained evidence: Prodigy ΔG `-14.5 kcal/mol`, Kd `2.3e-11 M`, 102 intermolecular contacts, Boltz2 ipTM `0.485`.
- cand11 had the highest Boltz2 ipTM `0.554` and the largest Cα-defined interface extent, 59 residue pairs.
- cand7 was retained as a lower-confidence comparison.
- BACK-domain glycan-associated ΔSASA was `34.2 Å²` for the simplified single-glycan approximation; glycan-antibody clashes were `0` under the recorded threshold.
- The paper's 161/165 interaction counts, ~67% H-bond share, 5 Å heated-MD boundary and 2.9 Å² E1 ΔSASA are not like-for-like reproducible with the available inputs.

## Execution status

Completed: input verification, workflow comparison, local ProteinMPNN candidate set, Boltz2 structures, interface metrics, approximate glycan analysis, Prodigy cross-check and packaging.

Pending or blocked: platform AntiBMPNN approval/submission, Antibody_Prediction developability metrics, heated-MD interface stability and exact paper benchmark reproduction.

## Where to read the results

- Human-readable result report: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/report.md`
- Candidate inventory: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/candidates.csv`
- Shortlist: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/shortlist.csv`
- Machine-readable metrics: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/metrics.json`
- Benchmark comparison: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/benchmark_comparison.csv`
- Structures: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/structures/`
- Validation: `../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/20261110_cdrh3_boltz2_glycan_prodigy/evidence/validation.json`
- Execution record: `runs/20261110_cdrh3_boltz2_glycan_prodigy/execution.md`
- Provenance: `runs/20261110_cdrh3_boltz2_glycan_prodigy/provenance.json`
