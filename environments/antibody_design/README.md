# Antibody Design

The `antibody_design` environment organizes antibody-design research into clearly defined tasks, input/output requirements, and validation criteria. It covers monoclonal antibodies with a supplied reference, target-only discovery, and bispecific antibody design and evidence assessment.

## Task families

| Family | Description |
| --- | --- |
| Monoclonal with reference | EGFR-directed design using cetuximab as the reference antibody. Two separate DENV prompt variants also remain available. |
| Monoclonal target only | EGFR-directed discovery without a supplied binding-reference antibody, with candidate-origin and evaluation requirements. |
| Bispecific design | HER2 biparatopic design using zanidatamab as the reference, with domain II/domain IV assignments and evidence for each arm and the assembled molecule. |
| Bispecific assessment | Supplied evidence is assessed through cellular-mechanism, CNS-delivery, CNS-readout comparison, and integrated CNS-assessment tasks. |

## Folder structure

```text
antibody_design/
├── README.md                     # Environment overview
├── ENVIRONMENT_SPEC.md           # Detailed requirements and implementation status
├── config/                       # Configuration and machine-readable definitions
│   ├── environment.yaml          # Task catalog and profile mapping
│   ├── shared/                   # Common fields, protocol and metric definitions
│   ├── monoclonal_reference/     # Reference-guided monoclonal configurations
│   ├── monoclonal_target_only/   # Target-only monoclonal configurations
│   ├── bispecific_design/        # Bispecific design configurations
│   └── bispecific_assessment/    # Cellular and CNS assessment configurations
├── tasks/                        # Nine Markdown task specifications only
├── tests/                        # Validation code, fixtures, and automated checks
│   └── monoclonal_antibody_with_reference/
└── results/                      # Example outputs and validation reports
```

The tree shows the main files and directories.

- **`ENVIRONMENT_SPEC.md`** defines the environment's scope, scientific requirements, evidence expectations, and current implementation boundaries.
- **`config/`** contains task profiles, request/result schemas, JSON input examples, and validation dependencies. Each family has its own configuration; common definitions are shared. See the [configuration guide](config/README.md).
- **`tasks/`** contains the nine task instructions as Markdown files. Each describes the objective, required inputs, constraints, evaluation requirements, and expected outputs.
- **`tests/`** contains all testing and validation code. The dedicated monoclonal suite covers a supplied antigen and reference antibody; shared checks validate configurations across all task families.
- **`results/`** holds small example outputs and generated validation summaries. Expected output formats are described in the [results guide](results/README.md).

Supporting [research notes](../../research/antibody_design/research-notes.md) and [references](../../research/antibody_design/references.md) are maintained separately under `research/antibody_design/` at the repository root.

## Current implementation

The environment is at **Specification** maturity. Reference-guided monoclonal tasks include input-completeness and result-bundle checks. Target-only, bispecific design, and assessment tasks include schemas and declared-data consistency checks.

Scientific execution requires external workflows. Passing these software checks does not establish antibody binding, function, safety, or improvement. Detailed requirements and remaining gaps are documented in the [environment specification](ENVIRONMENT_SPEC.md) and [coverage review](tests/monoclonal_antibody_with_reference/COVERAGE.md).
