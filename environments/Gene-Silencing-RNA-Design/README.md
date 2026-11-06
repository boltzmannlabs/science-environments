# Gene Silencing RNA Design

**Status: In Progress.** This package includes the application-aware design protocol (v1.2), a frozen evaluation-gate set, requirement-aware ranking, an exploratory design loop, and executed computational benchmarks on public data. Experimental validation, delivery/chemistry prediction and plant/pest adapters remain separate requirements.

**Default operation: agent-led execution.** Give the agent a target gene (or candidate sequences) and, when known, the application and priorities. The agent routes the request (DESIGN / EVALUATE / EXPLORATORY / BENCHMARK / AUDIT), resolves the requirement brief, generates and evaluates siRNA candidates through a fixed multi-dimensional battery under frozen gates, and returns a traceable, per-dimension-ranked deliverable. When the user has only a target, EXPLORATORY mode searches the design space under multiple strategies and requirement hypotheses and returns a consensus panel plus a **proposed** brief for confirmation.

Accept an exact human transcript and design requirements; generate paired 19-nt core candidates; evaluate efficacy (two independent endpoints, never blended), structure, both-strand specificity, seed toxicity and immune hazards; rank under the user's confirmed requirements with mandatory weight-perturbation stability; return a typed-evidence shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

**One environment, different applications.** The battery and gates are shared. Nine human application profiles (oncology; genetic disease ± allele-selective; metabolic/liver-GalNAc; systemic/LNP; neuro/CNS; inflammation/immune modulation; functional genomics; gene-expression regulation; drug-target validation) add required stages, hard vetoes and interpretation rules — not separate generators. Antiviral/pathogen/pest requests are review-only; agricultural/plant design is inactive pending a species adapter. Human efficacy models are never applied to plant/pest targets.

Protocol versions are frozen with hashes (`engine-v1.0.0` → `v1.1.0` requirement ranking → `v1.2.0` explorer). Component changes require a version bump; gate thresholds may be tightened by a user brief, never loosened silently. Constraint adaptations discovered during exploration (e.g., cohort-relative re-anchoring of a saturated off-target gate) are **PROPOSED** with diagnosis and require user confirmation; affected candidates carry `rel_gate_only`.

## Read in this order

1. [Agent task](tasks/gene_silencing_rna_001.md): task-facing description, required execution steps, constraints and expected deliverable.
2. [Environment specification](ENVIRONMENT_SPEC.md): modes, inputs, brief contract, battery stages, ranking, benchmarking and scope gates.
3. [Environment configuration](config/environment.yaml), [requirement-brief contract](config/requirement_brief.schema.json) and [candidate contract](config/candidate.schema.json); frozen gates in [thresholds.v1.0.frozen.json](config/thresholds.v1.0.frozen.json).
4. [Runtime contracts](runtime/CONTRACTS.md): isolated backends, exact invocations, operational rules.
5. [Acceptance plan](tests/ACCEPTANCE.md) and recorded validation ([validation.json](tests/validation.json)); [benchmark evidence](benchmark/README.md) with the [run registry](benchmark/BENCHMARK_RUNS.md) (published references vs Run-N results in the iteration structure).
6. [Research notes](../../research/Gene-Silencing-RNA-Design/research-notes.md) and [references](../../research/Gene-Silencing-RNA-Design/references.md).

## Package structure

```text
Gene-Silencing-RNA-Design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── config/
│   ├── environment.yaml
│   ├── requirement_brief.schema.json
│   ├── candidate.schema.json
│   ├── thresholds.v1.0.frozen.json
│   ├── ttr_design.example.json
│   └── hif1a_exploratory.example.json
├── runtime/
│   ├── CONTRACTS.md
│   ├── immune_scan.py
│   ├── rank_by_requirements.py
│   └── explore_design.py
├── tasks/
│   ├── README.md                     (task index + benchmark status per application)
│   ├── gene_silencing_rna_001.md     (general routing task, all modes)
│   ├── gene_silencing_<application>_002..011.md   (ten application tasks: oncology ·
│   │                                  genetic-disease total/allele · metabolic-liver-GalNAc ·
│   │                                  systemic-LNP · neuro-CNS · inflammation · functional-
│   │                                  genomics · gene-regulation · drug-target-validation)
│   └── *.request.example.json        (per-application syntax-only example briefs)
├── tests/
│   ├── ACCEPTANCE.md
│   ├── validate_spec.py
│   ├── test_runtime.py
│   └── validation.json
├── benchmark/
│   ├── README.md
│   ├── WORKFLOWS_AND_VALIDATION.md   (per-benchmark workflows, tools, validation, arms)
│   ├── HeadToHead-LargePool/         (manual-vs-sub-agent definitive comparison)
│   ├── PROVENANCE.sha256
│   ├── Simone-independent-evaluation/
│   ├── TTR-approved-drugs-cohort/
│   └── HIF1A-case-study/
└── results/
```

Example briefs illustrate syntax only; they are not approved runs. No model weights, transcriptome indexes or restricted datasets are redistributed; backends are referenced by absolute local path with pinned versions and hashes (see [runtime contracts](runtime/CONTRACTS.md)).

## Scope

Human siRNA/shRNA-scale knockdown reagent design on exact versioned transcripts (paired 19-nt RNA cores; generator envelope 19–8,000 nt with the acceptance-validated span 57–1,000 nt disclosed when exceeded). Chemistry-aware and delivery layers are context annotations, not predictions (no public sequence-based delivery predictor exists). ASO efficacy models are explicitly excluded from siRNA scoring. The battery's E4e hybridization stage is currently `NOT_RUN(broken-binary)` — see [STATUS](STATUS.md).

## Validate this specification package

From this directory (Python 3.10+ standard library):

```bash
python3 tests/validate_spec.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

These checks validate the specification package and runtime-script behavior on synthetic fixtures only. They do not validate external tools, model predictions or biological efficacy. Component-level backend validation (11/12 pass, one documented defect) is recorded in the source workspace's end-to-end validation report, referenced from [STATUS](STATUS.md).

## Contribution and licensing

**Owner, tracking issue and reviewers:** pending assignment.

Repository location: `environments/Gene-Silencing-RNA-Design/`. Supporting research and sources are maintained in `research/Gene-Silencing-RNA-Design/`, following [CONTRIBUTING.md](../../CONTRIBUTING.md).

This is a protocol-and-benchmark contribution. Issue linkage and scientific/software review remain pending. Computational benchmark results do not establish biological efficacy. The repository's [LICENSE](../../LICENSE) states that license selection is pending; it is not a license grant. This package adds no separate license and redistributes no third-party code, weights or restricted datasets; upstream OligoFormer is proprietary-licensed (research use, no redistribution) and no-license models (RNAiSpline, SiaRNA, shRNAI) remain internal-research-only.
