# CRISPR Design

**Status: Partial computational workflows and executed model benchmarks; protocol v0.1 gates remain DRAFT.** All 13 tasks now have hash-bound result and benchmark records under Run-2_2026-11-12, following the sibling RNA environment layout. Evidence ranges from fresh model inference to author-score replay, component-only tests and explicit blockers; no complete application or experimental validation is claimed.

Start with the [campaign accuracy report](benchmark/000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md), [coverage matrix](benchmark/000_Protocol-reproduction/Run-2_2026-11-12/modality_performance_coverage_matrix.csv), and [result index](results/README.md).

**Default operation (once runtime lands): agent-led execution.** Give the agent a target
gene/locus and, when known, the modality (knockout · base editing · prime editing · HDR ·
CRISPRi/a · CRISPRoff · Cas13 · diagnostics · pooled library) and priorities. The agent
routes the request (DESIGN / EVALUATE / EXPLORATORY / BENCHMARK / AUDIT), resolves the
requirement brief, enumerates guide candidates, evaluates them through a fixed
multi-dimensional battery under calibrated-then-frozen gates, and returns a traceable,
per-dimension-ranked deliverable capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

**One environment, modality tasks.** The battery and gates are shared; application tasks
add required stages, hard vetoes and interpretation rules — not separate generators.
Pathogen-diagnostics design is review-only; plant editing is inactive pending a species
adapter; microbial design runs through its dedicated task with bacterial models.

**Evidence base.** Built from a 2026-11-10 three-sweep source-verified curation
(on-target nucleases · precision editing & regulation · specificity/Cas13/diagnostics/
libraries) plus a local-asset audit that found a prior verified CRISPR-KO run
(crisprDesign/crisprScore installed; Lindel backend PASS; Bowtie 1.3.1 + GRCh38.p14
index + GENCODE 49). Misattributions in common lore were corrected during curation
(see [research notes](../../research/CRISPR-Design/research-notes.md)); every number
carries a primary source; unverified items are flagged UNVERIFIED.

## Read in this order

1. [Task index](tasks/README.md) — 13 tasks with per-task benchmark status; start at the
   [general routing task](tasks/001_crispr_design_general.md).
2. [Environment specification](ENVIRONMENT_SPEC.md): modes, inputs, brief contract,
   battery stages, ranking, benchmarking and scope gates.
3. [Models and tools](MODELS_AND_TOOLS.md): curated registry with licenses, availability
   and leakage notes.
4. [Environment configuration](config/environment.yaml), [requirement-brief contract](config/requirement_brief.schema.json),
   [candidate contract](config/candidate.schema.json); draft gates in
   [thresholds.v0.1.draft.json](config/thresholds.v0.1.draft.json) (calibrate-then-freeze).
5. [Runtime contracts](runtime/CONTRACTS.md): backend map, invocation discipline,
   liveness probe.
6. [Acceptance plan](tests/ACCEPTANCE.md) and recorded package validation
   ([validation.json](tests/validation.json)); [benchmark anchors](benchmark/README.md)
   with the run registry ([BENCHMARK_RUNS.md](benchmark/BENCHMARK_RUNS.md)); unsupported stages remain `NOT_EXECUTED`.
7. [Research notes](../../research/CRISPR-Design/research-notes.md) and
   [references](../../research/CRISPR-Design/references.md).

## Package structure

```text
CRISPR-Design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── config/
│   ├── environment.yaml
│   ├── requirement_brief.schema.json
│   ├── candidate.schema.json
│   ├── thresholds.v0.1.draft.json     (DRAFT — calibrate on Kim-2019/Konstantakos before freeze)
│   └── 001..013_*.request.example.json  (13 example briefs, syntax only)
├── runtime/
│   ├── CONTRACTS.md                    (backend map + binding rules; verified local assets)
│   └── probe_backends.py               (liveness probe — reports backend presence, no fake scoring)
├── tasks/
│   ├── README.md                       (task index + benchmark status per task)
│   ├── 001_crispr_design_general.md    (routing task, all modes)
│   └── 002..013_crispr_<modality>.md   (KO · therapeutic in-vivo · variant correction ·
│                                        base editing · prime editing · CRISPRi/a · CRISPRoff ·
│                                        Cas13 · diagnostics[review-gated] · libraries ·
│                                        plant[inactive] · microbial)
├── tests/
│   ├── ACCEPTANCE.md
│   ├── validate_spec.py                (package validation, stdlib only)
│   └── validation.json                 (recorded results)
├── benchmark/
│   ├── README.md                       (published anchors plus executed, provenance-bound benchmarks)
│   └── BENCHMARK_RUNS.md               (published | Run-N iteration registry; NOT_EXECUTED slots)
└── results/                            (13 task folders with Run-2_2026-11-12 evidence; see results/README.md)
```

## Relationship to the prior base-editing environment

`environments/crispr-base-editing-environment` (single-task ToolUniverse wrapper,
ABE/CBE design) is subsumed by task 005 (base editing) here; its 50-nt-context predictor
conventions carry over where the wrapped tools are used.
