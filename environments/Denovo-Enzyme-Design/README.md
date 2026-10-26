# Denovo Enzyme Design

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
│   ├── request.example.json
│   └── homodimer.request.example.json
└── tests/
    ├── ACCEPTANCE.md
    ├── validate_spec.py
    └── specification-validation.json
```

The [monomer request](tasks/request.example.json) and [homodimer request](tasks/homodimer.request.example.json) illustrate input syntax only. Conditions, design counts and budgets are illustrative, not approved run limits. Neither request supplies a qualified reaction profile or a completed design run. No motifs, model weights, experimental results or invented benchmark scores are included.

## Scope

The specified scope is soluble, cofactor-free **monomers and homodimers**. A monomer has one protein chain; a homodimer has two copies of one sequence. Each enabled assembly/reaction combination requires its own qualified profile and working capabilities. Heterodimers, larger assemblies, metals, organic cofactors and membrane systems require separately qualified extensions. No scientific runtime support is claimed by this specification.

When assembly is unspecified, resolve it from biological evidence before generation; do not default to a monomer or infer it from the coordinate-file chain count. The homodimer path includes coupled sequence design, independent assembly assessment, interface checks and explicit active-site/state coverage. See [assembly requirements](ENVIRONMENT_SPEC.md#assembly-resolution-and-homodimer-contract).

Contract version 2.0 adds assembly, chain and site fields to reaction profiles. Earlier profiles require explicit migration and renewed qualification for their declared scope; changing the version string is insufficient.

The user supplies the conversion, conditions and requirements. The environment supplies mapped chemistry, catalytic motifs, state models, tool settings, thresholds and rewards from a versioned profile maintained by the scientific team.

## Validate this specification package

From this directory, with Python, PyYAML and jsonschema available:

```bash
python3 tests/validate_spec.py
```

This checks document links, schemas, the example request, stage dependencies and policy invariants. It does not execute enzyme generation or chemistry calculations.

## Contribution and licensing

**Owner, tracking issue and reviewers:** pending assignment.

Repository location: `environments/Denovo-Enzyme-Design/`. Supporting research and sources are maintained in `research/Denovo-Enzyme-Design/`, following [CONTRIBUTING.md](../../CONTRIBUTING.md). The repository structure, contribution guidelines, PR template and license notice were read on 26 October 2026.

This is a specification contribution. Issue linkage and scientific/software review remain pending. Package checks do not establish a working or scientifically validated environment.

The repository's [LICENSE](../../LICENSE) states that license selection is pending; it is not a license grant. This package does not add a separate license or redistribute third-party code, weights or restricted datasets.
