# MD benchmark catalogue

This directory holds the frozen, package-local inputs and published-protocol
reconstruction tasks used by the MD specialist
agent packets. It intentionally separates inputs from `results/`, which holds
execution and evaluation evidence.

## Benchmark catalogue

| Location | Information |
| --- | --- |
| [`PAPER_CATALOGUE.md`](PAPER_CATALOGUE.md) | Published studies and scope. |
| [`paper_manifest.json`](paper_manifest.json) | Machine-readable case and input manifest. |
| [`protocol_targets.json`](protocol_targets.json) | Required protocol fields and provenance targets. |
| `MD-PAPER-*/` | One README, paper reference, and task card per study. |
| `fixtures/` | Frozen structures, trajectories, records, and faults. |
| `../src/cases/` | Molecular structures, requests, and materialized agent packets. |

| Task card | Reproduction target |
| --- | --- |
| [task_001_villin_headpiece.md](task_001_villin_headpiece.md) | Villin folding setup and observables |
| [task_002_barnase_barstar.md](task_002_barnase_barstar.md) | Barnase–barstar interface dynamics |
| [task_003_dna_duplex.md](task_003_dna_duplex.md) | DNA duplex preparation and helical analysis |

Research-paper reconstruction benchmarks are catalogued in
[`PAPER_CATALOGUE.md`](PAPER_CATALOGUE.md), with one packet per study and a
machine-readable [`paper_manifest.json`](paper_manifest.json). Run
`python scripts/validate_paper_benchmark.py` to verify packet structure and
input hashes before an agent benchmark. A preflight result is written under
`results/`; `REVIEW` is the default until paper-matched trajectories,
observables, and uncertainty evidence are available.

Run the comparable configurations with `python scripts/run_paper_benchmark.py`.
The `general`, `specialist`, and `orchestrated` configurations are scored on
protocol-field coverage, provenance, and explicit missing-value handling. The
score measures setup reconstruction, not scientific reproduction.
The contract gate is expected to pass for all three configurations; scientific
qualification remains a separate `REVIEW` gate until trajectory evidence exists.

- `fixtures/structures/` contains coordinate files, topology snippets, and
  ligand structures.
- `fixtures/trajectories/` contains bounded trajectory inputs for analysis and
  failure tests.
- `fixtures/records/` contains protocol, observable, provenance, and reference
  records.
- `fixtures/failures/` contains deterministic recovery and infrastructure fault
  fixtures.

All paths are package-relative and are recorded in `inputs/MD-*/task.json`.
Fixtures support structural and adapter validation only; their presence does
not establish a scientific PASS.
