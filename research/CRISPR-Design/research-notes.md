# CRISPR Design — research notes

## Scope and provenance

Application-aware CRISPR guide-RNA design across editing modalities (nuclease knockout,
base editing, prime editing, HDR, CRISPRi/a, CRISPRoff, Cas13, diagnostics, pooled
libraries). Curation assembled 2026-11-10 in the source workspace
(`~/IMRAN/NOV26/cirspr-sci-env`) from: (1) a three-agent web curation sweep with
per-URL primary-source verification — on-target nuclease activity; precision editing &
regulation; specificity/Cas13/diagnostics/screens; (2) direct inspection of local
installations (prior CRISPR-KO run workspace with crisprDesign/crisprScore + verified
Lindel backend + Bowtie 1.3.1 GRCh38 index; existing single-task
`crispr-base-editing-environment`). Full tables live in the source workspace
(`~/IMRAN/NOV26/cirspr-sci-env/01_tools/open_source/*.md`, `TOOL_REGISTRY.csv`,
`02_benchmarks/published_benchmarks.md`); this file records the findings that drove the
environment design. Full citations: [references.md](references.md).

## Key findings driving the environment design

1. **Task taxonomy (13 tasks).** The modality axis (KO / BE / PE / HDR / CRISPRi/a /
   CRISPRoff / Cas13 / diagnostics / libraries / plant / microbial) is the clean
   application split — each has a distinct design objective, toolset, and benchmark
   anchor, unlike siRNA where the application axis was delivery/disease-context.
2. **Local head start.** A prior KIF11 CRISPR-KO run
   (`~/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38/`)
   has crisprDesign/crisprScore (Bioconductor) installed with a frozen R library, a
   verified Lindel model backend (interface test PASS 0.798, crisprScoreData EH6128),
   Bowtie 1.3.1 with a checksum-verified GRCh38.p14 index, GENCODE 49 annotation, and a
   transcript-validation pipeline (spliced-exon sequence checks + CDS translation checks).
   Off-target policy documented in `runs/20261105T102927Z/off_target_policy.yaml`
   (NGG, 20-nt spacer, 0–3 mismatches, both strands, intended-locus exclusion, bulges
   NOT_EVALUATED).
3. **Benchmark integrity.** (a) DeepCRISPR headline numbers do not transfer to
   training-disjoint data (best on only 1/6 independent datasets — Konstantakos 2022);
   cross-study correlation can be as low as 0.52 (Kim-2019 vs Wang-2019). (b) No neutral
   head-to-head benchmark exists for base/prime-editing predictors — all cross-tool
   claims are self-reported on incompatible splits; BE-dataHIVE (460k combos, 5 studies
   harmonized) is the fair-comparison substrate. (c) Off-target in-silico scores are
   prioritization-only: recall ≈77% at top-500, weak score↔indel correlation
   (Kaufmann 2026, 14 tools). (d) Expression-system context binds: U6 vs T7/IVT scores
   do not transfer (Haeussler 2016). Realistic performance envelope: assay-replicate
   ρ≈0.7 ceiling; ≥0.4 on truly independent data is respectable.
4. **Reference standards per task** (see environment `benchmark/README.md`):
   KO on-target → Kim-2019 (12,832 paired sgRNA–target, SRA SRP150719) + Konstantakos
   6-disjoint-set protocol; variants → DeepHF (80,263 pairs, PRJNA522677); off-target →
   CHANGE-seq (110 guides / 201,934 sites) + GUIDE-seq (cell-based truth); BE → BE-Hive
   (38,538 targets, outcome R≈0.9) + BE-dataHIVE; PE → PRIDICT2.0 (92,423 pegRNAs,
   ρ 0.85/0.78); CRISPRi/a → Horlbeck-2016 γ-scores (rules only, no 2024–26 DL model
   found — gap); CRISPRoff → GSE168012 tiling + 3 design rules (no dedicated tool — gap);
   Cas13 → TIGER (~200k guides, 2023; Cas13design 2020 is the earlier model);
   diagnostics → EasyDesign (ρ 0.812, n=11,496; only large ML pair).
5. **Attribution corrections verified during curation** (common lore is wrong):
   DeepSpCas9 = Kim 2019 *Science Advances* (12,832 pairs — not "Nat Methods ~51k");
   Rule Set 3 = DeWeirdt 2022 *Nat Commun* (not "Hart 2017" — Hart 2017 is the
   screen-evaluation/BAGEL paper); CRISPRon = *Nat Commun* 2021 (not NAR); DeepHF =
   *Nat Commun* (not Cell Reports); DeepCpf1 = *Nat Biotechnol* 2018 (not Genome Biol);
   BE-Hive = Arbab 2020 *Cell* (Song 2020 *NBT* = DeepABE/DeepCBE, a different tool);
   DeepPE = Kim 2021 *NBT* (not "2020 Nat Methods"); DeepBE = N. Kim 2024 *NBT* (not
   "Furman Nat Commun"); CRISPR-BERT and CRISPR-Net are off-target tools; "MULTIPRIME"
   is an NGS-primer designer, not prime editing; "CRISPR-RT" and "CRISPRi-ML" could not
   be verified to exist.
6. **Therapeutic anchors are strategy-level only.** No proprietary therapeutic guide
   sequence is verifiably public: exa-cel/Casgevy guide "SPY101" is named but redacted
   (b)(4) in the FDA SBRA; nexiguran ziclumeran guide is patent-bound; VERVE-101 exact
   20-nt sequence unconfirmed in open text. Benchmarks anchor on target identity, edit
   mechanism, and off-target-assay strategy — never on invented sequences.
7. **Licenses bind reuse.** CRISOT is CC BY-NC 2.0 (non-commercial — blocks platform
   redistribution); deepcrispr.info portals research-use; DeepBE, yachielab
   base-editing-prediction, and the Cas13design GitHub mirror state no license
   (research-internal tier); Elevation is MIT (cleanest); crisprScore/crisprDesign are
   Bioconductor (MIT/Artistic-2.0).
8. **Variant-awareness is clinically load-bearing.** CRISPRme found a PAM-creating
   MAF-4.5% allele driving the top off-target for a clinical BCL11A enhancer guide;
   CHANGE-seq found human SNVs affect ~15.2% of analyzed off-target sites. Allele-specific
   and therapeutic tasks require VCF-aware search (CRISPRitz/CRISPRme), not
   reference-genome-only scoring.
9. **Scope gates** (mirroring the siRNA environment): pathogen-targeting diagnostics
   sequence design is review-only (EasyDesign/PrimedSherlock exist — tool presence is
   not authorization); plant editing is inactive pending a validated species adapter
   (no plant-specific activity model verified; mammalian scores transfer weakly).
10. **Gaps flagged as opportunities**: no verified activity predictor for SpG/SpRY/
    HypaCas9; Cas12a rests on Kim-2018 + preprints; no dedicated CRISPRoff designer;
    no CRISPRi/a DL model 2024–26; HDR ML niche nearly empty (largest public set n=30).

## Environment design decisions (2026-11-10)

- **One environment, modality tasks.** Shared core battery (guide intake → on-target
  multi-endpoint → off-target stack → indel outcome → application layers → physico-chem)
  + per-task layers, mirroring Gene-Silencing-RNA-Design's battery+profile pattern.
- **Thresholds stay DRAFT v0.1** until calibrated on Kim-2019/Konstantakos data; provenance
  per threshold is recorded; freeze happens at first benchmark execution.
- **Runtime starts honest**: backend map + probe script (liveness check of local assets);
  scoring adapters land in the next phase, against the verified KIF11-run evidence base.
- **Benchmarks: published anchors only.** No executed computational run is claimed yet;
  BENCHMARK_RUNS.md carries explicit NOT_EXECUTED Run slots.

## Open questions

1. Will CRISPRon complement or duplicate DeepSpCas9/RS2 in the local battery (correlated
   training data — Kim-2019 rescaled is inside CRISPRon's training)?
2. Bulge-aware off-target (CRISPRitz) vs Bowtie-1 ungapped: run both or sequence them?
3. Does the CC BY-NC CRISOT license force an in-house off-target scorer for any
   redistributed artifact?
4. Prime-editing local deployment: PRIDICT2.0 CLI vs web — dataset licensing for
   Mathis-2023 held-out reproduction to be checked at install time.
