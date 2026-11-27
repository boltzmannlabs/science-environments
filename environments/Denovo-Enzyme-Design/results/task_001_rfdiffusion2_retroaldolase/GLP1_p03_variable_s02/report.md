# task_001_rfdiffusion2_retroaldolase — Results

## Candidate and workflow

Reporting representative: `GLP1_p03_variable_s02`. Comparison sequences: `KCR1_s01` and `KCR1_s02`. The panel contains three120-residue sequences on the same generated scaffold, with20 retained assessment structures.

Workflow:5AN7 motif preparation → RFdiffusion2 scaffold generation → LigandMPNN sequence design and packing → sequence/atom correspondence checks → Chai-1 independent structure prediction → catalytic-site, backbone, exposure and contact measurements → Foldseek/TM-align structural comparison.

## 1. Inputs and residue mapping

Reaction: retroaldol cleavage of methodol. Source:5AN7 chainA. Generation analogue:LLK. Structure predictions in this reporting panel use the separately submitted free-CCD-LLK ligand `COc1ccc2cc(ccc2c1)C(=O)/C=C/C`. Source author numbering, prepared numbering and generated positions are retained separately.

| Source / prepared identifier | Design residue | Protected functional atoms |
|---|---|---|
| Tyr1051 / A51 | Tyr5 | CZ, OH |
| Lys1083 / A83 | Lys37 | CE, NZ |
| Asn1110 / A110 | Asn101 | CG, OD1, ND2 |
| Tyr1180 / A180 | Tyr85 | CZ, OH |

The canonical generator backbone retains placeholder identities outside the catalytic residues; the FASTA records define the actual designed sequences. Predictions are assessed against the unchanged canonical reference, not a packed or fitted replacement.

## 2. Sequence design

The original scaffold sequence stage contains8 draws. The restored-constraint stage adds2 new draws under the original two-sequence-per-backbone budget. `generated_sequences.fasta` retains these10 draws; `sequences.fasta` contains the three-sequence comparison panel.

| Sequence | Length | Fixed catalytic identities | Nonmotif lysines | Assessment structures |
|---|---:|---:|---:|---:|
| GLP1_p03_variable_s02 | 120 | 4/4 | 11 | 10 |
| KCR1_s01 | 120 | 4/4 | 0 | 5 |
| KCR1_s02 | 120 | 4/4 | 0 | 5 |

## 3. Independent structure assessment

Catalytic recovery is measured over41 heavy atoms from Tyr5/Lys37/Asn101/Tyr85 after fitting their N/CA/C atoms. The published AME numerical reference is RMSD<1.5Å. Backbone RMSD uses all120 corresponding Cα atoms.

| Cohort | Models | Catalytic RMSD range, Å | Mean, Å | Models<1.5Å | Cα RMSD range, Å |
|---|---:|---:|---:|---:|---:|
| Lead / original | 5 | 0.993–1.191 | 1.067 | 5/5 | 0.835–0.998 |
| Lead / confirmation | 5 | 1.017–1.138 | 1.081 | 5/5 | 0.817–0.973 |
| KCR1_s01 | 5 | 1.826–2.088 | 1.981 | 0/5 | 1.165–6.768 |
| KCR1_s02 | 5 | 2.932–3.325 | 3.081 | 0/5 | 2.048–2.279 |

The representative's original and fresh-seed cohorts each contribute five structures. The two replacement sequences each contribute five structures. Repeated structures of one sequence remain distinct from sequence diversity.

## 4. Per-residue catalytic recovery

Mean sidechain heavy-atom RMSD after one full-chain Cα alignment; coupled Tyr CD/CE ring swaps are treated as equivalent, whereas Asn OD1/ND2 are not interchangeable.

| Residue | Lead original, Å | Lead confirmation, Å | KCR1_s01, Å | KCR1_s02, Å |
|---|---:|---:|---:|---:|
| Tyr5 | 0.633 | 0.671 | 2.413 | 1.925 |
| Lys37 | 1.529 | 1.451 | 3.386 | 1.908 |
| Asn101 | 1.641 | 1.686 | 2.027 | 1.904 |
| Tyr85 | 1.387 | 1.405 | 1.561 | 7.843 |

## 5. Ensemble coordinate dispersion

RMSF is calculated within each five-structure cohort about its aligned coordinate mean, using named sidechain atoms and the population denominator. Values describe prediction-ensemble coordinate dispersion.

| Residue | Lead original, Å | Lead confirmation, Å | KCR1_s01, Å | KCR1_s02, Å |
|---|---:|---:|---:|---:|
| Tyr5 | 0.251 | 0.237 | 0.899 | 0.695 |
| Lys37 | 0.631 | 0.464 | 0.637 | 0.633 |
| Asn101 | 1.107 | 1.166 | 0.642 | 0.515 |
| Tyr85 | 0.224 | 0.204 | 0.596 | 1.375 |

## 6. Exposure and contacts

Shrake–Rupley SASA uses a1.4Å solvent probe,960 sphere points and the retained Bondi element radii. Ligand exposure fraction is complex ligand SASA divided by isolated ligand SASA in the same conformation.

| Cohort | Mean Lys37 SASA, Å² | Mean NZ SASA, Å² | Mean ligand exposure fraction |
|---|---:|---:|---:|
| Lead / original | 0.567 | 0.114 | 0.1474 |
| Lead / confirmation | 0.453 | 0.000 | 0.1578 |
| KCR1_s01 | 4.624 | 1.959 | 0.1158 |
| KCR1_s02 | 0.830 | 0.000 | 0.1065 |

For the representative,8/10 structures have no protein–free-ligand heavy-atom pair below1.5Å. Two original-cohort structures have Lys37NZ–ligandC14_1 distances of1.498 and1.448Å. The source-design backbone-only clearance is3.426Å; it is a separate measurement. Explicit free-component connectivity is retained; proximity alone is not used to introduce a new covalent bond.

## 7. Structural novelty and paper comparison

The paper's Figure4a designed retroaldolase has a reported closest-PDB TM-score of0.47 to6SU3. The representative's best retrieved match is `4kkn-assembly1_A` (bovine CTLA-4), with query-normalized TM-score0.6161, target-normalized score0.6273 and query coverage0.992.

The local search uses PDB100250101, Foldseek cluster-member expansion,1000 retrieved candidates and full TM-align reranking of20 hits. Search scope and normalization accompany the comparison rather than treating different database searches as identical.

## 8. Assessment coverage and selection definitions

The reporting representative is selected for its retained catalytic-recovery results; this is distinct from original-task eligibility. The original rule also checks no newly designed nonmotif lysines, per-residue sidechain RMSD≤1Å and globalCα RMSD≤2Å. All sequence and structural values are retained in `candidates.csv`, `shortlist.csv` and the raw selection records.

| Assessment state | Retained samples in this panel | Metric coverage |
|---|---:|---|
| Free CCD LLK prediction |20 | Backbone/site RMSD, coordinate RMSF, SASA and contacts |
| Apo |0 | Not recorded |
| Noncovalent R-methodol |0 | Not recorded |
| Four carbinolamine states |0 each | Not recorded |

Substrate hydrogen-bond occupancies and candidate kinetic constants have no values in the retained records and are not assigned numerical substitutes.

## Evidence and saved outputs

[Run index](run.json) · [Candidate inventory](candidates.csv) · [Assessed metrics](metrics.csv) · [Sample metrics](sample_metrics.csv) · [Comparison panel](shortlist.csv) · [Sequences](sequences.fasta) · [Representative sequence](selected_sequence.fasta) · [Benchmark comparison](benchmark_comparison.csv) · [Structures](structures) · [Raw evidence](raw) · [Checksums](sha256_manifest.json).

Paper: [Atom-level enzyme active site scaffolding using RFdiffusion2](https://doi.org/10.1038/s41592-025-02975-x), Results AME benchmark and Figure4a. This package indexes the retained executed results; packaging does not add model runs.
