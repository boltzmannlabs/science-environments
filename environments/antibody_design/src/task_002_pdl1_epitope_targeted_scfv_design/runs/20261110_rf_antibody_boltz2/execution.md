# Task 002 execution record

Run ID: `20261110_rf_antibody_boltz2`
Task: `task_002_pdl1_epitope_targeted_scfv_design`
Date represented by retained artifacts: November 10, 2026.

## Actual execution

1. Recovered the Germinal generic scFv framework and PD-L1 V-like target from the local Germinal snapshot.
2. Submitted the design-selected `epitope_abgen` branch. It returned no output after more than two hours; no downstream work was performed for that branch.
3. Used the completed `rfdiffusion_proteinmpnn` output as the executable fallback. The returned JSON contains 20 candidate records.
4. Prepared 10 explicit Boltz-2 YAML inputs and ran them sequentially with `recycling_steps=3` and `--use_msa_server`.
5. Parsed confidence JSON and mmCIF structures with Biopython. Measured PD-L1 hotspot contact pairs, contacted residues, minimum inter-chain distance and heavy-atom pairs below 2.4 Å.
6. Ranked the 10 evaluated candidates using the documented composite score.
7. Submitted the five-candidate shortlist to `Antibody_Prediction` with thermal stability, solubility and IMGT CDR prediction.
8. Packaged the shortlist and benchmark evidence under the paired results directory.

## Counts

| Quantity | Count |
|---|---:|
| RF-Antibody candidates returned | 20 |
| Candidates included in local Boltz-2 batch | 10 |
| Candidates with interface metrics | 10 |
| Candidates with Antibody_Prediction properties | 5 |
| Final shortlist records | 5 |
| Epitope-engaged recommendations | 4 |
| Contrast candidate | 1 (`rf0_d0`) |

## Stage status

| Stage | Status | Evidence |
|---|---|---|
| Workflow design | complete | `../../workflow.md`, `../../approaches.md` |
| `epitope_abgen` | pending/failed: no output | doc_id in `provenance.json`; `logs/platform_jobs.md` |
| `rfdiffusion_proteinmpnn` | complete | platform job manifest; `../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/raw/platform_outputs/rfantibody_candidates.json` |
| Sequence-level selection | complete for the evaluated 10 | explicit IDs in `../../code/boltz2_run_batch.sh` |
| Local Boltz-2 | complete for 10/10 | `../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/raw/platform_outputs/boltz2_analysis.json`, local logs |
| Interface/hotspot analysis | complete for 10/10 | `../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/raw/platform_outputs/boltz2_analysis.json` |
| Antibody_Prediction | complete for 5/5 shortlist records | `../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/raw/platform_outputs/antibody_pred_output.csv` |
| H5 benchmark | complete from retained reference run | paired results `../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/task002_h5_rmsd.json` |
| StaBddG | not applicable | mutation-ddG tool; no bound generic reference complex |

## Deviations and limitations

- The design-selected epitope-conditioned branch did not produce artifacts, so the final candidate set is from the whole-surface RF-Antibody fallback. Hotspot engagement is post-hoc, not a generation constraint.
- The remote platform payload implementation is not available locally. The job IDs, uploaded inputs, output records and statuses are retained; private backend code is not reconstructed.
- The platform property output is retained. No separate local thermal-stability or solubility predictor was run.
- The result package's flat task directory is the pre-existing scientific output location. This source run directory is the organized execution record and points to it rather than moving or overwriting those results.

## Canonical scientific results

- [Scientific report](../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/report.md)
- [Candidate inventory](../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/candidates.csv)
- [Selection table](../../../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/shortlist.csv)

The source run and scientific results share run ID `20261110_rf_antibody_boltz2`.
