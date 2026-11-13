# CRISPR-Design — First Runs Report (2026-11-10)

Covers: workflow execution (task 002 / KIF11), run-validation tests, new-model
exploration + integration, and the first executed benchmark with published-benchmark
comparison. All numbers traceable to artifacts in this repo or the curation workspace.

---

## 1. Workflow execution — task 002 knockout (KIF11, Run1)

| Stage | Result |
| --- | --- |
| Reference | GRCh38.p14 + GENCODE 49 (symlinked verified prior-run reference; checksum manifest) |
| C1 enumerate | **8,421** canonical NGG windows (locus ±100 bp, both strands) |
| E1 validate | 227 coding-valid (cut site in CDS of ≥1 protein-coding transcript; alphabet + reference round-trip asserted) |
| E2 on-target (6 endpoints, separate columns, native units) | RuleSet1 (0.004–0.93) · RuleSet3-Sequence-Hsu2013 (−2.46…1.28) · CRISPRater (0.42–0.86) · CRISPRscan T7-context (−0.03–0.72) · **CRISPRon (1.9–68.8)** · Lindel frameshift (0.42–0.92) |
| E3 off-target | Bowtie 1.3.1 genome-wide ≤3 mm (index rebuilt — 3.2 Gbp, ~70 min), intended-locus exclusion, NGG-PAM filter, CFD per site |
| Gates (DRAFT v0.1) | exact-match off-target veto · poly-T veto · intended-locus-recovery check |
| R2/R3 ranking | cohort-percentile preference view (weights .35/.30/.25/.10), ±25% stability, site-distinct panel of 6 |

Run-validation suite (`tests/test_first_run.py`, 8 tests): artifacts · independent
coordinate re-extraction from the genome · scorer determinism (RS1+CRISPRater re-score
bit-stable) · **Lindel regression anchor (documented 65-mer → 0.798)** · off-target
positive control (intended locus recovered) + negative control (decoy 20-mer → 0
alignments) · cross-endpoint Spearman · gate conformance · provenance. *(Test outcomes
recorded in the run dir `tests/run_tests.json`.)*

## 2. Issues found and fixed (workflow updates)

1. **Prior-run pipeline never completed** — the inherited "verified" KIF11 run retained
   no candidate outputs and its generation script crashes at transcript-coverage
   (annotation lacks `exon_number`). Fixed (synthesized `exon_index`); its Bowtie genome
   index also wasn't retained → rebuilt. CONTRACTS + curation registry corrected.
2. **crisprScore 1.17.2 method inventory** — namespace-verified: no RS2/Azimuth,
   DeepSpCas9, DeepCpf1 exports (10 scorers only). E2 endpoint set corrected across
   spec/tasks/registry. (EnPAM-GB + CasRxRF present → future task 006/009 upgrades.)
3. **−-strand context-window orientation** — initial seq30/seq35 construction had wrong
   flank coordinates for minus-strand guides; fixed with strand-aware windows and
   offset-integrity assertions on every scored guide.
4. **CRISPRon integration traps** — (a) Keras-3/TF≥2.16 cannot load their pre-2.5
   SavedModels → pinned TF 2.14.1/Keras 2.14; (b) rth.dk CRISPRoff tarball link dead →
   sourced from github.com/RTH-tools-admin/crisproff (GPL-3.0); (c) CRISPRon enumerates
   every NGG window per record (`_p_N` IDs) → join on the exact 30-mer string (fixed in
   both the run script and the benchmark join).
5. **Benchmark label semantics** — GEO GSM read-count columns are QC statistics, not
   editing rates (first-pass `1−filt/raw` gave |ρ|≈0.09 for everything incl. CRISPRon,
   exposing the error). Switched to the authoritative paper-supplementary
   `total_indel_eff`; methodology correction recorded in the benchmark README.

## 3. New-model exploration (source-verified; archived in curation workspace)

**Integrated now:** CRISPRon (AGPL-3.0, internal-use) — actively maintained, in-repo
weights, regression `TEST ok`; internal-test ρ 0.80 / external 0.46–0.68 published.

**Queued (ranked):** Azimuth 2.0 (BSD-3, archived, py2.7) · DeepSpCas9 (MIT subtree,
py2.7/TF1) · **DeepCas12a (Apache-2.0, torch, 2025/26, AP 0.783/AUC 0.868/ρ 0.630)** ·
Elevation pair-scoring (MIT, py2.7, needs Azimuth) · CCLMoff (MIT; weights external,
repro effort).

**Negative results:** DeepHF standalone repo dead (404; registry corrected) · OptiPrime
code exists but no license (blocked) · Graph-CRISPR/CRISMER/CRISPR_HNN/CrnnCrispr no
license · DeepCpf1 subtree unlicensed · CRISPR-LDP/DeepMEns no code found.

## 4. First executed benchmark vs published anchors

**Cohort:** Xiang-2021 TRAP12K surrogate library (HEK293T SpCas9, Day10 +dox),
authoritative `total_indel_eff` labels, n=11,461. One of Konstantakos's six
training-disjoint evaluation sets. Blind join; bootstrap 1000× CIs; no tuning.

| Endpoint | ρ (this run) | 95% CI | vs published |
| --- | --- | --- | --- |
| RS3-Sequence Hsu2013 | **0.516** | [0.500–0.530] | consistent with independent-data envelope 0.4–0.7 (Konstantakos) |
| CRISPRon | 0.504 | [0.489–0.519] | within its published external range 0.46–0.68; below its internal 0.80 — expected (full-set eval, not their held-out split; this library is in its training) |
| RuleSet1 | 0.222 | [0.204–0.240] | below CRISPOR's 0.34–0.44 non-training range — assay-context effect (U6-trained rules on TRAP surrogate library) |
| CRISPRater | 0.091 | [0.0724–0.1116] | same assay-transfer degradation |
| *Assay-noise ceiling (measured)* | *0.615* | D8+dox vs D10+dox replicate | the honest upper bound for this assay |

**Reading:** the two modern endpoints reach **83–84% of the measured assay-noise
ceiling** — i.e., near the practical limit for this assay, and inside every published
envelope we compared against. Classical rules transfer poorly to this assay class,
matching Haeussler-2016's assay-dependence finding. nDCG@20 is degenerate at n=11.5k
(0.17% cohort slices); Run-2 will use the smaller Konstantakos cohorts (e.g., Labuhn
HEL n=424) where the metric is meaningful.

**Environmental consequence:** CRISPRon + RS3 are the load-bearing on-target endpoints
for task 002; RS1/CRISPRater stay as comparator columns only.

## 5. Status after these runs

- Runtime: knockout stack end-to-end verified (enumerate → 6 endpoints → genome-wide
  off-target + CFD → gates → ranking → tested deliverable).
- Benchmarks: 1 of 5 pre-registered slots executed; no-tuning attestation holds.
- Gates remain DRAFT (calibrate-before-freeze unchanged; these runs produced no
  threshold changes).
- Nothing here is wet-lab validated; all deliverables cap at `NEEDS_EXPERIMENTAL_VALIDATION`.
