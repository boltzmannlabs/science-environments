# pH-dependent antigen binding and release

**Status: Specification (draft).**

This package organizes the shared computational environment and its existing antibody case-study tasks. Read [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md), then the selected [task](tasks/README.md). The workflow completes relevant modeling and static assessments before simulations assess the selected systems. The task controls the molecular context, pH conditions and required calculations.

## Package structure

```text
ph_dependent_ag_release/
├── ENVIRONMENT_SPEC.md
├── MODELS_AND_TOOLS.md
├── README.md
├── STATUS.md
├── benchmark/
├── config/
├── results/
├── scripts/
├── src/
├── tasks/
└── tests/
```

The directory names and capitalization match the supplied enzyme-environment template. `config/` and `results/` contain only `.gitkeep` placeholders so Git preserves the reserved directories. The guide specifies no preset candidate, finalist or replica counts. Existing tasks retain their own mandatory conditions and sampling requirements.

## Working with the tasks

Run from the environment root and save generated artifacts under the selected task's `results/<task_id>/<run_id>/` directory. Choose suitable open-source or eligible academic/noncommercial implementations, verify their licenses and capabilities, and record actual versions and native outputs. This package does not prescribe a scientific execution backend.

Supply a verified external input-only bundle before running Task 001; its task file lists the required filenames. Other tasks also require verified molecular inputs to be supplied or recovered from permitted authoritative records. Record each bundle location and input hash in the run manifest. Read each task's input-access rules before discovery. The package does not contain source papers, expected numerical answers or historical calculation results. Keep independent evaluator material outside the execution context until outputs are frozen.

`benchmark/`, `config/`, `results/`, `scripts/`, `src/` and `tests/` are reserved with `.gitkeep` placeholders. No runtime controller, package validator, automated scientific tests or benchmark data are included. The specification describes the intended execution and evidence contracts; those contracts are not implemented software interfaces yet.

## Review and execution status

Structural review covers directory names, document links, task input/output contracts and absence of machine-specific paths. This is documentation review, not evidence of scientific execution.

Before execution, supply the task's verified molecular inputs, choose suitable licensed implementations, freeze their versions and settings, and establish a working route from each invocation to its requested observable. Record missing prerequisites explicitly. No model inference, production simulations or numerical benchmark comparisons have been performed as part of packaging this environment.
