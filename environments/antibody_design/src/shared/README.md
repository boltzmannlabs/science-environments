# Shared Code and Transfer Records

This directory supports the five existing HER2, PD-L1, PD-1, LCAT and Gal-3BP packages. The import is based on upstream `main` commit `ba3232c0480ba3e6fd516712d36ed2d93adf9414`. No task or benchmark definition was changed; unrelated upstream task/result files remain intact.

## Shared Implementations

`prepare_inputs.py`, `run_proteinmpnn.py`, `run_boltz2.py` and `metrics.py` are retained historical helpers. Their original paths and runtime assumptions may require configuration before reuse. They are not a ready-to-run general executor. In particular, `metrics.py` contains a custom local-distance function whose thresholds differ from standard lDDT; the LCAT report records its scope.

`validate_packages.py` performs packaging checks only. Run from the repository root:

```bash
python environments/antibody_design/src/shared/validate_packages.py
```

It validates task/result links, candidate membership, exported FASTA coverage, tables, JSON/JSONL, imported-file preservation and current integrity. It does not submit tools, install dependencies, deserialize pickles or assess affinity.

## Transfer Records

| File | Meaning |
| --- | --- |
| `import_context.json` | Original workspace, destination base and bounded transfer scope. |
| `import_manifest.csv` | Every imported original byte sequence, its original hash and current location. Edited metadata is retained unchanged under `import_history/original_files/`. |
| `artifact_relocations.csv` | Inputs and logs moved from results into matching source runs. |
| `omitted_files.csv` | Exact inventory of excluded caches, bulk downloads and unrelated upstream examples; originals were not deleted. |
| `external_artifacts.json` | Sizes and SHA-256 hashes of the excluded large archives. |
| `package_inventory.csv` | Fresh paths, sizes and SHA-256 hashes for finalized package files, excluding self-referential validation/inventory records. |
| `PACKAGE_REVIEW.md` | Scope, scientific limitations and local validation entry points for review. |
| `validation/` | Package-wide integrity report and readable summary; scientific run evidence remains under each results run. |

Historical checksum files and absolute paths describe the original execution. Use the fresh package inventory for the transferred layout. Run snapshots/tool inventories added during arrangement are explicitly retrospective and do not assert current endpoint availability.

## External Dependencies

The 4.10 GB Ab-SELDON archive and full AbFlow dataset download/tree remain in the original workspace. The contribution includes the extracted HER2 evidence, the RAbD 60-case test inputs and retained benchmark outputs, rather than the full training collections. Python bytecode, Foldseek temporary workspaces and unrelated Ab-SELDON example targets are excluded. Original scientific outputs and reported failures are preserved.

Ab-SELDON archive source: [Zenodo 15803983](https://doi.org/10.5281/zenodo.15803983); source/file metadata is retained in task 001's audit inputs. AbFlow dataset/checkpoint origin and checkpoint hash are recorded in task 004's provenance and `evidence/abflow_rabd_reproduction.json`. The downloaded bulk archive's verified byte identity is recorded here; code/weights and their original execution environments remain external dependencies.

The retained RAbD input JSONL contains original absolute PDB paths, and processed data may reference external source paths. Reproduction requires restoring the matching upstream dataset and code/checkpoint, configuring paths for the execution workspace and preserving the original test/chain/mask definitions. This import verifies packaging; it does not prove a fresh portable rerun.

Scientific raw measurements remain under results; commands, tool logs, inputs and configuration remain under source runs. The original workspace was preserved in place. No scientific jobs ran during transfer.

## Upstream Attribution

The original Ab-SELDON BSD 3-Clause license is retained with its inspected source revision under task 001's audit `inputs/benchmark_sources/Ab-SELDON.LICENSE`, with the source URL in the neighboring `.source.txt` file. Upstream material retains its own attribution and terms. Original run-specific data and third-party code provenance remain in source manifests and benchmark references.
