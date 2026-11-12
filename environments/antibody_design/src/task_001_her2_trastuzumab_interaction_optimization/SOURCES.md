# Task 001 — Sources, Inputs, Tools and Provenance

This file records the actual sources and execution artifacts used for
`task_001_her2_trastuzumab_interaction_optimization`.

## Task and benchmark sources

| Purpose | Source |
| --- | --- |
| Task definition | `tasks/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md` |
| Published benchmark definition and values | `benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md` |
| Reference complex | PDB 1N8Z, deposited trastuzumab Fab + human HER2 extracellular domain |
| Reference structure used locally | `/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science_env_results/her2_results/1N8Z_deposited_complex.pdb` |
| Reference chain interpretation | Chain A = VL, chain B = VH, chain C = HER2 |
| Results package | `results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/` |
| Task-spec bundle | `/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science_env_results/her2_results/` |

The benchmark source reports REF15 interaction scores in Rosetta energy units
(REU). REF15 was not recomputed because Rosetta was unavailable. ProDIGy values
in the results package are a separate, non-comparable metric.

## Boltzmann tools used

### 1. AntiBMPNN — candidate generation

- Provider: Boltzmann platform tool / NodeAPI.
- Tool: `AntiBMPNN`.
- Local output directory:
  `/home/boltzmann10/.sci/workspace/outputs/antibmpnn_results/`
- Job name: `AntiBMPNN - 20261110-151953Z - cbb255`.
- Experiment ID: `6af3361ad982f81aac5b4a52`.
- Model: `antibmpnn_020`.
- Generation count: 20.
- Sampling temperature: 0.1.
- Backbone noise: 0.0.
- Seed: 37.
- Designed chains: A and B.
- Fixed chain: C (HER2).
- Designed chain A positions: 24–34, 50–56 and 89–97.
- Designed chain B positions: 26–32, 50–65 and 97–109.
- Primary outputs:
  - `antibmpnn_results.csv`
  - `antibmpnn_generation_metrics.csv`
  - `run_manifest.json`
  - `logs/01_parse_pdbs.log`
  - `logs/02_antibmpnn.log`
  - `antibmpnn_artifacts/`

### 2. Antibody_Prediction — stability and solubility

- Provider: Boltzmann platform tool.
- Evaluated records: `REF_1N8Z`, `AB_08`, `AB_20`, `AB_04`, `AB_05`, `AB_13`.
- Local raw output retained in the results run: `results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/evidence/raw/task001_antibody_pred_output.csv`.
- Parsed output retained in the results run: `results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/evidence/raw/task001_props_parsed.csv`.
- Reported fields:
  - `Thermal_stab_protbert`
  - `Thermal_stab_esm`
  - `solubility`

### 3. Boltz2 — structure prediction

- Provider: Boltzmann platform tool.
- Payload generator: `src/task_001_her2_trastuzumab_interaction_optimization/code/03_boltz2_payloads.py`.
- Payload records: `REF_1N8Z`, `AB_08`, `AB_20`, `AB_04`, `AB_05`, `AB_13`.
- Each payload contained VH, VL and HER2 protein sequences.
- Reference artifacts retained locally:
  - `/home/boltzmann10/.sci/workspace/outputs/ref_pdbs.zip`
  - `/home/boltzmann10/.sci/workspace/outputs/ref_outputs.zip`
  - `/home/boltzmann10/.sci/workspace/outputs/ref_paths.csv`
  - `/home/boltzmann10/.sci/workspace/outputs/ref_bundle/`
- Reference confidence used in the report:
  - VH–VL: confidence 0.96, ipTM 0.955, complex pLDDT 0.961, ipDE 0.46.
  - VH–HER2: confidence 0.777, ipTM 0.245, complex pLDDT 0.910, ipDE 15.87.
- Candidate Boltz2 jobs were submitted, but candidate signed-download artifacts
  were not recovered because the 300-second signed-URL lifetime was exceeded by
  inter-call latency. Candidate Boltz2 structures are therefore not claimed as
  completed outputs.

## Open-source tools used

### ProDIGy

- Executable: `/home/boltzmann10/anaconda3/bin/prodigy`.
- Version: use the installed executable in the conda base environment; the exact
  package version was not separately recorded in the original run.
- Selection: `--selection "A,B" C`.
- Interpretation: Fab chains A+B versus HER2 chain C.
- Outputs: binding affinity in kcal/mol, predicted KD at 25 °C, intermolecular
  contact count.
- Reproducibility wrapper:
  `src/task_001_her2_trastuzumab_interaction_optimization/code/06_run_prodigy.sh`.

### Biopython and NumPy

- Used for PDB parsing, chain/residue mapping, fixed-pose reconstruction,
  structure writing and clash counting.
- Executed with `/home/boltzmann10/anaconda3/bin/python`.
- The conda environment contained Biopython 1.84 and NumPy.

## Derived inputs and intermediate records

The following working files were used during execution and are retained in the
Sci workspace scratch area:

- `/home/boltzmann10/.sci/cache/scratch/task001_candidates.json`
- `/home/boltzmann10/.sci/cache/scratch/task001_shortlist.json`
- `/home/boltzmann10/.sci/cache/scratch/task001_seqs.json`
- `/home/boltzmann10/.sci/cache/scratch/task001_boltz2_payloads.json`
- `/home/boltzmann10/.sci/cache/scratch/task001_checkmap.py`
- `/home/boltzmann10/.sci/cache/scratch/task001_filter.py`
- `/home/boltzmann10/.sci/cache/scratch/task001_select.py`
- `/home/boltzmann10/.sci/cache/scratch/task001_reconstruct.py`
- `/home/boltzmann10/.sci/cache/scratch/task001_clashes.py`
- `/home/boltzmann10/.sci/cache/scratch/task001_assemble.py`
- `/home/boltzmann10/.sci/cache/scratch/task001_bundle.py`

The reproducible copies of the execution scripts are in this task's `code/`
directory. The scratch paths are retained as provenance, not as the primary
source location.

## Reference sequences

The reference VH and VL sequences were extracted from the first 120 standard
residues of 1N8Z chain B and first 107 standard residues of chain A.

- VH: `EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS`
- VL: `DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK`

The candidate-to-structure mapping was verified as 1:1 for the variable-domain
regions: candidate VH position i maps to 1N8Z chain-B residue i; candidate VL
position i maps to 1N8Z chain-A residue i.

## Historical comparison source

The task folder contains `evidence/historical_proteinmpnn_cdrh3/`. Those files
come from an earlier ProteinMPNN CDR-H3-only run and are retained as historical
comparison evidence. They are not the selected AntiBMPNN all-CDR result.
