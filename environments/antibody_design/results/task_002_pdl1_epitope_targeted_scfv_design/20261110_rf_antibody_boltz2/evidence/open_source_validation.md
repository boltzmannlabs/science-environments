# task_002 — Open-Source Tool Validation

## Tools and execution

| Tool | Version/source | Role | Status |
| --- | --- | --- | --- |
| Boltz-2 (open-source) | local install, `~/.boltz` checkpoints (boltz2.pt, boltz2_aff.ckpt) | Structure prediction of scFv+PD-L1 complexes; interface metrics | **COMPLETED** (10/10 candidates) |
| Biopython 1.84 | conda base | Interface analysis: hotspot contacts, clashes, geometry | **COMPLETED** |
| StaBddG (open-source) | conda env `stabddg` | Mutation ΔΔG prediction | **NOT APPLICABLE** — StaBddG predicts the ΔΔG of *mutations* in a *bound* reference complex; no bound generic-framework reference complex exists for this de novo design, so it cannot score absolute binding of the new candidates. Recorded as evaluated-but-not-run, not completed. |
| ProteinMPNN (open-source) | — | Sequence design | Not run standalone — ProteinMPNN is the sequence-design stage *inside* the platform `rfdiffusion_proteinmpnn` job (same model). Running it again standalone would duplicate, not validate, the generation. |

## GPU resource management

- Hardware: NVIDIA RTX 3090, 24 GB VRAM.
- Boltz-2 jobs were run **sequentially** (one complex at a time) in `scratch/boltz2_task002`, never in parallel, to avoid VRAM OOM. GPU occupancy was checked before the run (`nvidia-smi`: 1 MiB used / 24576 MiB at run start) — the GPU was idle, so no resource wait was required.
- No OOM events occurred. Per-complex prediction memory stayed within the 24 GB envelope.

## Open-source results vs Boltzmann platform predictions

### Structure / binding
The structure predictions were produced with **open-source Boltz-2** (the same model the platform exposes as `Boltz2`). Therefore the structural and interface metrics reported in `benchmark_comparison.md` (pTM, ipTM, pLDDT, iPLDDT, ipDE, hotspot contacts, clashes) are, by construction, consistent with what the platform `Boltz2` would produce for the same inputs — the comparison is not a discrepancy check between two different predictors, but a direct open-source execution of the platform model. This is disclosed explicitly rather than implied.

- Highest-confidence epitope-engaged complex: **rf1_d5** (ipTM 0.772, ipDE 3.06, 12 hotspot pairs, all 5 hotspots).
- Off-epitope high-confidence complex: **rf0_d0** (ipTM 0.813, ipDE 2.04, 0 hotspot pairs) — binds PD-L1 outside the declared epitope.

### Stability / developability
Thermal stability (ProtBERT, ESM) and solubility (ESM) were predicted with the **Boltzmann platform `Antibody_Prediction`** (doc_id `6af36e74d982f81aac5b4ec8`) for the 5 shortlist candidates. No separate open-source thermal-stability/solubility predictor was run locally (no validated local equivalent was available in this environment); these property values are therefore platform-only and are labeled as such. This is a limitation of the cross-validation, not an omission of a completed step.

### Agreement summary
| Metric | Source | Value (rf1_d5) | Cross-validation |
| --- | --- | ---: | --- |
| pTM / ipTM | open-source Boltz-2 | 0.888 / 0.772 | platform Boltz2 = same model (consistent by construction) |
| ipDE | open-source Boltz-2 | 3.06 | same model |
| Hotspot engagement | open-source Boltz-2 + Biopython | 5/5 (12 pairs) | geometry-based, independent of predictor |
| Thermal stability (ProtBERT/ESM) | platform Antibody_Prediction | 46.83 / 79.44 | platform-only (no local equivalent run) |
| Solubility (ESM) | platform Antibody_Prediction | 1 | platform-only |

## Reference benchmark cross-check

- H5 reconstruction (Boltz-2, open-source): 14.94 Å Cα RMSD vs 35TL, against the Germinal-published 1.25 Å (different predictor — see `benchmark_comparison.md` §1 for interpretation).
- Shortlist CDR3-H novelty vs H5: 6.9–27.6% identity (novel; below the paper's ~40% dataset-level figure).

## Reproducibility
- Boltz-2 run script and per-candidate inputs: `scratch/boltz2_task002/` (run_batch.sh, per-candidate YAML).
- Interface analysis script: `scratch/boltz2_task002/analyze.py`.
- All shortlist structures (CIF) are in `structures/`; confidence JSONs and the analysis are in `evidence/metrics_new.json`.
