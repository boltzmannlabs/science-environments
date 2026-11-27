# CRISPR Design

Application-aware CRISPR guide-RNA design environment: request routing, multi-dimensional
candidate evaluation and requirement-aware ranking across the editing modalities —
knockout · therapeutic in-vivo · variant correction (BE/PE/HDR router) · base editing ·
prime editing · CRISPRi/a · CRISPRoff · Cas13 · diagnostics · pooled libraries — with
executed computational benchmarks and enforced evidence honesty.

## About-env

- **13 fully-specified agent tasks** in the house structure (Description → Target →
  Design Constraints → Required Execution Steps → Expected Output → Constraints →
  Important Instructions), each with an example brief that validates against the
  [requirement-brief schema](config/requirement_brief.schema.json).
- **Seven completed native-model benchmarks** in the [completed-only
  registry](benchmark/BENCHMARK_RUNS.md) — RS3 Sequence, CRISPRon, CFD2016, BE-Hive BE4,
  PRIDICT2.0, DeepPrime PE2, RFcombined — with fresh native inference rerun and verified
  identical for five of them, and scientifically material limitations attached to every
  result.
- **An executed end-to-end workflow (Run-1, task 002):** 8,421 windows enumerated, 227
  coding-valid guides scored on 6 endpoints, Bowtie off-target search with CFD pair
  scoring, Lindel frameshift outcomes (regression anchor 0.798) and R2/R3 ranking.
- **Machine-checked integrity:** 10/10 package validation
  ([validate_spec.py](tests/validate_spec.py)) plus publication-integrity checks
  ([test_completed_benchmarks.py](tests/test_completed_benchmarks.py) — SHA-256 artifact
  binding, fresh-inference verification, independent metric recomputation, link
  resolution).
- **Source-verified 34-tool registry** with licenses, availability and leakage notes;
  common-lore misattributions were corrected during curation, and every number carries a
  primary source.
- **Enforced honesty discipline:** per-dimension evidence, `NOT_RUN(reason)` transparency
  and `best_design=null` without wet-lab data; off-target output is prioritization,
  never a safety claim.

**Status: Partial computational workflows and executed model benchmarks; protocol v0.1 gates remain DRAFT.** All 13 tasks have hash-bound result records (Run-2_2026-11-12), and every claim in this package is traceable to what actually ran: fresh model inference, matched held-out evaluation, author-score replay, component-only tests and explicit blockers are each labeled as such. Model benchmarks validate endpoints, not full design applications; no wet-lab validation exists. The older mixed-report archive is [absent from this checkout](results/HISTORY.md); historical preservation is unverified here.

**Default operation: agent-led execution.** Give the agent a target
gene/locus and, when known, the modality (knockout · base editing · prime editing · HDR ·
CRISPRi/a · CRISPRoff · Cas13 · diagnostics · pooled library) and priorities. The agent
routes the request (DESIGN / EVALUATE / EXPLORATORY / BENCHMARK / AUDIT), resolves the
requirement brief, enumerates guide candidates, evaluates them through a fixed
multi-dimensional battery under calibrated-then-frozen gates, and returns a traceable,
per-dimension-ranked deliverable capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

**One environment, modality tasks.** The battery and gates are shared; application tasks
add required stages, hard vetoes and interpretation rules — not separate generators.
Scope gates are deliberate safety posture: pathogen-diagnostics design is review-only;
plant editing is inactive pending a species adapter; microbial design runs through its
dedicated task with bacterial models only.

**Evidence base.** Built from a 2026-11-10 three-sweep source-verified curation
(on-target nucleases · precision editing & regulation · specificity/Cas13/diagnostics/
libraries) plus a local-asset audit that recovered a prior verified CRISPR-KO stack
(crisprDesign/crisprScore installed; Lindel backend PASS; Bowtie 1.3.1 + GRCh38.p14
index + GENCODE 49) and put it back to work. Misattributions in common lore were
corrected during curation (see [research notes](../../research/CRISPR-Design/research-notes.md));
unverified items are flagged UNVERIFIED rather than silently trusted.

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
5. [Runtime contracts](src/CONTRACTS.md): backend map, invocation discipline,
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
├── config/                         # contracts, draft gates, 13 example briefs
├── tasks/                          # index and 13 task definitions
├── src/                            # runtime contracts, backend probe, knockout implementation
├── scripts/
│   ├── README.md
│   └── benchmarks/00N_<Model>/      # original inference recipes
├── tests/                          # package, run and benchmark validation
├── benchmark/
│   ├── README.md
│   ├── BENCHMARK_RUNS.md
│   ├── completed_benchmarks.{json,csv}
│   └── 00N_<task-name>/README.md    # task indexes, evaluation definitions and limits
└── results/
    ├── README.md
    ├── HISTORY.md                  # run-name mapping and missing-evidence notes
    ├── 00N_<application>/
    │   └── Run-2_2026-11-12/        # 13 task reports, provenance and actual inputs
    ├── 002_knockout_gene_disruption/
    │   └── Run-1_2026-11-10/        # first-run stage-1 record and input snapshots
    └── benchmarks/
        ├── README.md
        ├── PROVENANCE.{json,sha256}
        └── 00N_<Model>/
            └── Run-4_2026-11-12/    # reports, predictions, metrics, protocol snapshots, logs
```


Run names follow `Run-<number>_<YYYY-MM-DD>`. Existing campaign numbers retain their
meaning; only `Run1_20261110` was renamed to `Run-1_2026-11-10`. Raw task outputs,
reference genomes and local runtimes are ignored. Lightweight task evidence and the
previously tracked benchmark artifacts remain eligible for Git tracking. See
[results/HISTORY.md](results/HISTORY.md) for migration and availability details.

## Local validation

From the repository root:

```bash
python3 environments/CRISPR-Design/tests/validate_spec.py
python3 environments/CRISPR-Design/tests/test_completed_benchmarks.py
```

Package validation uses the Python standard library. Benchmark validation also needs
pandas, NumPy, SciPy, scikit-learn and the external source roots recorded in provenance.
It recomputes saved metrics and checks recorded inference evidence; it does not rerun
model inference. Source-copy verification and historical-archive checks fail while
the original archive and three indexed source files within it are missing. First-run validation additionally requires the local scientific runtimes,
reference assets and missing stage-2 outputs; see [the acceptance plan](tests/ACCEPTANCE.md).

## Relationship to the prior base-editing environment

`environments/crispr-base-editing-environment` (single-task ToolUniverse wrapper,
ABE/CBE design) is subsumed by task 005 (base editing) here; its 50-nt-context predictor
conventions carry over where the wrapped tools are used.
