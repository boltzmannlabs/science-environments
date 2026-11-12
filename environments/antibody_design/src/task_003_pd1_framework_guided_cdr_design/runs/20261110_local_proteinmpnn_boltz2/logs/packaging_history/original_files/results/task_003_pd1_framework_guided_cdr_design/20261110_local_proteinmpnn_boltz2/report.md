# Task 003 — Historical local CDR-H3-only result

# Task 003 — PD-1: Framework-Guided CDR-H3 Design — Benchmark Result

## Question
Are we better than the published benchmark?

**Published benchmarks (tFold, Nat. Commun. 2025):**
- PD-1 virtual-screening AUROC: 0.76 (panel of 745 antibodies, 27 positives)
- PD-1 top-1% enrichment factor: 7.41 (same panel)
- PD-1 designed-antibody discrimination AUROC: 0.95 (design-campaign analysis)
- Epitope-informed CDR-H3 amino-acid recovery: 0.317 (SAbDab-22-DesignAb aggregate)
- Final H965 ipTM, designed-region confidence, PAE, DockQ: **Not verified** (benchmark states no exact individual values are established)

## What we did (complete pipeline)
- Boltz2 predicted the H965(VH)+H965(VL)+PD-1 complex (H965 from tFold Suppl. Table 6, PD-1 from PDB 4ZQK chain B).
- ProteinMPNN **fixed the entire framework, VL and PD-1** and redesigned **only CDR-H3** (native `AKEYINTFTY`, 10 residues) → 20 designs, 17 unique CDR-H3 sequences.
- Boltz2 predicted H965+PD-1 (reference) and the top-3 candidates + PD-1.

## Candidate-level Boltz2 confidence (our computation, model 0)

| Complex | ipTM | pLDDT | pDE | VH–PD-1 ipTM | VL–PD-1 ipTM |
|---|---:|---:|---:|---:|---:|
| H965 (reference) | 0.878 | 0.920 | 0.404 | 0.727 | 0.724 |
| cand11 | 0.652 | 0.904 | 0.733 | 0.305 | 0.281 |
| cand9 | 0.671 | 0.897 | 0.717 | 0.331 | 0.302 |
| cand2 | 0.760 | 0.927 | 0.568 | 0.489 | 0.459 |

All three redesigned CDR-H3s show **lower** antibody–PD-1 interface confidence (pair-ipTM 0.28–0.49) than H965's native CDR-H3 (0.72). The de novo CDR-H3s did not recapitulate the H965 ligand-binding interface.

## Comparison with the published benchmark — NOT REPRODUCIBLE

| Published metric | Value | Why we cannot reproduce it |
|---|---:|---|
| PD-1 virtual-screening AUROC | 0.76 | Needs the original **745-antibody panel** (27 positives) — not provided. |
| Top-1% enrichment | 7.41 | Same 745-antibody panel — not provided. |
| Design-campaign AUROC | 0.95 | Needs the paper's design-campaign labels — not provided. |
| CDR-H3 AAR (epitope-informed) | 0.317 | Needs the **SAbDab-22-DesignAb** aggregate dataset — not provided. |
| H965 ipTM / confidence / PAE / DockQ | *Not verified* | No published individual H965 value exists to compare against. |

## Verdict
**Cannot compare — the primary benchmarks are aggregate screening/classification metrics requiring a specific labelled panel and dataset that we do not have.** A single candidate cannot yield an AUROC or enrichment factor. We did NOT fabricate one, did NOT assign the paper's aggregate AUROC to a single new candidate, and did NOT infer binding from AUROC or AAR.

## Bottom line
The full design → structure-prediction pipeline ran and produced 20 valid framework-preserved CDR-H3 candidates with measured Boltz2 confidence. The published benchmark metrics remain **not reproducible** with the available inputs. The one concrete, honest observation: the redesigned CDR-H3s score lower on antibody–PD-1 interface confidence than the H965 reference, so this de novo redesign did not reproduce H965's binding interface.

## Artifacts
- Code: src/task_003_pd1_framework_guided_cdr_design/ (design_cdrh3.py)
- Designs: results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/designed_sequences.fasta
- Boltz2: results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/evidence/reference/ and structures/
- Confidence: results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/metrics.json


This is the historical local run. It is separate from the pending platform source run `20261110_pd1_framework_stage0_pending`; no platform candidate metrics are assigned to this result.
