# Monoclonal Antibody Design

**Environment ID:** `antibody_design`  
**Status:** Computational monoclonal-antibody specification with executable DENV contracts and target-agnostic mAb request/result validation. The protocol records which tools a configured Agent-Scientist run uses; this folder validates the request and result bundle but does not launch tools, install adapters, or qualify model weights or biological thresholds.

Define reproducible, computational-only tasks for paired-chain monoclonal antibodies. The primary lane takes a supplied antigen and reference antibody, preserves their declared identities and chain pairing, and evaluates a single declared objective such as affinity maturation, humanization, developability improvement, specificity, or mechanism compatibility. The DENV-2/DV87.1 EDIII task is one concrete profile in that reusable environment, not the definition of all antibody tasks.

The task directory contains a reference-guided monoclonal task and a secondary target-only monoclonal task. Bispecific task templates are maintained as separate extensions and are outside the initial paired-chain monoclonal lane.

This package uses the repository's science-environment conventions for task definitions, configuration, validation, and result records. It specifies a reproducible monoclonal-antibody assessment without assuming a scientific execution engine or inventing an unprovided runner or API.

## Read in this order

1. [General task](tasks/denv_antibody_001.md): the benchmark without named scientific software.
2. [Tool-specific task](tasks/denv_antibody_001_tools.md): the same inputs, requirements, and outputs, with the methods named in the dengue case study.
3. [Reference-guided monoclonal design](tasks/mab_reference_guided_design.md): primary reusable task.
4. [Target-only monoclonal design](tasks/mab_target_only_design.md): secondary mode with no supplied reference.
5. [Generic mAb request schema](config/generic-antibody-request.schema.json), [generic result schema](config/generic-antibody-metrics.schema.json), and [assay record schema](config/mab-assay-record.schema.json).
6. [Environment specification](ENVIRONMENT_SPEC.md): task modes, stages, evidence, comparison rules, and failure handling.
7. [Configuration](config/environment.yaml), [DENV request schema](config/request.schema.json), [protocol schema](config/protocol.schema.json), [metric catalog](config/metric-catalog.json), and [DENV result schema](config/metrics.schema.json).
8. [Bispecific task templates](tasks/bispecific_antibody_design.md): separate extension, not part of the initial monoclonal lane.
9. [DENV benchmark brief](../../research/antibody_design/DENV2_Computational_Antibody_Benchmark.md) and [antibody research findings](../../research/antibody_design/research-notes.md).
10. [Acceptance plan](tests/ACCEPTANCE.md) and [result format](results/README.md).

The two DENV task files are alternative presentations of **one benchmark**, not two independent biological tasks. Freeze the same input package, evaluation protocol, budget, and random seed before comparing them. The general task does not prescribe implementations; implementations actually used must still be recorded in the submitted evidence.

## Package structure

```text
antibody_design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── validation.py
├── config/
│   ├── environment.yaml
│   ├── generic-antibody-request.schema.json
│   ├── generic-antibody-metrics.schema.json
│   ├── mab-assay-record.schema.json
│   ├── request.schema.json
│   ├── protocol.schema.json
│   └── metrics.schema.json
├── tasks/
│   ├── denv_antibody_001.md
│   ├── denv_antibody_001_tools.md
│   ├── mab_reference_guided_design.md
│   ├── mab_target_only_design.md
│   ├── bispecific_antibody_design.md
│   ├── bispecific_cellular_mechanism_assessment.md
│   ├── bispecific_cns_delivery_assessment.md
│   ├── bispecific_cns_shuttle_integrated_gate.md
│   ├── bispecific_cns_readout_comparison.md
│   └── request.example.json
├── tests/
│   ├── ACCEPTANCE.md
│   ├── MONOCLONAL_ANTIBODY_TEST_CASES.md
│   ├── test_task_variants.py
│   ├── test_validation.py
│   ├── test_mab_testing_criteria.py
│   ├── make_needs_input_example.py
│   ├── validate_spec.py
│   └── specification-validation.json
└── results/
    ├── README.md
    └── needs-input.example.json
```

## Validate the package

From this directory, using an interpreter with PyYAML and jsonschema installed:

```bash
python3 tests/validate_spec.py
```

This runs the package's specification checks and behavioral tests, then writes a dated validation report. It does not submit scientific jobs. Tests use explicitly synthetic, non-biological fixtures for software assertions.

Inspect the example request's readiness:

```bash
python3 validation.py preflight tasks/request.example.json
```

The example intentionally returns `NEEDS_INPUT` and exit code 2: exact biological inputs are absent. No antigen sequence, antibody sequence, structure accession, chain assignment, or calibrated scientific threshold has been invented.

For an externally produced run bundle, validate the declared input and output contracts:

```bash
python3 validation.py bundle /path/to/run/08_results \
  --request /path/to/run/request.json --input-root /path/to/run
```

This checks schema, file hashes, evidence completeness, frozen rule decisions, resource accounting, and consistency between the shortlist and paired FASTA. It does not independently verify molecular identities, recompute predictions, or establish the truth of a scientific claim.

The same `preflight` and `bundle` commands dispatch target-agnostic monoclonal requests by their `design_mode`. Validate an individual historical or externally generated assay record with:

```bash
python3 validation.py assay-record /path/to/assay-record.json --root /path/to/run
```

Preflight checks request structure, local artifact hashes, protocol qualification, method revisions, required evidence groups, and resource limits. It does not install or execute scientific tools. A completed computational result must record the model, Agent-Scientist harness, enabled tools, execution backend, isolated workspace, seed, and exact protocol revision.

## What the dengue records establish

The documented named methods are Stability-Binding DDG (backend job `stability-binding-ddg`), PRODIGY, and ipSAE. The records name no antibody-antigen complex generator, and they describe docking, developability predictions, and molecular dynamics without specifying their implementations. Those capabilities remain unbound until qualified implementations and settings are supplied. No replacement software or invocation parameters are guessed.

The records do not supply a reproducible sequence/structure input bundle, a consistent candidate-to-experimental-sample map, or a qualified evaluation protocol. Historical shortlist counts and metric ranges are outcomes, not acceptance thresholds. ELISA EC50 is a separate experimental endpoint and is excluded from agent-visible task answers.

The supplied example's `2024-09-01` cutoff is preserved in the request. Availability of every selected code, model, and dataset version must be demonstrated against it. Naming a method in retrospective documentation does not establish eligibility; unresolved or incompatible versions produce `PROTOCOL_REQUIRED` rather than silently relaxing the cutoff.

## Monoclonal-antibody design requirements

Each design is a paired heavy/light-chain antibody with a declared IgG, Fab, or F(ab')2 product context and an explicit sequence scope (`variable_domains`, `Fab_chains`, or `full_length_chains`), reference lineage, variable-domain numbering scheme, framework/CDR annotations, and allowed edit mask. scFv, VHH/nanobody, fusion, conjugate, and multispecific architectures need different chain contracts and are separate extensions. Each target is identified by antigen sequence, construct, strain or serotype, structure, chain assignment, and mapped binding region. Candidate identity and chain pairing must remain consistent through structure assessment, scoring, and export.

Evaluation keeps antibody-chain fold confidence, antigen–antibody pose and interface confidence, predicted interaction energy, stability, and developability as separate evidence categories. Aggregation, solubility, expression-related liabilities, polyreactivity, and immunogenicity indicators require their own qualified definitions and uncertainty. Predicted binding, measured affinity, ELISA binding, neutralization, and enhancement are distinct endpoints; none can substitute for another or be combined into an uncalibrated score. The rationale and published evidence are documented in the linked [research notes](../../research/antibody_design/research-notes.md).

### Current readiness gaps

The package makes the antibody-specific requirements explicit, but the supplied dengue records do not yet provide a runnable, reproducible experiment. Before scientific execution, supply and verify the exact DV87.1 heavy and light sequences, DENV-2 EDIII antigen sequence and structure, construct/chain/residue mapping, and candidate-to-experimental-sample crosswalk. Freeze qualified implementations, cutoff-compatible versions, score definitions, uncertainty handling, thresholds, and resource settings. The source documents leave some of these items unnamed or inconsistent; the research notes record those uncertainties instead of filling them with assumptions. Until they are resolved, preflight must return `NEEDS_INPUT` or `PROTOCOL_REQUIRED`.

## Integration and review status

The package can be consumed by an external Agent-Scientist harness through the request and result contracts. Use computational tools already exposed to that runtime and record their exact revisions and enabled-tool manifest in the frozen protocol and run provenance; this package does not install or auto-detect them. Biological input preparation, scientific calibration, and live execution remain dependencies of a design run. No training or reward-driven optimization loop is implemented.

**Owner, issue, and scientific/software reviewers:** pending assignment. This is a local specification and validation contribution; publication and review have not been completed. The repository's pending license applies. Changes are confined to this new environment.
