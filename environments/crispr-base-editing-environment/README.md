# CRISPR Base-Editing Guide Design Environment

This environment describes a reusable workflow for designing and prioritizing base-editing guide RNAs for supported genetic targets.

## Contents

- `ENVIRONMENT_SPEC.md` — environment purpose, supported scope, workflow, tool contracts and output requirements.
- `config/tool_profile.json` — known tool and sequence-format settings supplied for this environment.
- `tasks/base_editing_grna_001.md` — reusable task definition and user inputs.
- `tests/ACCEPTANCE.md` — checks required before the workflow is considered implemented.

## Current scope

The supplied design interface scans exonic regions for 20-nt protospacers with NGG PAMs. It supports ABE and CBE modes with editor-specific windows. Prediction tools take 50-nt FASTA records in the specified flank/guide/PAM layout. Bowtie is used for reference-genome sequence-match screening when a matching index is available.

Tool support varies by organism, editor subtype and cell type. Record the selected reference and tool settings for each run. A result of `NO_COMPATIBLE_GUIDES` applies only to the configured search scope.
