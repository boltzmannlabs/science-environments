# Task: crispr_knockout_002

**Task family:** application-aware CRISPR design — **knockout / gene disruption (incl.
functional-genomics use)**. **Status:** specification phase; workflow defined; scoring
runtime pending; no executed benchmark. Core battery shared; only the requirements below
differ. Start from the [general task](001_crispr_design_general.md) for mode routing.

## Description

Coding-frame disruption of a resolved human target under the user's confirmed brief:
enumerate SpCas9 (or variant/Cas12a) spacers, evaluate through the fixed battery under
draft gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at
`NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: early-exon placement with all-isoform coverage;
frameshift outcome (Lindel) emphasized; ≥2 independent on-target endpoints (DeepSpCas9 +
CRISPRon or RS2/RS3, never averaged); protein-position context.

## Target

Resolved per request — never defaulted. Example genes (KIF11, KRAS) illustrative only
([002 example brief](../config/002_knockout.request.example.json)).

- **Reference:** versioned transcript(s) + spliced-exon validation (pipeline evidence from
  the prior verified run: transcript sequence vs spliced genomic exons, CDS translation checks).
- **Default vetoes:** off_target_exact_match, poly_t_termination_risk.
- **Default weight emphasis:** on_target .35–.40 / specificity .25–.30 / outcome_quality .20–.30 / context .10.

## Design Constraints

*Universal contract from [task 001](001_crispr_design_general.md) applies in full.* Modality-specific layers:

**Modality & nuclease context**
- Nuclease declared per run: WT SpCas9 default (20-nt + NGG); eSpCas9(1.1)/SpCas9-HF1
  scored with DeepHF-class variant models (per-variant endpoints, never mixed into one
  column); Cas12a with DeepCpf1-class models (23-nt + TTTV; note PAM is 5′ of the
  protospacer — orientation mapping mandatory).
- **No verified activity model exists for SpG/SpRY/HypaCas9** — near-PAMless design runs
  enumeration + off-target + physico-chem only, with the model gap stated per deliverable;
  relaxed/custom PAMs use enumeration-only mode (CRISPOR/CHOPCHOP conventions).
- Paired-nickase designs are outside battery v0.1 (stated boundary, not approximated).

**Target placement (disruption logic)**
- Placement favors early constitutive coding exons so a frameshift disables all major
  isoforms; the isoform-coverage table is part of every candidate record — a guide
  covering a subset of protein-coding isoforms is flagged, never silently accepted.
- Cut-site protein position recorded (RS2-lineage positional context); guides whose only
  consequence is an in-frame lesion near the C-terminus are down-ranked with reasons.
- Alternative first exons / alternative starts surfaced when the isoform set includes them.

**Outcome constraints**
- Frameshift probability from Lindel (local verified backend) is a first-class endpoint;
  DRAFT floor 0.60 before calibration — treated as a ranking constraint, not a promise of
  knockout; indel profile (incl. 1-bp insertion fractions) reported with it.
- On-target endpoints: DeepSpCas9 + CRISPRon or RS2/RS3 (≥2, separate columns); CRISPRon
  column carries the Kim-2019-in-training disclosure whenever Kim data is involved.

**Specificity constraints**
- Bowtie-1 ungapped ≤3 mm both strands, intended locus excluded, heuristic caps disclosed;
  bulges NOT_EVALUATED (disclosed cap); CFD + Elevation pair/aggregate reported separately.
- Guides with additional perfect matches genome-wide are vetoed (multi-cut confound —
  Kuscu 2019 lineage applies to screen use as well).

**Physico-chemical filters (ranking constraints, not silent drops)**
- GC 40–80% band (RS2-era convention; flag outside band); ≥4 consecutive T's flagged
  (Pol III termination risk — CRISPOR convention); homopolymer runs and
  self-complementarity flagged; Tm reported with method stated.

**Benchmark discipline**
- Training-disjoint splits mandatory for any benchmark arm (the DeepCRISPR lesson — best
  on only 1/6 independent datasets, Konstantakos 2022); DeepCRISPR itself excluded as a
  scoring endpoint (cautionary baseline only).

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm application=knockout; resolve priorities (defaults above where user silent). | Confirmed hashed brief. |
| 2. Verify reference | Transcript + exon structure; isoform decision surfaced. | Verified reference or stage blocker. |
| 3. Enumerate | All PAM-adjacent windows in CDS/early exons; all retained. | `candidate_pool.csv`. |
| 4. E1 validation | Alphabet/orientation/coordinates/consequence/isoform coverage. | pass/reject with reasons. |
| 5. E2 on-target | ≥2 independent endpoints + model identity + expression-system tag. | Separate score columns. |
| 6. E3 off-target | Enumeration + CFD + Elevation aggregate; intended locus excluded. | Counts + pair/aggregate scores. |
| 7. E4 outcome | Lindel frameshift + indel profile. | Probabilities. |
| 8. E6 physico-chem | GC band, poly-T, self-complementarity, Tm. | Values + flags. |
| 9. Gates (R1) | DRAFT gates ∪ brief vetoes ∪ defaults. | Survivor set + decision log. |
| 10. Rank (R2/R3) | Cohort-percentile weighting; ±25% stability; site-distinct panel. | Ranked table + stability report. |
| 11. Deliver | Panel + evidence + provenance + tier + next-evidence recommendation. | Complete typed bundle. |

## Expected Output

Fresh run directory: ranked spacers (20-nt + PAM + coordinates + consequence),
per-dimension evidence, gate log, stability report, provenance, honest tier.

## Constraints

On-target endpoints never averaged; off-target = prioritization only; nuclease model gaps
stated, never approximated; DeepCRISPR excluded as a scoring endpoint (cautionary
baseline only).

## Important Instructions

Published-anchor status (strongest task): Kim-2019 (12,832 paired measurements, SRA
SRP150719) is the reference standard; DeepHF (80,263 pairs) for variants; RS3 corpus for
rules; **Konstantakos 2022 defines the evaluation protocol** (6 training-disjoint sets,
Spearman + nDCG@20, realistic ceiling ρ≈0.7). Local benchmark plan pre-registered in
[benchmark/BENCHMARK_RUNS.md](../benchmark/BENCHMARK_RUNS.md) — Run slots NOT_EXECUTED.
