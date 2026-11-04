


# Task: crispr_design_gene_knockout_003

Task family: application-aware CRISPR design — Gene knockout gRNA design. Status: Proposed; computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only the application-specific requirements differ.

Description

Design and prioritize gRNAs for disruption of a resolved human protein-coding gene using CRISPR-Cas9. The deliverable is a ranked candidate set supported by independent evidence for on-target activity, genomic specificity, and coding-region relevance.

Generate candidate guides across the eligible target region, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked shortlist capped at NEEDS_EXPERIMENTAL_VALIDATION.

Application-specific requirements: coding-region and exon relevance; transcript-coverage reporting; predicted frameshift or loss-of-function context where supported; off-target burden assessment; avoidance of single-guide overclaiming as proof of gene knockout.

Target

Resolved per request — never defaulted.Example gene (KIF11) and any example values are illustrative, not defaults.

Reference: exact versioned human transcript and genome assembly; transcript and target-region sequence hashed into provenance.

Brief: user-confirmed target gene, intended knockout scope, required transcript coverage, and design priorities.

Target region: coding exons or other explicitly specified functional regions.

Default vetoes: invalid guide representation; incompatible PAM; failed sequence validation; unacceptable off-target burden under frozen gates.

Default weight emphasis: specificity and predicted activity; weights resolved through the common ranking contract.

Design Constraints

Representation: SpCas9-compatible guide candidates with explicit spacer and PAM representation.

Targeting: candidate guides must map to the resolved reference and intended target region.

Both strands evaluated where supported by the generator.

Predicted cleavage activity and predicted knockout consequence remain separate endpoints.

Transcript coverage must be reported; a guide targeting one isoform is not assumed to disrupt all isoforms.

Computational predictions do not establish protein-level knockout.

Candidate ranking must not override frozen vetoes.

Required Execution Steps

Step

What must happen

Required result

1. Route + brief

Confirm mode=gene_knockout; resolve target, transcript coverage, and priorities.

Confirmed hashed brief.

2. Verify reference

Verify transcript, genome assembly, target region, and sequence orientation.

Verified reference sequence or stage blocker.

3. Application preparation

Identify eligible coding regions; report exon and transcript coverage; define knockout interpretation.

Application readiness record.

4. Generate

Run local guide generator; retain all eligible windows; use a fresh run directory.

candidate_pool.csv.

5–8. Battery E1–E4

Run common validation, efficacy, structure, and both-strand specificity assessments.

Per-dimension values and flags.

9. Application layers (E5)

Evaluate coding-region relevance, transcript coverage, and predicted knockout context.

Typed application flags.

10. Gates (R1)

Apply frozen gates ∪ brief vetoes ∪ knockout-specific requirements.

Survivor set and decision log.

11. Rank (R2/R3)

Apply confirmed ranking weights and stability analysis.

Ranked table and stability report.

12. Deliver

Report candidate shortlist, evidence, transcript coverage, limitations, and experimental validation requirements.

Complete typed bundle.

Expected Output

Fresh run directory: ranked gRNA candidates with spacer/PAM, genomic coordinates, transcript and exon coverage, per-dimension evidence, gate log, stability report, provenance block, evidence tier, and application-specific next-evidence recommendation.

Constraints

Human reference and scoring models must remain versioned. Off-target predictions are computational estimates. No candidate is reported as experimentally validated unless supported by direct evidence. License tiers bind redistribution.

Important Instructions

Do not deliver a single “best” guide as definitive proof of gene knockout. Report the transcript scope and the assumptions used to interpret predicted loss of function. Candidates remain capped at NEEDS_EXPERIMENTAL_VALIDATION unless independent experimental evidence is available.

Application benchmark status: To be established against an experimentally characterized knockout-guide reference cohort. Benchmark must report the source dataset, guide-level labels, and evaluation metrics.
