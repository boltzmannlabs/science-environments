# Hit identification

Scientific tasks for identifying and prioritising small-molecule hits from supplied libraries. The agent selects its approach and supports recommendations with retained evidence.

Status: draft specification and validated inputs; scientific execution and runtime qualification remain separate.

| Task | Target | Inputs |
| --- | --- | --- |
| [task_001](tasks/task_001_d2r_peripheral_candidate_prioritisation.md) | Human dopamine D2 receptor | 400 source records, experimental receptor structures, sequences and reference controls |

Run the selected task from this environment directory: its `inputs/...` paths resolve here. Give the execution agent the selected task and `inputs/` only. Do not include owner-only `benchmark/` metadata or source-paper outcomes.

The primary receptor input is the original 6CM4 crystal complex. No prebuilt reconstruction is supplied. The task requests eight ranked candidates, two final priorities and a detailed report. It prescribes no tools or scientific stages and has no Description or Evaluation section.

Owner provenance: [benchmark metadata](benchmark/task_001_d2r_peripheral_candidate_prioritisation.md). Source DOI 10.1371/journal.pone.0355997, PMC13524263. These identify the source for maintainers; they are not execution instructions.

Validate files and configuration with `python scripts/validate_environment.py`. Tests run with `python -m pytest tests`.
