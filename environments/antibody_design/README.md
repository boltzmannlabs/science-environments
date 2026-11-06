# Antibody Design

A scientific environment for antibody discovery, design, optimization and evaluation with Agent-Scientist. It brings together explicit scientific tasks, task-specific benchmarks and a common structure for agent implementations, execution scripts, specialized skills and reproducible results.

The environment's development scope covers **monoclonal, bispecific and multispecific antibodies**, including **de novo design and optimization of existing antibodies**. The [environment specification](ENVIRONMENT_SPEC.md) defines the scientific requirements guiding these capabilities.

## Scientific Scope

| Area | Design focus |
| --- | --- |
| Monoclonal antibody design | Target-directed candidate design, reference-guided refinement, epitope recognition and structural assessment. |
| Bispecific antibody design | Two intended binding specificities, with evaluation of each component and the assembled molecule. |
| Multispecific antibody design | Three or more intended binding specificities, with attention to component compatibility and overall architecture. |
| De novo design | Candidate discovery from a defined target and design objective, using an optional framework or scaffold. |
| Antibody optimization | Interaction quality, specificity, humanization, developability and molecular architecture, guided by declared constraints. |
| Reconstruction and benchmarking | Controlled comparisons of sequence recovery, structural agreement and other task-defined endpoints. |

Tasks specify the molecular format and representation appropriate to their objective, including paired-chain antibodies, fragments, scFv constructs and other architectures described in the specification.

## Environment Organization

| Directory | Purpose |
| --- | --- |
| [tasks/](tasks/) | Scientific task definitions describing objectives, required inputs, design constraints and expected outputs. |
| [benchmark/](benchmark/) | Corresponding task benchmarks with published metrics, reference values and comparison guidance. |
| [src/](src/) | Planned Agent-Scientist specialist definitions and environment implementation for antibody design. |
| [scripts/](scripts/) | Planned execution scripts that provide explicit operations for the agent, including input preparation, workflow execution and result collection. |
| [skills/](skills/) | Planned specialized agent skills for task interpretation, scientific reasoning, workflow planning and evidence reporting. |
| [tests/](tests/) | Planned validation resources for environment components and task requirements. |
| [results/](results/) | Planned release of candidate records, evaluation summaries and reproducible run artifacts. |

## Tasks and Benchmarks

The current release provides five monoclonal antibody task specifications, each paired with its own benchmark document. Tasks define the work assigned to Agent-Scientist; benchmarks define the evidence used to assess its outputs.

| Task | Design objective | Benchmark |
| --- | --- | --- |
| [001 — HER2](tasks/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md) | Trastuzumab interaction optimization. | [Metrics and reference values](benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md) |
| [002 — PD-L1](tasks/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md) | Epitope-targeted scFv design. | [Metrics and reference values](benchmark/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md) |
| [003 — PD-1](tasks/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md) | Framework-guided CDR design. | [Metrics and reference values](benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md) |
| [004 — LCAT](tasks/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md) | Reference Fab CDR-H3 reconstruction. | [Metrics and reference values](benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md) |
| [005 — Gal-3BP](tasks/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement.md) | Glycan-aware antibody interface refinement. | [Metrics and reference values](benchmark/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement.md) |

## Using the Environment

Start with a task's objectives, inputs and constraints, then consult its matching benchmark for metric definitions and comparison conditions. Keep candidate results attributable to their inputs and evaluation methods, and distinguish computational estimates from experimental measurements.

The [environment specification](ENVIRONMENT_SPEC.md) describes the full development scope. [Models and tools](MODELS_AND_TOOLS.md) explains capability requirements and selection criteria, while [status.md](status.md) summarizes current availability and upcoming work.
