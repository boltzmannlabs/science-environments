# De Novo Enzyme Design

An Agent-Scientist environment for end-to-end de novo enzyme design, from a specified substrate-to-product conversion to generated enzyme candidates and computational evaluation of their structure, protein properties and reaction chemistry. The scope covers soluble, cofactor-free monomers and homodimers, including assembly-aware catalytic-site and chemical-step assessment.

**Status: In Progress.** The execution controller and evidence contracts are implemented; reaction-specific methods and complete scientific qualification require validation.

## Environment structure

```text
Denovo-Enzyme-Design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── config/
├── tasks/
├── runs/
├── results/
├── benchmark/
├── scripts/
├── src/
└── tests/
```

| Location | Information |
| --- | --- |
| [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md) | Scientific scope, end-to-end workflow, catalytic constraints, reaction-state preparation, chemistry evaluation and qualification criteria. |
| [STATUS.md](STATUS.md) | Implemented work, current limitations and validation requirements. |
| [MODELS_AND_TOOLS.md](MODELS_AND_TOOLS.md) | Required scientific capabilities, execution policy and tool-selection requirements. |
| [config/](config/) | Environment policy, schemas under `schemas/`, and shared request examples under `shared/`. |
| [tasks/](tasks/README.md) | Stable scientific task definitions organized by task ID. |
| [runs/](runs/) | Execution records and run-specific workflow documentation, organized by task and run ID. |
| [results/](results/) | Scientific outputs and result records organized by the same task and run IDs. |
| [benchmark/](benchmark/) | Benchmark definitions and reference data; benchmark execution outputs remain with their corresponding results. |
| [scripts/](scripts/) | Controller launch, resume, status and package-validation entry points. |
| [src/](src/) | Shared workflow code, agent instructions and runtime/evidence contracts. |
| [tests/](tests/) | Technical and scientific validation resources. |

## Prerequisites and start

Use an available SCI installation, a configured execution harness and access to the required scientific capabilities. Copying this environment does not configure services or authorize scientific submissions.

1. Read the selected task, [environment specification](ENVIRONMENT_SPEC.md) and [tool policy](MODELS_AND_TOOLS.md).
2. Resolve the reaction, assembly and available reference inputs; prepare the stage-specific molecular inputs and record the evaluation conditions and resource limits.
3. Initialize a new controller run using the [runtime contracts](src/CONTRACTS.md), then record execution metadata under `runs/<task-id>/<run-id>/` and outputs under `results/<task-id>/<run-id>/`.

## Evaluation and results

The environment treats folding, assembly, solubility, aggregation, substrate placement and reaction chemistry as separate evidence requirements. Full qualification includes the required chemical steps, with reaction-path or free-energy assessment, controls, convergence checks and uncertainty. The detailed procedures are defined in the specification rather than repeated here.

Return traceable sequences, structures, measurements, chemistry evidence, exclusions and requested-versus-qualified counts. Missing required evidence remains unresolved. Published computational results are the initial benchmark targets; experimental measurements remain separate supporting context.

Supporting literature is recorded in the [research notes](../../research/Denovo-Enzyme-Design/research-notes.md) and [references](../../research/Denovo-Enzyme-Design/references.md). Repository [contribution guidance](../../CONTRIBUTING.md) and [licensing](../../LICENSE) continue to apply.
