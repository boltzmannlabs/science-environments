# CRISPR Design

**Status: Partial computational workflows and executed model benchmarks; protocol v0.1 gates remain DRAFT.** All 13 tasks have hash-bound result records (Run-2_2026-11-12) and the active benchmark publication is the [completed-only registry](benchmark/BENCHMARK_RUNS.md) — seven completed native-model/endpoint evaluations, with fresh native inference rerun for RS3, BE-Hive, PRIDICT2.0, DeepPrime and CFD. Model benchmarks do not establish full design-application validation. Evidence ranges from fresh model inference to author-score replay, component-only tests and explicit blockers; no complete application or experimental validation is claimed, and no wet-lab validation exists. Older mixed reports and setup/partial evidence are retained as [execution history](execution_history/before_completed_only_20261112T061830Z/README.md) outside `benchmark/`.

**Default operation: agent-led execution.** Give the agent a target
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

1. [Task index](tasks/README.md) — 13 tasks with per-task executed-evidence and
   published-anchor status; start at the
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
   ([validation.json](tests/validation.json)); [benchmark evidence](benchmark/README.md)
   with the completed-only run registry ([BENCHMARK_RUNS.md](benchmark/BENCHMARK_RUNS.md));
   per-task [result index](results/README.md).
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
│   ├── probe_backends.py               (liveness probe — reports backend presence, no fake scoring)
│   ├── run_002_knockout.R              (executed Run1 stage-1: enumerate → E1/E2/E4/E6)
│   └── run_002_specificity.R           (executed Run1 stage-2: Bowtie E3 + CFD + gates + ranking)
├── tasks/
│   ├── README.md                       (task index + executed-evidence and anchor status per task)
│   ├── 001_crispr_design_general.md    (routing task, all modes)
│   └── 002..013_crispr_<modality>.md   (KO · therapeutic in-vivo · variant correction ·
│                                        base editing · prime editing · CRISPRi/a · CRISPRoff ·
│                                        Cas13 · diagnostics[review-gated] · libraries ·
│                                        plant[inactive] · microbial)
├── tests/
│   ├── ACCEPTANCE.md
│   ├── validate_spec.py                (package validation, stdlib only)
│   ├── validation.json                 (recorded results)
│   ├── test_first_run.py               (Run1 run-validation: determinism, anchors, controls)
│   ├── test_completed_benchmarks.py    (completed-only publication integrity + metric recomputation)
│   └── completed_benchmarks_validation.json
├── benchmark/                          (completed-only registry: 7 native-model/endpoint
│   ├── README.md                       evaluations under 00N_<Model>/Run-4_2026-11-12/,
│   ├── BENCHMARK_RUNS.md               each with predictions/metrics/protocol/REPORT;
│   ├── completed_benchmarks.{json,csv} PROVENANCE.json + sha256 binding)
│   └── 001..007_<Model>/
├── results/                            (13 task folders with Run-2_2026-11-12 records:
│   └── README.md                       REPORT + 00_inputs/requirement_brief + provenance)
└── execution_history/                  (pre-reorganization mixed evidence, byte-identical;
    └── before_completed_only_20261112T061830Z/  see its README.md)
```

## Relationship to the prior base-editing environment

`environments/crispr-base-editing-environment` (single-task ToolUniverse wrapper,
ABE/CBE design) is subsumed by task 005 (base editing) here; its 50-nt-context predictor
conventions carry over where the wrapped tools are used.
