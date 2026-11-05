# Task: crispr_design_cas13_rna_targeting_005

**Task family:** application-aware CRISPR guide design — **Cas13 RNA targeting / knockdown**.  
**Status:** In Progress; protocol v1.0, computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only application-specific requirements differ. Start from the [general task](../gene_editing_rna_001.md) for mode routing.

## Description

Design and rank Cas13-compatible guides for targeting a resolved RNA transcript. Report transcript-level target coverage, sequence accessibility/context where supported, specificity against related transcripts, and guide quality. The deliverable is a computational candidate panel with evidence tiers; RNA knockdown is not presumed.

Application-specific requirements: RNA target transcript verification; isoform coverage; transcriptome-wide near-match review; RNA context/accessibility evidence where available; collateral-activity caveat appropriate to the selected system.

## Target and Reference (Fixed)

This task uses a fixed human **KRAS transcript** RNA-targeting scenario. Do not ask the user to provide a transcript or gene.

- **Organism:** Homo sapiens
- **Gene:** `KRAS`
- **Reference transcript:** `NM_004985.5` (RefSeq; verify accession and sequence)
- **Target:** full reference transcript for the selected accession; report the isoforms included in the comparison set
- **Reference source:** NCBI RefSeq transcript sequence
- **Cas13 system:** use the system specified in the environment tool profile; if no compatible Cas13 profile is configured, stop with `TOOL_PROFILE_REQUIRED` rather than asking for a target
- **Fixed-input behavior:** resolve and validate the transcript sequence automatically. Stop with `REFERENCE_VALIDATION_FAILED` if accession/version or transcript sequence does not match.

- **Default vetoes:** unresolved transcript; incompatible guide format; invalid target sequence; unacceptable transcriptome matches.
- **Default weight emphasis:** transcript specificity .35 / target compatibility .25 / guide quality .20 / isoform coverage .20.
## Design Constraints

- Use RNA-targeting rules for the selected Cas13 system; do not apply DNA nuclease PAM assumptions blindly.
- Report transcript isoforms and sequence matches explicitly.
- Distinguish predicted target engagement from measured knockdown.
- Include system-dependent collateral activity as a limitation, not a universal assertion.
- Context/accessibility scores must identify their source and limitations.

## Required Execution Steps

| Step | What must happen | Required result |
|---|---|---|
| 1. Route + brief | Confirm `mode=cas13`; resolve Cas13 system, transcript, and priorities. | Confirmed, hashed brief. |
| 2. Verify reference | Verify transcript sequence, version, and isoforms. | Verified `transcript.fa` or blocker. |
| 3. Application preparation | Define compatible target windows and transcriptome comparison set. | Application readiness record. |
| 4. Generate | Generate Cas13-compatible candidates in a fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Validate format, assess guide quality, and evaluate sequence specificity. | Per-dimension evidence and flags. |
| 9. Application layer (E5) | Annotate isoform coverage and supported RNA context/accessibility. | RNA-context report. |
| 10. Gates (R1) | Apply frozen gates and transcript-specific vetoes. | Survivor set and decision log. |
| 11. Rank (R2/R3) | Rank under confirmed weights; assess isoform and weight sensitivity. | Ranked candidates and stability report. |
| 12. Deliver | Provide candidate panel, transcript matches, evidence, and limitations. | Complete typed bundle. |

## Expected Output

Fresh run directory containing `candidate_pool.csv`, `ranked_candidates.csv`, `transcript_match_summary.csv`, `isoform_coverage.csv`, `gate_log.json`, `ranking_stability.json`, `provenance.json`, and `report.md`.

## Constraints

Computational scope only. RNA-targeting design does not imply DNA editing. Cas13 system assumptions and any collateral-risk statements must be sourced and versioned.

## Important Instructions

Report the exact target transcript and off-target transcript matches. Do not claim knockdown or specificity from sequence prediction alone. Benchmark against an RNA-targeting reference dataset suitable for the selected Cas13 system.

---
