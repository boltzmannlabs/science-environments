# Status

**Lifecycle:** Runtime-started (partial adapters; first executed run 2026-11-10; first
executed benchmark 2026-11-10; completed-only benchmark registry published 2026-11-12).
**Protocol:** v0.1 (draft — no engine freeze; thresholds still calibrate-before-freeze).
**Contribution status:** awaiting issue/PR assignment per repo workflow.

## Implemented and evidenced

- **Completed-only benchmark registry (2026-11-12):** seven completed
  native-model/endpoint evaluations — RS3 Sequence held-out activity, CRISPRon v1
  external activity, CFD2016 assayed specificity, BE-Hive BE4 any-edit efficiency,
  PRIDICT2.0 grouped-OOF outcomes, DeepPrime PE2 fixed test, RFcombined published-method
  refit ([BENCHMARK_RUNS.md](benchmark/BENCHMARK_RUNS.md)). Fresh native inference was
  rerun and verified identical for RS3, BE-Hive, PRIDICT2.0, DeepPrime and CFD; CRISPRon
  and RFcombined retain their already-completed native runs. No heuristic rule,
  missing-feature imputation or surrogate endpoint was added; publication integrity is
  machine-checked ([tests/test_completed_benchmarks.py](tests/test_completed_benchmarks.py)
  → [completed_benchmarks_validation.json](tests/completed_benchmarks_validation.json)).
- **Per-task records (Run-2_2026-11-12):** all 13 tasks have hash-bound result records
  (brief + provenance + REPORT) under `results/00N_<application>/`, plus archived
  Run-2/Run-3 benchmark comparisons in
  [execution_history](execution_history/before_completed_only_20261112T061830Z/README.md).
  Evidence classes are stated per task (fresh component evaluation · matched model
  components · author-score replay · component-only test · blocked endpoint); the
  [historical campaign report](execution_history/before_completed_only_20261112T061830Z/benchmark/000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md)
  and [coverage matrix](execution_history/before_completed_only_20261112T061830Z/benchmark/000_Protocol-reproduction/Run-2_2026-11-12/modality_performance_coverage_matrix.csv)
  describe that pre-reorganization campaign.
- **Runtime phase (2026-11-10, first executed):** task-002 Run1 executed end-to-end —
  8,421 windows enumerated, 227 coding-valid scored on **6 endpoints** (RuleSet1,
  RuleSet3-Sequence-Hsu2013, CRISPRater, CRISPRscan-T7-context, **CRISPRon**, Lindel
  frameshift); GRCh38 Bowtie-1.3.1 index rebuilt; off-target + CFD + DRAFT gates +
  R2/R3 ranking. Retained artifacts cover stage-1; the stage-2 outputs were not
  retained in the repo copy (noted in [runtime contracts](runtime/CONTRACTS.md)), so
  `tests/test_first_run.py` passes its stage-1 checks (coordinate integrity, Lindel
  regression anchor 0.798, cross-endpoint sanity) and fails the stage-2-dependent
  checks on file presence — regenerate by rerunning `run_002_specificity.R`.
- **CRISPRon installed & verified** (Zenodo v1.0, AGPL-3.0 internal-use; regression
  `TEST ok`; Keras-2/TF-2.14 pin documented; CRISPRoff features via RTH-tools-admin).
  New-models survey (source-verified) archived; second wave queued: Azimuth-2.0 (py2.7),
  DeepSpCas9 (py2.7/TF1, MIT subtree), **DeepCas12a (Apache-2.0, torch)**; DeepHF
  standalone repo confirmed dead (404) — registry corrected.
- **First executed benchmark (2026-11-10):** Xiang-2021 TRAP12K D10+dox clean-cohort
  evaluation — RS3 **0.516 [0.500–0.530]**, CRISPRon 0.504 [0.489–0.519] (exposed), RS1
  0.222, CRISPRater 0.091 vs **D8/D10 assay concordance 0.615 (not a predictor
  ceiling)**; blind label join; no tuning; methodology correction documented (GEO
  read-count columns ≠ editing rates) — archived under
  [execution_history](execution_history/before_completed_only_20261112T061830Z/benchmark/001_Xiang2021-clean-evaluation/README.md).
- **Curation (2026-11-10):** three-sweep source-verified tool/benchmark curation
  (on-target nucleases · precision editing & regulation · specificity/Cas13/diagnostics/
  libraries) with per-URL primary-source verification; 34-tool registry with licenses,
  availability, dataset pointers, leakage notes; misattribution corrections recorded
  (DeepSpCas9 = Sci Adv 2019 with 12,832 pairs — not "Nat Methods ~51k"; RS3 = DeWeirdt
  2022 — not "Hart 2017"; BE-Hive = Arbab 2020 Cell; DeepPE = Kim 2021 NBT; DeepBE =
  N. Kim 2024 NBT; CRISPR-BERT/CRISPR-Net are off-target tools; "MULTIPRIME",
  "CRISPR-RT", "CRISPRi-ML" unverified/nonexistent). Source workspace:
  `~/IMRAN/NOV26/cirspr-sci-env` (application map, TOOL_REGISTRY.csv, per-area tool
  docs, benchmark ledger).
- **Task taxonomy:** 13 task documents in the house structure (general routing + 12
  modality/application tasks), each with application-specific stages/vetoes/weights,
  example request briefs (illustrative-only markers), executed-evidence status and
  published-anchor status.
- **Contracts:** requirement-brief and candidate JSON schemas; environment.yaml policy;
  thresholds DRAFT v0.1 with per-threshold provenance and calibrate-before-freeze rule.
- **Local asset verification (inherited):** prior KIF11 CRISPR-KO run provides
  crisprDesign/crisprScore installed with frozen R library; Lindel backend interface
  test PASS (0.798); Bowtie 1.3.1 with checksum-verified GRCh38.p14 index; GENCODE 49;
  transcript/CDS validation pipeline; documented off-target policy v1.0.
  `runtime/probe_backends.py` re-checks presence on demand.
- **Package validation:** `tests/validate_spec.py` (stdlib) — files/links, task house
  structure, schema well-formedness, example-brief schema conformance, YAML invariants,
  benchmark-doc structure, results-tree conventions. See
  [tests/validation.json](tests/validation.json).
- **Reorganization (2026-11-12):** benchmark/ restricted to completed-only evidence;
  269 prior mixed files preserved byte-identically under `execution_history/`
  ([inventory](execution_history/before_completed_only_20261112T061830Z/archive_inventory.json));
  raw original scientific sources unchanged.

## Not established

There is no wet-lab validation of any candidate; no therapeutic safety or off-target
safety claims; `best_design=null` throughout. Adapters beyond the knockout stack are not
yet built (CRISPRon/RS3/Lindel/CFD/Bowtie live; Elevation, variant-aware
CRISPRitz/CRISPRme, PRIDICT2.0, BEDICT2.0, DeepCas12a pending); gates remain DRAFT
(not calibrated, not frozen); no delivery prediction; plant and pathogen-diagnostics
execution gated. Model benchmarks validate endpoints, not design applications: weak BE4
transfer, GFP leave-screen-out CRISPRi performance, incomplete diagnostics replay,
blocked epigenetic endpoint and author-score-replay-only plant/microbial evidence are
all stated as limitations in the registry and task files.

## Open backlog

1. Runtime phase: backend adapters + ranking implementation (R1–R3) + explorer loop (X1–X5).
2. Threshold calibration on Kim-2019 held-out + Konstantakos 6-disjoint-set data → gate freeze v1.0.
3. Remaining benchmark arms (pre-registered plan in
   [execution_history](execution_history/before_completed_only_20261112T061830Z/benchmark/BENCHMARK_RUNS.md)):
   CFD-vs-Elevation on CHANGE-seq; BEDICT2.0/DeepBE on BE-dataHIVE held-out editors;
   PRIDICT2.0 self-hosted CLI on Mathis held-out.
4. Bulge-aware + VCF-aware off-target layer (CRISPRitz/CRISPRme install decision;
   CC BY-NC CRISOT redistribution question).
5. PRIDICT2.0 CLI local deployment + Mathis held-out data licensing check.
6. Cas12a decision: Kim-2018 model via crisprScore vs Luo-2019 R package.
7. Diagnostics EasyDesign replay fix (nonnumeric dash tokens) before any diagnostic
   benchmark claim; epigenetic endpoint unblocking (labels + adapter).
