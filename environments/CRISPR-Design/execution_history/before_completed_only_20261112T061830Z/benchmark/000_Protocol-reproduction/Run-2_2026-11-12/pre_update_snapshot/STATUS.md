# Status

**Lifecycle:** Runtime-started (first executed run + first executed benchmark; adapters
still partial). **Protocol:** v0.1 (draft — no engine freeze; thresholds still
calibrate-before-freeze). **Contribution status:** awaiting issue/PR assignment per repo workflow.

## Implemented and evidenced

- **Runtime phase (2026-11-10, first executed):** task-002 Run1 executed end-to-end —
  8,421 windows enumerated, 227 coding-valid scored on **6 endpoints** (RuleSet1,
  RuleSet3-Sequence-Hsu2013, CRISPRater, CRISPRscan-T7-context, **CRISPRon**, Lindel
  frameshift); GRCh38 Bowtie-1.3.1 index rebuilt; off-target + CFD + DRAFT gates +
  R2/R3 ranking; run-validation suite (determinism, Lindel regression anchor 0.798,
  coordinate integrity, off-target positive/negative controls).
- **CRISPRon installed & verified** (Zenodo v1.0, AGPL-3.0 internal-use; regression
  `TEST ok`; Keras-2/TF-2.14 pin documented; CRISPRoff features via RTH-tools-admin).
  New-models survey (source-verified) archived; second wave queued: Azimuth-2.0 (py2.7),
  DeepSpCas9 (py2.7/TF1, MIT subtree), **DeepCas12a (Apache-2.0, torch)**; DeepHF
  standalone repo confirmed dead (404) — registry corrected.
- **First executed benchmark:** Xiang-2021 TRAP12K D10+dox clean-cohort evaluation —
  RS3 **0.516 [0.500–0.530]**, CRISPRon 0.504 [0.489–0.519] (exposed), RS1 0.222,
  CRISPRater 0.091 vs **measured assay-noise ceiling 0.615**; blind label join; no
  tuning; methodology correction documented (GEO read-count columns ≠ editing rates).
  [benchmark/001_Xiang2021-clean-evaluation](benchmark/001_Xiang2021-clean-evaluation/README.md).
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
- **Task taxonomy:** 13 task documents (general routing + 12 modality/application tasks),
  each with application-specific stages/vetoes/weights, example request briefs
  (illustrative-only markers), and stated published-anchor benchmark status.
- **Contracts:** requirement-brief and candidate JSON schemas; environment.yaml policy;
  thresholds DRAFT v0.1 with per-threshold provenance and calibrate-before-freeze rule.
- **Local asset verification (inherited):** prior KIF11 CRISPR-KO run provides
  crisprDesign/crisprScore installed with frozen R library; Lindel backend interface
  test PASS (0.798); Bowtie 1.3.1 with checksum-verified GRCh38.p14 index; GENCODE 49;
  transcript/CDS validation pipeline; documented off-target policy v1.0.
  `runtime/probe_backends.py` re-checks presence on demand.
- **Package validation:** `tests/validate_spec.py` (stdlib) — files/links, task house
  structure, schema well-formedness, example-brief schema conformance, YAML invariants,
  benchmark-doc structure, results-tree conventions. See [tests/validation.json](tests/validation.json).

## Not established

Adapters beyond the knockout stack are not yet built (CRISPRon/RS3/Lindel/CFD/Bowtie
live; Elevation, variant-aware CRISPRitz/CRISPRme, PRIDICT2.0, BEDICT2.0, DeepCas12a
pending); no frozen gates (thresholds are DRAFT); only one of the five pre-registered
benchmarks executed; no wet-lab validation of any candidate; no delivery prediction;
plant and pathogen-diagnostics execution gated.

## Open backlog

1. Runtime phase: backend adapters + ranking implementation (R1–R3) + explorer loop (X1–X5).
2. Threshold calibration on Kim-2019 held-out + Konstantakos 6-disjoint-set data → gate freeze v1.0.
3. First benchmark executions (pre-registered plan in benchmark/BENCHMARK_RUNS.md).
4. Bulge-aware + VCF-aware off-target layer (CRISPRitz/CRISPRme install decision;
   CC BY-NC CRISOT redistribution question).
5. PRIDICT2.0 CLI local deployment + Mathis held-out data licensing check.
6. Cas12a decision: Kim-2018 model via crisprScore vs Luo-2019 R package.
