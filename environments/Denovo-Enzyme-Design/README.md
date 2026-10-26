# Boltzyme: de novo enzyme design

**Status: Specification.** This package specifies an end-to-end computational environment. It does not implement or validate the scientific pipeline.

Accept a requested chemical conversion and design requirements; generate enzyme candidates; evaluate folding, protein properties and catalytic chemistry; return a traceable shortlist. Reinforcement learning can control permitted design and evaluation choices, with the same mandatory acceptance rules as fixed execution.

## Read in this order

1. [Agent task](tasks/denovo_enzyme_001.md): the task-facing description, 14 required execution steps, constraints and expected deliverable, organized like the supplied BioDesignBench example.
2. [Environment specification](ENVIRONMENT_SPEC.md): inputs through final evaluation, including chemistry, RL, interfaces, failure handling and benchmarking.
3. [Environment configuration](config/environment.yaml), [request contract](config/request.schema.json) and [protocol contract](config/protocol.schema.json): machine-readable requirements.
4. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json): what has been checked and what still requires implementation.
5. [Research notes](../../research/Denovo-Enzyme-Design/research-notes.md) and [references](../../research/Denovo-Enzyme-Design/references.md): rationale, scientific foundations, provenance and open work.

The task preserves the reference's Description, Target, Design Constraints, Expected Output, Constraints and Important Instructions sections. Its software-list section is replaced with Required Execution Steps. The specification describes operations, acceptance decisions and outputs without prescribing named scientific software.

## Package structure

```text
Denovo-Enzyme-Design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── config/
│   ├── environment.yaml
│   ├── request.schema.json
│   └── protocol.schema.json
├── tasks/
│   ├── denovo_enzyme_001.md
│   └── request.example.json
└── tests/
    ├── ACCEPTANCE.md
    ├── validate_spec.py
    └── specification-validation.json
```

The example request demonstrates the user-input contract. It is not a scientifically qualified reaction profile or a completed design run. No motifs, model weights, experimental results or invented benchmark scores are included.

## Scope

The initial supported implementation is intended for soluble, single-chain, cofactor-free enzymes with a qualified reaction profile. Metals, organic cofactors, membrane systems and multichain assemblies require separately qualified extensions. A generic reaction request does not imply universal chemistry support.

The user supplies the conversion, conditions and requirements. The environment supplies mapped chemistry, catalytic motifs, state models, tool settings, thresholds and rewards from a versioned profile maintained by the scientific team.

## Validate this specification package

From this directory, with Python, PyYAML and jsonschema available:

```bash
python3 tests/validate_spec.py
```

This checks document links, schemas, the example request, stage dependencies and policy invariants. It does not execute enzyme generation or chemistry calculations.

## Contribution and licensing

**Owner:** [srivani1303](https://github.com/srivani1303). **Tracking issue and reviewers:** pending assignment.

Repository location: `environments/Denovo-Enzyme-Design/`. Supporting research and sources are maintained in `research/Denovo-Enzyme-Design/`, following [CONTRIBUTING.md](../../CONTRIBUTING.md). The repository structure, contribution guidelines, PR template and license notice were read on 26 October 2026.

This is a specification contribution on `feat/denovo-enzyme-design`. Issue linkage, a pull request and scientific/software review remain required before merge. Package checks do not establish a working or scientifically validated environment.

The repository's [LICENSE](../../LICENSE) states that license selection is pending; it is not a license grant. This package does not add a separate license or redistribute third-party code, weights or restricted datasets.
