# Task 005 code inventory

These files are organized copies of the scripts used or retained for the task. The original flat files remain one directory above for backward compatibility.

| File | Role | Main inputs | Main outputs |
|---|---|---|---|
| `03_design_cdrh3.py` | Identify VH CDR-H3 and create fixed-position map for ProteinMPNN | Prepared BDBV-43 Fab PDB | Fixed-position JSONL and ProteinMPNN design invocation |
| `04_prepare_struct.py` | Parse ProteinMPNN output, deduplicate CDR-H3 designs, create reference/candidate complex FASTAs | ProteinMPNN FASTA and LGALS3BP sequence | Prepared reference/candidate FASTAs |
| `05_interface_metrics.py` | Parse Boltz2 PDB/confidence outputs and calculate matched interface metrics | Boltz2 model-0 PDBs and confidence JSON | Interface metric JSON |
| `06_glycan_aware.py` | Approximate BACK-domain glycan occlusion and antibody clash count | Reference complex PDB | Glycan-aware analysis JSON |
| `07_prodigy_validate.py` | Run Prodigy and parse affinity/contact estimates | Reference/candidate complex PDBs | Prodigy validation JSON |
| `08_consolidate.py` | Join interface, Prodigy and glycan outputs and write final tables | Evidence JSON files | `candidates.csv`, `metrics.json`, `benchmark_comparison.csv` |

## Reproducibility note

The copied scripts preserve the paths and assumptions of the historical execution, including paths under `/home/boltzmann10/shared_metric_tools` and the task results directory. They are an execution record, not yet a portable package. Before rerunning on another machine, replace absolute paths, verify tool versions and re-check the input files.

The glycan script is explicitly approximate: it creates a simplified 12-sugar coordinate model at Asn362 and uses the BACK domain as an E1 proxy because the paper's exact E1 residue mapping was unavailable.
