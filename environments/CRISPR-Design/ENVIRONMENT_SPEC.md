# CRISPR Design — Environment Specification

**Environment ID:** `crispr-design`

**Status:** In Progress — partial runtime, executed computational model benchmarks.
Protocol v0.1 (draft — no engine freeze yet); thresholds DRAFT v0.1
(calibrate-then-freeze). Active benchmark evidence is the [completed-only
registry](benchmark/BENCHMARK_RUNS.md): seven completed native-model/endpoint
evaluations, with per-task result records under [results/](results/README.md) and older
mixed Run-2/Run-3 reports preserved in [execution_history](execution_history/before_completed_only_20261112T061830Z/README.md).
Model benchmarks validate endpoints, not design applications, and do not activate every
application adapter or freeze the DRAFT gates; unimplemented stages stay `NOT_RUN(reason)`
/ `NOT_IMPLEMENTED`. No experimental validation is claimed.

**Intended runtime claim (when implemented):** computational guide-RNA candidate generation,
multi-dimensional evaluation and requirement-aware ranking for CRISPR design tasks across
editing modalities. This specification delivers no experimentally validated editing, no
delivery prediction, no clinical or therapeutic qualification, and no off-target-safety
proof (in-silico scores are prioritization only — Kaufmann 2026).

## 1. Objective and supported modes

Given a target gene/locus (or supplied candidate spacers), a modality/application and user
requirements, produce up to K diverse guide candidates with per-dimension evaluation
evidence and a requirement-ranked, gate-surviving shortlist. Every delivered result carries
its evidence tier; purely computational outcomes cap at `NEEDS_EXPERIMENTAL_VALIDATION`.

| Mode | Trigger | Path |
| --- | --- | --- |
| DESIGN | target + requirements | brief → resolve/verify → enumerate → battery → staged ranking → deliver |
| EVALUATE | supplied spacers + property question | run only the requested battery stages; native units; no generation |
| EXPLORATORY | target only ("explore", "don't know what matters") | multi-strategy loop → consensus panel + proposed brief (§5) |
| BENCHMARK | "compare to published" | same-side protocol: published and our candidates through the identical battery (§7) |
| AUDIT | capability/gate question | registry + status report |

## 2. Inputs: user versus environment

| User supplies | Environment prepares |
| --- | --- |
| Gene/locus or sequence; organism (human default); genome assembly (GRCh38 default) | Exact versioned transcript + exon structure (GENCODE 49 local); isoform decision surfaced, never silently chosen |
| Modality/application (knockout, base edit, prime edit, HDR, CRISPRi/a, CRISPRoff, Cas13, diagnostics, library); nuclease/editor | Application profile: required stages, default hard vetoes and weights (§4); modality router for correction requests (edit type → editor class) |
| Priorities: hard vetoes, dimension weights, minimum standards — when known | Requirement brief parsed, echoed, confirmed and hashed into provenance; application defaults proposed where the user is silent |
| Variant objective (allele-specific / correction), when applicable | Reference-verified variant (ClinVar/dbSNP + VEP) before any allele-selective design; WT-vs-mutant discrimination assay at the PAM/spacer |
| Candidate spacers (EVALUATE mode) | Alphabet/orientation checks; only the requested stages |
| Panel size, review-window depth | Defaults per application |

Ambiguity in mode or application produces exactly one clarifying question round; essential
unresolved ambiguity produces `NEEDS_INPUT`. Non-human targets route to gated/inactive
profiles (plant inactive; pathogen diagnostics review-only; microbial via the dedicated
task) rather than model extrapolation.

### Requirement brief and autonomous resolution

The resolved brief follows [requirement_brief.schema.json](config/requirement_brief.schema.json).
The agent resolves settings in this order: explicit user requirements → application profile
defaults → documented reference evidence; adopted settings are recorded as adopted, never as
user requirements or measured properties. User `min_standards` may tighten gates; loosening
requires explicit user instruction, logged. The confirmed brief binds the run by hash.

## 3. Stage-specific execution (core battery)

```text
00_inputs/
  requirement_brief.json      confirmed brief (hashed)
  reference.fa                exact genomic/transcript reference (DNA)
  annotation.gtf|csv          versioned transcript/exon structure
  variant.json                only for allele-selective objectives (verified)
  candidate_pool.csv          enumerator output (all PAM-adjacent windows retained)
  thresholds.json             DRAFT gate set in force (copy-on-use; version-stamped)
  resolution_decisions.json   sources, adopted settings, assumptions
```

Battery stages (per candidate; per-dimension outputs never blended except the disclosed
ranking view of §4):

| Stage | Content | Endpoint semantics |
| --- | --- | --- |
| E1 | validation: alphabet, spacer/PAM orientation, coordinates, exon/CDS consequence, isoform coverage | pass/reject with reasons |
| E2a–c | on-target activity: ≥2 independent endpoints — **Run1-verified local set: RuleSet1, RuleSet3-Sequence (Hsu2013/Chen2013), CRISPRater (U6) + CRISPRscan (declared T7/IVT-context column)**; {CRISPRon, DeepSpCas9, RS2/Azimuth, DeepHF (variant), DeepCpf1} activate on upstream installs (pinned crisprScore 1.17.2 exports only: CasRxRF, CFD, CRISPRater, CRISPRscan, DeepHF*, EnPAMGB*, Lindel, MIT, RuleSet1, RuleSet3 — *env-pending) — separate columns, native units, **never averaged**; expression-system context declared | scores + model identity |
| E3a | genome-wide off-target enumeration: ≤3-mismatch, both strands, intended-locus exclusion (Bowtie 1 local / CRISPRitz with VCFs + bulges for variant-aware tasks) | hit counts by mismatch class; heuristic caps disclosed |
| E3b | off-target pair scoring: CFD (baseline) + Elevation/ElevationSC (aggregate); CRISOT optional (CC BY-NC — research-internal only, never redistributed) | pair scores + aggregate specificity |
| E3c | variant-aware layer (allele/therapeutic tasks): CRISPRitz/CRISPRme VCF-panel search | ancestry/allele off-target nominations |
| E4 | indel outcome: Lindel frameshift probability + 1-bp insertion profile | probabilities (KO tasks) |
| E5 | application layers: modality router; BE editing-window/bystander enumeration (BE-Hive-family models); PE pegRNA (PBS/RTT) design + PRIDICT2.0/DeepPrime efficiency; HDR donor rules (asymmetry, arm composition); CRISPRi/a TSS-window + chromatin context; CRISPRoff rules (±500 bp TSS window, NDR, functional-CpG density); Cas13 spacer nt 15–21 intolerance; diagnostics primer–crRNA compatibility; library multi-targeting avoidance | typed outputs per modality |
| E6 | physico-chem: GC (40–80% band, flagged not hard-gated), homopolymer runs (≥4 T's — Pol III termination risk), self-complementarity, Tm (method stated) | values + flags |

Failed/missing stages are `NOT_RUN(reason)` — never imputed; a failed stage blocks only
dependent claims.

## 4. Requirement-aware ranking (protocol draft)

R1 hard vetoes: brief ∪ application defaults ∪ calibrated gates (thresholds DRAFT until
first benchmark execution). R2: requirement-weighted **cohort-percentile** ordering
(per-target normalization), with mandatory ±25% weight-perturbation stability; unstable
orderings are labeled and the per-dimension table becomes the decision basis; the weighted
score is disclosed as a preference view, never an efficacy estimate. R3: site-diverse,
PAM-distinct panel. Implementation lands with the runtime phase (`runtime/`).

## 5. Exploratory design loop (protocol draft)

X1 strategy partition (model-led, rule-led, property-envelope sweeps, diversity-led
mid-tier) → X2 cheap funnel (GC/poly-T/exact-match off-target) → X3 tiered gate descent
with declared screen budgets → X3b adaptive constraint re-anchoring (PROPOSED, gates
unchanged, `rel_gate_only` marks) → X4 brief-variant search → X5 synthesis: consensus
panel, divergence, Pareto front, proposed brief. Selection never consults measured or
published outcomes; benchmark labels join post-hoc only.

## 6. End-to-end execution

DESIGN: resolve brief → verify reference → enumerate (all windows retained) → battery →
ranking → deliver (candidates CSV, per-dimension values, flags, `NOT_RUN` list, provenance
block, evidence tier, next-evidence recommendation per application). Outputs land in a
fresh run directory; inputs are read-only.

## 7. Benchmarking (executed local registry + published anchors)

Executed local evidence lives in the [completed-only registry](benchmark/BENCHMARK_RUNS.md):
seven completed native-model/endpoint evaluations (RS3 Sequence, CRISPRon, CFD2016,
BE-Hive BE4, PRIDICT2.0, DeepPrime PE2, RFcombined), each with predictions, metrics,
protocol manifest and limitations attached. These are endpoint-level model benchmarks —
they do not validate any full design application. Older mixed evidence (Run-2/Run-3
per-task comparisons, replays, blocked attempts) is preserved in
[execution_history](execution_history/before_completed_only_20261112T061830Z/README.md).
All published numbers below are source-verified (see
[benchmark/README.md](benchmark/README.md) and [research references](../../research/CRISPR-Design/references.md)).

| Anchor | Cohort | Independence | Published headline |
| --- | --- | --- | --- |
| Kim-2019 / DeepSpCas9 | 12,832 paired sgRNA–target, HEK293T (SRA SRP150719) | single-lab, paired library | CV Spearman up to ~0.77; default transfer-test set |
| DeepHF | 80,263 pairs, WT/eSpCas9(1.1)/SpCas9-HF1 (PRJNA522677) | single-lab per-variant | held-out ρ 0.86–0.87 (internal; 0.4–0.6 cross-study) |
| RS3 corpus | 46,526 train + 23,629 held-out + 84,609 tiling (PRJNA832308) | tracrRNA-annotated protocol | RS3 Seq+Target > RS2 (p<0.002) |
| **Konstantakos 2022** | 6 datasets disjoint from every tool's training | **independent** | DeepHF/DeepSpCas9 consistently top; DeepCRISPR best on 1/6; ceiling ρ≈0.7 |
| CHANGE-seq | 110 guides / 201,934 off-target sites (PMC7652380) | cell-free truth | SNVs affect ~15.2% of sites; chromatin explains cell activity |
| **Kaufmann 2026** | 3,827 deep-sequenced sites, 26 gRNA/Cas9 combos | **independent, 14 tools** | recall ≈77% @ top-500; weak score↔indel correlation |
| BE-Hive | 38,538 targets, 11 editors (PMC7384975) | single-platform | outcome R≈0.9 / efficiency R≈0.7 |
| BE-dataHIVE | 460,000+ combos, 32 editors, 5 studies harmonized | aggregate/harmonized | fair-comparison substrate |
| PRIDICT2.0 | 92,423 pegRNAs / 13,349 pathogenic mutations | multi-context | ρ 0.85 intended / 0.78 purity |
| DeepPrime | 338,996 pairs, 8 PE systems × 7 cell types | multi-system | breadth standard |
| Horlbeck 2016 | K562 CRISPRi tiling + genome-wide γ-scores | single-lab | compact 5-guide libraries detect >90% essential genes |
| Nuñez 2021 CRISPRoff | ~116k-sgRNA tiling + 21,378-element screen (GSE168012) | single-lab | 3 design rules |
| TIGER | ~200,000 RfxCas13d guides ± mismatches/indels | single-lab | current Cas13 reference |
| EasyDesign | 11,496 validated Cas12a-detection cases | single-lab | ρ 0.812; 4 held-out pathogens |

Local benchmark plan (pre-registered; partially superseded by the executed registry
above): Konstantakos-protocol replication
on Kim-2019 held-out; CFD-vs-Elevation pair scoring on CHANGE-seq 110-guide set;
BEDICT2.0/DeepBE on BE-dataHIVE held-out editors; PRIDICT2.0 self-hosted CLI on Mathis
held-out — the unexecuted arms remain open backlog (see
[STATUS](STATUS.md#open-backlog)).

## 8. Scope gates and hard rules

- Pathogen-targeting diagnostics sequence design (task 010): **review-only**; no generation
  or evaluation. Tool presence (EasyDesign/PrimedSherlock) is not authorization.
- Plant/crop editing (task 012): **inactive** pending a validated species adapter; human
  activity models never transfer (Haeussler 2016 cross-expression finding).
- Allele-selective claims require a reference-verified variant and an explicit
  WT-vs-mutant objective; therapeutic tasks additionally require the variant-aware
  off-target layer (E3c).
- Off-target results are prioritization, never safety claims; no negative in-silico screen
  proves specificity (Kaufmann 2026).
- No therapeutic guide sequence is public — benchmarks anchor on target/strategy, never on
  invented sequences.
- License tiers are binding: CRISOT (CC BY-NC) and no-license repos (DeepBE, yachielab,
  Cas13design mirror) never enter redistributed artifacts; their outputs carry provenance
  only. deepcrispr.info / PRIDICT web are research-use.
- Endpoints are never averaged or ensembled; `best_design` stays null without experimental
  evidence.

## 9. Failure handling

A broken backend blocks only its dependent dimension (`NOT_RUN(reason)`). Gate saturation
is diagnosed and surfaced — under DESIGN it yields an honest no-deliverable outcome; under
EXPLORATORY it triggers proposed re-anchoring. Recovery never invents scores, pads
candidates or silently changes thresholds. Known pre-runtime gaps: bulge-aware search and
variant-aware layers are documented as NOT_IMPLEMENTED (Bowtie-1 ungapped is the current
enumeration base, per the verified prior-run policy).
