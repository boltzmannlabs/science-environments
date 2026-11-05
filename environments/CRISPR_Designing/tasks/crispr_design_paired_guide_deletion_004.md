# Task: crispr_design_paired_guide_deletion_004

**Task family:** application-aware CRISPR guide design — **Paired-guide genomic deletion design**.  
**Status:** In Progress; protocol v1.0, computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only application-specific requirements differ. Start from the [general task](../gene_editing_rna_001.md) for mode routing.

## Description

Design compatible pairs of guides intended to flank a specified genomic interval. Rank pairs based on individual guide evidence, target-boundary fidelity, pair geometry, specificity, and predicted interval consequence. The deliverable is a paired candidate panel; deletion formation and repair outcomes remain experimental questions.

Application-specific requirements: pair-level interval coordinates; orientation and spacing compatibility; pairwise off-target review; target-boundary and transcript consequence reporting; individual-guide evidence retained.

## Target and Reference (Fixed)

This task uses a fixed human **PCSK9 exon-1 deletion** design scenario. Do not ask the user to supply a target interval.

- **Organism:** Homo sapiens
- **Gene:** `PCSK9`
- **Reference assembly:** GRCh38
- **Transcript:** `NM_174936.4` (RefSeq; verify accession and sequence)
- **Target interval:** the annotated first protein-coding exon of the selected transcript, mapped to GRCh38 from the pinned annotation release; record exact 1-based closed genomic coordinates after mapping
- **Reference source:** NCBI RefSeq and GRCh38
- **Benchmark purpose:** evaluate pair construction, interval boundary reporting, and pair-level evidence on a fixed exon target; do not claim a published deletion outcome unless a supplied reference dataset supports it
- **Fixed-input behavior:** derive the genomic interval from this transcript/exon definition and validate it. If the mapping is ambiguous or unavailable, stop with `REFERENCE_VALIDATION_FAILED`; do not request a new interval.

- **Default vetoes:** unresolved interval; incompatible PAM; invalid guide; pair does not flank the target; unacceptable individual or pair-level specificity.
- **Default weight emphasis:** boundary fidelity .30 / pair compatibility .25 / specificity .25 / guide quality .20.
## Design Constraints

- Evaluate both guides independently and the pair jointly.
- Report predicted excision boundaries and interval size; do not assume exact repair.
- Do not infer deletion efficiency by multiplying guide scores unless a validated model is specified.
- Account for possible alternative repair outcomes and unintended rearrangements as limitations.
- Preserve alternate pairs with distinct boundaries where useful.

## Required Execution Steps

| Step | What must happen | Required result |
|---|---|---|
| 1. Route + brief | Confirm `mode=paired_deletion`; resolve target interval, nuclease, and boundary criteria. | Confirmed, hashed brief. |
| 2. Verify reference | Verify assembly, interval coordinates, and annotation. | Verified interval or blocker. |
| 3. Application preparation | Define flank regions and pair compatibility rules. | Application readiness record. |
| 4. Generate | Generate candidate guides on both sides in a fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Score and validate each guide; assess specificity. | Per-guide evidence and flags. |
| 9. Application layer (E5) | Assemble compatible pairs; annotate interval size, boundaries, orientation, and pair-level risks. | Pair table and interval report. |
| 10. Gates (R1) | Apply individual-guide and pair-specific frozen gates. | Survivor pairs and decision log. |
| 11. Rank (R2/R3) | Rank pairs using confirmed weights; test pair geometry and weight stability. | Ranked pairs and stability report. |
| 12. Deliver | Provide pair alternatives, individual evidence, predicted interval, and limitations. | Complete typed bundle. |

## Expected Output

Fresh run directory containing `candidate_pool.csv`, `ranked_pairs.csv`, `individual_guide_evidence.csv`, `predicted_intervals.csv`, `off_target_summary.csv`, `gate_log.json`, `ranking_stability.json`, `provenance.json`, and `report.md`.

## Constraints

Computational design only. No guarantee of deletion or exact repair. Any wet-lab execution requires independent institutional review and an appropriate approved protocol.

## Important Instructions

Do not rank a pair solely from guide scores. Report both component guides and pair-specific criteria. Distinguish predicted interval deletion from observed genotype and phenotype.

---
