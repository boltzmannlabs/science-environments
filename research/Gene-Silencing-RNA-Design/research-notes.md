# Gene Silencing RNA Design — research notes

## Scope and provenance

Application-aware human siRNA design, evaluation and property prediction. Assembled
2026-11-03/04 in the source workspace (`~/IMRAN/NOV26/siRNA-Design-Task-Specific`) from:
direct inspection of local installations (siRNA-Bench platform + model registry;
OligoFormer/RNA-FM integration workspace with pinned checkpoint SHA-256s; ToolUniverse 1.5.7
registry, 2,719 tools); a five-agent web curation sweep with per-URL verification
(efficacy/design tools; specificity/structure/immune evaluators; published designs and
datasets; ToolUniverse + delivery ecosystem; plant/pest tools); and executed benchmarks.

## Key findings driving the environment design

1. **Tool landscape:** OligoFormer upstream license is proprietary (research use, no
   redistribution); RNA-FM/RN.Ai/IntaRNA/OligoGym/siRBench are clean; RNAiSpline, SiaRNA,
   shRNAI carry no license (internal tier). Classical plant servers (pssRNAit, psRNATarget,
   E-RNAi) are dead; live arm = TargetFinder/dsRIP/si-Fi21/WMD3. No open-source siRNA immune
   scanner exists — implemented from verified motifs (UGUGU/TLR7-8 PMIDs 15778705, 15723075;
   TLR3 length class PMID 18368052; RIG-I IVT-only PMID 17038590). No GalNAc/delivery
   sequence predictor exists — chemistry layer stays rules-based.
2. **Benchmark integrity:** Huesken-2005 data leaks into nearly every learned predictor;
   clean cohorts are Simone/Sciabola-322 and CMsiRNAdb-43k. FDA GINAS + EMA EPAR systematic
   names give verified sequences + decoded modification maps for all 7 approved siRNA drugs.
3. **Executed results:** clean predictor AUC 0.7021 (Simone); generator clean AUC 0.760 with
   measured-top-10 at median 97.5th percentile (HIF1A); approved-drug sites ranked #62/#107
   of 598 (TTR); target-level off-target gate saturation discovered (HIF1A) driving the
   cohort-relative re-anchoring design; E4e RNAhybrid build defect found by end-to-end
   validation.

## Open work

Backlog #1–#4 (overhang intake gate; viability threshold evidence; per-target off-target
calibration; RNAhybrid fix); chemistry-aware arm (CMsiRNAdb); agent-level evaluation
(TxBench-OD-style); wet-lab validation of the selected panels.
