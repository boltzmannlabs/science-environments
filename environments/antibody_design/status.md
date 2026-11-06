# Antibody Design Status

**Maturity:** Specification

## Current Contents

| Component | Status |
| --- | --- |
| Monoclonal tasks | Five benchmarked prompts and two restored fixed-framework VHH prompts in `tasks/monoclonal_antibody_design/`. |
| Bispecific tasks | One design prompt and four evidence-assessment prompts. |
| Benchmarks | Ten matching documents with metrics, available reference values and task-specific interpretation. |
| Configuration | Shared schemas and nine contract profiles: four retained monoclonal profiles and five active bispecific profiles. |
| Validation | Contract validators and regression tests under `tests/`; retired prompts remain in `tests/fixtures/retired_tasks/`. |
| Source, scripts and skills | Each folder contains only `readme.md`. No specialist implementation is included. |
| Results | A missing-input example and a stored specification-validation report. No completed antibody-design run is supplied. |

## Validation Scope

Existing checks assess schemas, declarations, provenance and output consistency. They do not establish the scientific performance of the twelve task documents. The seven current monoclonal prompts have no dedicated executable profiles or automatic scientific graders. The restored VHH prompts are registered under `fixed_framework_tasks`; validation checks their identities, required sections and catalog membership.

The stored validation report is historical and was not regenerated for the documentation changes. Documentation checks cover local links, folder descriptions and task/benchmark correspondence; they are separate from scientific execution.

## Remaining Implementation

Scientific execution requires configured external tools, verified task inputs, task-compatible output validation and independent evaluation. Published benchmark measurements and agent-reported observations retain their stated evidence scope.

See the [environment specification](ENVIRONMENT_SPEC.md), [task overview](README.md) and [benchmark index](benchmark/README.md).
