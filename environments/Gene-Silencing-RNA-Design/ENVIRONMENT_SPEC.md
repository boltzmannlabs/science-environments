# Gene Silencing RNA Design — Environment Specification

**Environment ID:** `gene-silencing-rna-design`

**Status:** In Progress — protocol v1.2, frozen gates v1.0, executed computational benchmarks on public data included.

**Intended runtime claim:** computational candidate generation, multi-dimensional evaluation and requirement-aware ranking for human siRNA design. This specification delivers no experimentally validated knockdown, no delivery prediction and no therapeutic qualification.

## 1. Objective and supported modes

Given a target gene (or supplied candidate sequences), an application and user requirements, produce up to K diverse siRNA candidates with per-dimension evaluation evidence and a requirement-ranked, gate-surviving shortlist. Every delivered result carries its evidence tier; purely computational outcomes cap at `NEEDS_EXPERIMENTAL_VALIDATION`.

| Mode | Trigger | Path |
| --- | --- | --- |
| DESIGN | target + requirements | brief → resolve/verify → generate → battery → staged ranking → deliver |
| EVALUATE | supplied sequences + property question | run only the requested battery stages; native units; no generation |
| EXPLORATORY | target only ("explore", "don't know what matters") | multi-strategy loop → consensus panel + proposed brief (§5) |
| BENCHMARK | "compare to published" | same-side protocol: published and our candidates through the identical battery (§7) |
| AUDIT | capability/gate question | registry + status report |

## 2. Inputs: user versus environment

| User supplies | Environment prepares |
| --- | --- |
| Gene symbol or sequence; organism (human default) | Exact versioned transcript (GENCODE v50 local / Ensembl via ToolUniverse); isoform decision surfaced, never silently chosen |
| Application and objective, when known | Application profile: required stages, default hard vetoes and weights (§4) |
| Priorities: hard vetoes, dimension weights, minimum standards — when known | Requirement brief parsed, echoed, confirmed and hashed into provenance; application defaults proposed where the user is silent |
| Allele/variant objective, when applicable | Reference-verified variant (ClinVar/dbSNP + VEP) before any allele-selective design; mutant-vs-WT duplex ΔΔG assay |
| Candidate sequences (EVALUATE mode) | Alphabet/orientation checks; only the requested stages |
| Review-window depth, panel size | Defaults per application (review window ≥100 recommended — approved-drug sites ranked #62 and #107 of 598 in the TTR benchmark) |

Ambiguity in mode or application produces exactly one clarifying question round; essential unresolved ambiguity produces `NEEDS_INPUT`. Non-human targets route to gated/inactive profiles rather than model extrapolation.

### Requirement brief and autonomous resolution

The resolved brief follows [requirement_brief.schema.json](config/requirement_brief.schema.json). The agent resolves settings in this order: explicit user requirements → application profile defaults → documented reference evidence; adopted settings are recorded as adopted, never as user requirements or measured properties. User `min_standards` may tighten frozen gates; loosening requires explicit user instruction, logged. The confirmed brief binds the run by hash.

## 3. Stage-specific execution

```text
00_inputs/
  requirement_brief.json      confirmed brief (hashed)
  transcript.fa               exact versioned reference (RNA, AUGC)
  variant.json                only for allele-selective objectives (verified)
  candidate_pool.csv          generator output (all windows retained)
  thresholds.json             frozen gate set in force (copy-on-use; version-stamped)
  resolution_decisions.json   sources, adopted settings, assumptions
```

Battery stages (per candidate; per-dimension outputs never blended except the disclosed ranking view of §4):

| Stage | Content | Endpoint semantics |
| --- | --- | --- |
| E1 | validation: alphabet, orientation, pairing, coordinates, CDS/UTR | pass/reject with reasons |
| E2a/E2b | efficacy: RN.Ai-Predict (% inhibition) and OligoFormer (scaled) — two independent endpoints | native units; N-padded context flagged lower-bound; never averaged |
| E3a–c | structure: guide MFE (RNAfold), duplex ΔG (RNAduplex), accessibility (RNAplfold, W/L/u declared) | kcal/mol / probabilities |
| E4a | both-strand near-match screen (bowtie2, ≤1 mismatch, ≤50 hits, heuristic cap disclosed) | hit counts; per-target saturation diagnosed, not silently passed |
| E4b | explicit 6/7/8-mer seed occurrence counts vs declared reference | counts |
| E4c/d | siSPOTR POTS (guide pos 2–8; 2012-frozen tables) · 6merDB viability (pos 2–7; cancer-line scaffold caveat) | percentile / % viability |
| E4e | RNAhybrid hybridization (SIREN conventions) | **currently NOT_RUN(broken-binary)** — build/adapter defect, §STATUS |
| E5a | immune hazard scan (`runtime/immune_scan.py`): UGUGU (TLR7/8), GU-fraction cohort decile, U-rich 5', ≥21-nt TLR3 class flag, IVT-only 5'ppp | typed flags; hazard filter, not probability |
| E5b | allele discrimination: verified variant + RNAduplex ΔΔG mutant vs WT | energies + margin |
| E5c | chemistry/delivery context: ESC/ESC+ rule cards, conjugate annotations | context only; no predictor exists — stated, never approximated |
| E5d | tissue expression context (GTEx/HPA via ToolUniverse) | qualitative context |
| E6 | physico-chem: GC, Tm (method stated), homopolymers, self-complementarity | values + flags |

Generation uses the local OligoFormer/RNA-FM installation (research-use; score semantics ×1.341 disclosed). Failed/missing stages are `NOT_RUN(reason)` — never imputed; a failed stage blocks only dependent claims.

## 4. Requirement-aware ranking (protocol v1.1)

R1 hard vetoes: brief ∪ application defaults ∪ frozen gates. R2: requirement-weighted **cohort-percentile** ordering (per-target normalization), with mandatory ±25% weight-perturbation stability; unstable orderings are labeled and the per-dimension table becomes the decision basis; the weighted score is disclosed as a preference view, never an efficacy estimate. R3: seed-distinct, site-diverse panel. Implementation: `runtime/rank_by_requirements.py`.

## 5. Exploratory design loop (protocol v1.2)

X1 strategy partition (model-led, rule-led, property-envelope sweeps, diversity-led mid-tier) → X2 cheap funnel (immune/GC/POTS/viability) → X3 tiered gate descent with declared screen budgets → **X3b adaptive constraint re-anchoring**: when an absolute gate is unsatisfiable within budget, characterize the target's own distribution on a stratified sample, re-anchor cohort-relative (lowest quartile), mark candidates `rel_gate_only`, record the adaptation as PROPOSED — frozen gates unchanged → X4 brief-variant search (safety/balanced/efficacy with stability reports) → X5 synthesis: consensus panel, divergence, Pareto front, proposed brief. Selection never consults measured or published outcomes; benchmarks join labels post-hoc only. Implementation: `runtime/explore_design.py`.

## 6. End-to-end execution

DESIGN: resolve brief → verify reference → generate (all windows retained) → battery → ranking → deliver (candidates CSV, per-dimension values, flags, `NOT_RUN` list, provenance block, evidence tier, next-evidence recommendation per application). Outputs land in a fresh run directory; inputs are read-only; ambiguous submissions are resolved by status query, never resubmission.

## 7. Benchmarking (executed, included in [benchmark/](benchmark/))

All benchmarks ran under frozen `engine-v1.0.0_protocol-v1.0` gates with no tuning; thresholds and weight vectors are recorded with each artifact set.

| Benchmark | Cohort | Independence | Headline result |
| --- | --- | --- | --- |
| Predictor validation | Simone/Sciabola-322 (Hep3B measured efficacy) | **clean** (outside all local models' training) | RN.Ai AUC **0.7021** / Pearson 0.5074 / Spearman 0.3930 (n=322) |
| Descriptive replay | Mix-469 | exposed | OligoFormer AUC 0.8437 · RN.Ai 0.8195 (published refs 0.8163/0.818 — not like-for-like) |
| Same-side battery | 7 approved siRNA drugs (FDA GINAS/EPAR-verified sequences + decoded modification maps) vs our TTR top-20 | anchor | efficacy bands coincide (RN.Ai median 84.3 vs 84.5); all drugs UGUGU-free; gates flag 6/20 of ours |
| Generator vs approved sites | TTR pool (598 windows) | anchor | vutrisiran site #62/598 (89.6th pct) · patisiran #107/598 (82.1st pct) |
| Case study (DESIGN end-to-end) | HIF1A NM_001530.4 vs 100 clean measured siRNAs | clean | generator's first clean validation: OligoFormer AUC **0.760**/P 0.635; measured-top-10 at median **97.5th percentile** of our ranking; frozen off-target gate saturates for this target (v1.1 backlog) |
| Explorer post-hoc | HIF1A exploratory loop | clean, blind selection | 3/18 gate-re-anchored clean candidates measured **0.92/0.92/0.87** (base rate 0.785) |
| Oncology case studies | HPSE (n=106) + HK2 (n=95) measured siRNAs | clean | rank-recovery median **94.5th/95.1st pct**; per-sequence AUC 0.58–0.72 (target-dependent) |
| Gene-regulation case study | MYC (n=7) measured siRNAs | clean | rank-recovery median **92.6th pct**; discrimination degenerate at n=7 (percentile-only) |
| Functional-genomics panels | seed-distinct panels on 3 pools | clean, overlap-limited | panel picks measured **0.92/0.91** where tiling overlaps (base 0.80) |
| Inflammation scanner | 13 published IFN-inducers (Hornung/Judge/Goodchild) | curated public | frozen UGUGU rule: **specificity 1.00, sensitivity 0.10** — hazard filter; incompleteness measured, not tuned |
| Allele ΔΔG | 26 published allele-guides (Pfister/Sibley/Miller/Alves/Hu) | curated public | ΔΔG direction confirmed: selective **6.7** vs weak **4.7** kcal/mol; Pearson 0.42 (n=5 subset) |
| Neuro EVALUATE | 26 Pfister HTT guides vs reporter IC50 | curated public | context-free RN.Ai Spearman **0.296** (degraded-input lower bound) |
| Bootstrap CIs (2026-11-05) | all gene-level AUCs | — | HIF1A OF [0.615–0.877], RN.Ai [0.639–0.901] exclude 0.5; **HPSE OF [0.465–0.703] includes 0.5** (disclosed) |
| **Large-pool head-to-head (v2)** | 4 genes · 16,802 windows · 308 measured siRNAs; manual vs sub-agent filtering with identical finalist budgets (locus-scoped E4a v1.2.1) | clean, pre-registered | pooled ordering: manual **0.569** [0.476–0.662] vs sub-agent **0.591** [0.488–0.693] — CI-overlap tie at predictor ceiling; sub-agent +0.14 AUC on HK2; panel results in the case folder |

Computational benchmark results are not biological validation; no wet-lab measurement exists for any generated candidate.

## 8. Scope gates and hard rules

- Antiviral/pathogen/pest/infection-host-factor sequence design: **review-only**; no generation or evaluation. Tool presence is not authorization.
- Agricultural/plant/pest: **inactive** pending a validated species adapter and declared references; human models never transfer.
- Allele-selective claims require a reference-verified variant and explicit mutant-vs-WT objective.
- License tiers are binding: proprietary OligoFormer (research use, no redistribution) and no-license models never enter redistributed artifacts; their score outputs carry provenance only.
- Endpoints are never averaged or ensembled; no negative screen proves safety or specificity; `best_design` stays null without experimental evidence.

## 9. Failure handling

A broken tool blocks only its dependent dimension (`NOT_RUN(reason)`). Known: E4e RNAhybrid binary incompatibility (quarantined; backlog). Gate saturation (HIF1A off-target) is diagnosed and surfaced — under DESIGN it yields an honest no-deliverable outcome; under EXPLORATORY it triggers proposed re-anchoring. Recovery never invents scores, pads candidates or silently changes thresholds.
