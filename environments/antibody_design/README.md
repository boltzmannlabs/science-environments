# Antibody Design

The `antibody_design` environment organizes antibody-design research into clearly defined tasks, input/output requirements, and validation criteria. The active tasks cover monoclonal antibody design with a supplied reference, scaffold or published comparator, and bispecific antibody design and evidence assessment.

## Task families

| Family | Description |
| --- | --- |
| Monoclonal antibody design | Five paper-based tasks for HER2, PD-L1, PD-1, LCAT and Gal-3BP, each with an identified reference antibody, scaffold or comparator. |
| Bispecific design | HER2 biparatopic design using zanidatamab as the reference, with domain II/domain IV assignments and evidence for each arm and the assembled molecule. |
| Bispecific assessment | Supplied evidence is assessed through cellular-mechanism, CNS-delivery, CNS-readout comparison, and integrated CNS-assessment tasks. |

## Folder structure

```text
antibody_design/
├── README.md                     # Environment overview
├── ENVIRONMENT_SPEC.md           # Detailed requirements and implementation status
├── MODELS_AND_TOOLS.md            # Model and tool reference documentation
├── status.md                     # Development status notes
├── config/                       # Configuration and machine-readable definitions
│   ├── environment.yaml          # Task catalog and profile mapping
│   ├── shared/                   # Common fields, protocol and metric definitions
│   ├── monoclonal_reference/     # Retained reference-guided contracts
│   ├── monoclonal_target_only/   # Retained target-only contract
│   ├── bispecific_design/        # Bispecific design configurations
│   └── bispecific_assessment/    # Cellular and CNS assessment configurations
├── tasks/                        # Task instructions only
│   ├── monoclonal_antibody_design/  # The five active monoclonal tasks
│   │   ├── mab_her2_reference_optimization.md
│   │   ├── mab_pdl1_epitope_design.md
│   │   ├── mab_pd1_epitope_design.md
│   │   ├── mab_lcat_cdr_design.md
│   │   └── mab_gal3bp_reference_design.md
│   ├── bispecific_design/        # One bispecific design task
│   └── bispecific_assessment/    # Four cellular and CNS assessment tasks
├── src/                          # README placeholder only
│   └── readme.md
├── scripts/                      # README placeholder only
│   └── readme.md
├── skills/                       # README placeholder only
│   └── readme.md
├── tests/                        # Validation code, fixtures, and automated checks
│   ├── monoclonal_antibody_with_reference/
│   └── fixtures/retired_tasks/   # Historical prompts used by existing tests
├── benchmark/                    # Mirrors tasks/ folders and filenames
│   ├── README.md                 # Task-to-benchmark index
│   ├── monoclonal_antibody_design/  # Five monoclonal benchmark documents
│   ├── bispecific_design/        # One biparatopic design benchmark
│   └── bispecific_assessment/    # Four evidence-assessment benchmarks
└── results/                      # Example outputs and validation reports
```

The tree shows the main files and directories.

- **`status.md`** summarizes current contents and remaining implementation work.
- **`ENVIRONMENT_SPEC.md`** defines the environment's scope, scientific requirements, evidence expectations, and current implementation boundaries.
- **`config/`** contains task profiles, request/result schemas, JSON input examples, and validation dependencies. Each family has its own configuration; common definitions are shared. See the [configuration guide](config/README.md).
- **`tasks/monoclonal_antibody_design/`** contains only the five current monoclonal tasks. Each defines the objective, reference context, constraints, evaluation criteria and expected outputs. The older reference/target-only prompt folders have been removed from `tasks/`.
- **`tests/`** contains all testing and validation code. The dedicated monoclonal suite covers a supplied antigen and reference antibody; shared checks validate configurations across all task families.
- **`benchmark/`** contains ten matching benchmark documents with metrics, available reference values and task-specific interpretation. The folders and filenames mirror `tasks/`. The [benchmark index](benchmark/README.md) maps every task to its reference document.
- **`src/`, `scripts/` and `skills/`** each contain one README placeholder. Specialist implementation, execution scripts and agent skills are not included in the current environment.
- **`results/`** holds small example outputs and generated validation summaries. Expected output formats are described in the [results guide](results/README.md).

Supporting [research notes](../../research/antibody_design/research-notes.md) and [references](../../research/antibody_design/references.md) are maintained separately under `research/antibody_design/` at the repository root.

## Monoclonal antibody design tasks

These five prompts test scientific planning and evidence reporting without prescribing tools or a workflow. Task instructions live in `tasks/monoclonal_antibody_design/`; published comparison values and sources live in `benchmark/`.

| Task | Reference and design objective | Benchmark |
| --- | --- | --- |
| [HER2 reference optimization](tasks/monoclonal_antibody_design/mab_her2_reference_optimization.md) | Trastuzumab-derived interaction optimization | [Ab-SELDON, 2026](benchmark/monoclonal_antibody_design/mab_her2_reference_optimization.md) |
| [PD-L1 epitope design](tasks/monoclonal_antibody_design/mab_pdl1_epitope_design.md) | Framework-conditioned scFv design; H5 comparator | [Germinal, 2026](benchmark/monoclonal_antibody_design/mab_pdl1_epitope_design.md) |
| [PD-1 epitope design](tasks/monoclonal_antibody_design/mab_pd1_epitope_design.md) | Humanized-framework CDR design; H965 comparator | [tFold, online 2025 / volume 2026](benchmark/monoclonal_antibody_design/mab_pd1_epitope_design.md) |
| [LCAT CDR design](tasks/monoclonal_antibody_design/mab_lcat_cdr_design.md) | Masked CDR-H3 reconstruction for the 5BV7 reference Fab | [AbFlow, 2026](benchmark/monoclonal_antibody_design/mab_lcat_cdr_design.md) |
| [Gal-3BP reference design](tasks/monoclonal_antibody_design/mab_gal3bp_reference_design.md) | BDBV-43 scaffold refinement; Mut1 comparator | [Gal-3BP integrative design study, 2026](benchmark/monoclonal_antibody_design/mab_gal3bp_reference_design.md) |

The `paper_benchmark_tasks` and `paper_benchmark_references` catalogs pair each task with its benchmark document. They do not add executable profiles or automatic scientific graders. Prepare the specified inputs before execution; framework-conditioned and scFv tasks do not automatically satisfy the existing reference-guided bundle schema. Published candidate scores, dataset averages and selection thresholds are labelled separately, with unverified values left unavailable.

## Bispecific benchmarks

| Task | Benchmark reference |
| --- | --- |
| HER2 biparatopic design | [Zanidatamab structural and experimental comparator](benchmark/bispecific_design/bispecific_antibody_design.md) |
| Cellular mechanism assessment | [Classifier performance and annotation reference values](benchmark/bispecific_assessment/bispecific_cellular_mechanism_assessment.md) |
| CNS delivery assessment | [Local evaluation criteria and related source tasks](benchmark/bispecific_assessment/bispecific_cns_delivery_assessment.md) |
| CNS readout comparison | [Reported concentration values and readout interpretation](benchmark/bispecific_assessment/bispecific_cns_readout_comparison.md) |
| CNS integrated gate | [Reported brain-exposure means and decision criteria](benchmark/bispecific_assessment/bispecific_cns_shuttle_integrated_gate.md) |

Three assessment prompts adapt public TxBench-Ab examples. Their benchmarks distinguish prompt-provided values from agent-reported observations; the latter are not verified answer keys. The general CNS-delivery task requires study-specific values, while the HER2 biparatopic task uses published structural and experimental reference evidence.

## Current implementation

The environment is at **Specification** maturity. The five current monoclonal tasks are evaluation prompts with separate published benchmarks. Existing monoclonal schemas and validation routines remain available for contract regression checks; their older prompts are retained only as test fixtures. Bispecific task profiles are unchanged.

Scientific execution requires external workflows. Passing these software checks does not establish antibody binding, function, safety, or improvement. Detailed requirements and remaining gaps are documented in the [environment specification](ENVIRONMENT_SPEC.md) and [coverage review](tests/monoclonal_antibody_with_reference/COVERAGE.md).
