# task_010_chimera_epitope_conditioned_cdr_design — Results

**Task ID:** `task_010_chimera_epitope_conditioned_cdr_design`  
**Scope:** existing Task 008 CHIMERA/TROP-2 run, archived under the user-requested Task 010 label. This is not the separate ACVR2B Task 010. No new model run was performed for this archive.

## Candidate and finalized workflow

Reference complex `9pi9_C_D_F` → RAAD H3 benchmark and representative structure → AntiBMPNN H3 sequence generation → nonduplicate generator-score ranking → five VH/VL/TROP-2 multimer predictions → native-reference H3 and interface assessment → standard DockQ and MolProbity measurements. The RAAD 292-complex fixed-native-context benchmark and the independent TROP-2 shortlist are distinct analyses and are not directly interchangeable.

## 1. Inputs and residue mapping

- Human TROP-2 reference: 9pi9 antigen chain F; antibody VH chain C and VL chain D. Assessment structures: A = VH, B = VL, C = antigen.
- Designed H3 occupies sequential VH positions 97–110 (14 residues); native H3 `ARGGFGSSYWYFDV`. Sequential positions are not IMGT residue labels.
- Predicted constructs contain 121 VH, 107 VL and 223 antigen residues. Framework and VL sequence were unchanged in the generated pairs. Reference and model chain sequences were checked. Disulfide integrity was not separately established.
- Generator conditioning used an existing predicted structural context; that context did not recover native H3 contact pairs. This differs from a guaranteed native antigen pose.

## 2. Benchmark RAAD evaluation

A local CPU RAAD H3 model was trained for 20 epochs; best validation checkpoint epoch 18. Dependency/device changes were made. One greedy H3 design was assessed for each of 292 epitope-group test complexes, with predicted H3 coordinates evaluated in a native-framework context. AAR = 0.368 ± 0.131, H3 Cα RMSD = 1.976 ± 0.829 Å, and TM = 0.200 ± 0.119 (population SD). Published Table 3 RAAD values are 0.38 ± 0.13, 1.95 ± 0.87 Å and 0.21 ± 0.13, respectively. These are descriptive side-by-side values, not proof of faithful reproduction: candidate budget, code revision, model substitutions and exact protocol equivalence remain unresolved.

The stored 3.369 PPL uses generated argmax residues, not the paper-described native sequence. Native-target PPL recomputed from saved generation logits is 9.045 ± 4.294 across 292, but model conditioning and equivalence to the paper are unverified. The reported 0.195 CAAR used 8 Å Cα native contacts; the paper specifies 4.5 Å heavy-atom paratope CAAR. Its 292-case recalculation has not been completed. The 0.645 fixed-context H3 DockQ-like score is not canonical DockQ; interface scope differs. Per-position top-3/top-5 logits coverage is not best-of-K sampling.

## 3. AntiBMPNN sequence generation and ranking

100 samples yielded 70 unique VH/VL pairs and 30 duplicate samples. Ranking uses ascending generator score, with sample number as tie-breaker; the ordering rule was documented after generation. The five-candidate subset was recorded after reference evaluation of rank 2, so it was not preregistered. The other 65 unique pairs were not modeled structurally.

## 4. Five candidate structures and reference evaluation

Each candidate was modeled as a three-chain complex; the top unrelaxed model from each returned set was evaluated. Pair contact recovery below is H3–antigen 8 Å Cα residue-pair recovery. Contact AAR below uses the native 4.5 Å heavy-atom mask for this 9pi9 case, not the earlier 8 Å aggregate CAAR. H3 RMSD is self-aligned; DockQ uses the separate standard whole-chain VH–antigen definition.

| Rank | Sample | H3 AAR | 4.5 Å contact AAR | H3 Cα RMSD (Å) | Native H3 pairs recovered | Epitope F1 | VH–antigen DockQ |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 36 | 0.357 | 0.167 | 3.192 | 0/20 | 0.00 | 0.009 |
| 2 | 29 | 0.286 | 0.000 | 3.170 | 0/20 | 0.00 | 0.008 |
| 3 | 67 | 0.286 | 0.000 | 3.100 | 0/20 | 0.00 | 0.007 |
| 4 | 57 | 0.286 | 0.000 | 3.429 | 0/20 | 0.25 | 0.020 |
| 5 | 52 | 0.286 | 0.000 | 3.393 | 0/20 | 0.00 | 0.008 |

Rank 4's epitope F1 = 0.25 measures overlap of antigen-residue sets; it can be nonzero while exact native H3–antigen residue-pair recovery is zero. Standard DockQ 2.1.3 uses its own whole-chain heavy-atom definitions and is not the paper's Cα-based proxy.

## 5. Geometry validation

MolProbity was run in measurement-only mode on all five unrelaxed structures. Clashscores for ranks 1–5 were 50.67, 38.85, 51.52, 32.24 and 44.47, respectively. Bond/angle and other geometry outliers were also recorded; see `geometry_review.md` and `metrics.json`. No pass/fail thresholds, repair or post-repair revalidation were applied. The rank-1 returned archive has no independent input-coordinate checksum; filename and atom/residue counts match. For ranks 2–5, service receipt-size limits prevented complete cross-file input validation.

The separate RAAD TROP-2 trimer was also measured: clashscore 46.37, 11 Ramachandran outliers, 151 bond outliers and 109 angle outliers. The returned archive likewise lacks an independent input-coordinate checksum.

## 6. Interpretation and limitations

All five modeled shortlist candidates recovered 0/20 exact native H3–antigen Cα contact pairs. This is poor native-interface reconstruction in the predicted models, not proof of experimental nonbinding. The single-target shortlist cannot be compared as a benchmark-wide mean against Table 3. A matched 9pi9 reference protocol or the same full test cohort, including the same candidate budget, is required for a valid method comparison. No experimental affinity or binding measurement was performed.

## Evidence and saved outputs

[Run index](run.json) · [70 unique pairs](candidates.csv) · [Five-candidate metrics](metrics.csv) · [Shortlist](shortlist.csv) · [VH/VL sequences](sequences.fasta) · [Benchmark comparison](benchmark_comparison.csv) · [Structures](structures/) · [Geometry review](geometry_review.md) · [Raw evidence](raw/) · [Checksums](sha256_manifest.json).

Paper: [CHIMERA-Bench, arXiv:2603.13431v3](https://arxiv.org/abs/2603.13431v3), Table 3, §4.2 and Appendix A.2. The original task specification is [task_008_chimera_epitope_conditioned_cdr_design.md](../../../Tasks/task_008_chimera_epitope_conditioned_cdr_design.md); the task number in this archive is the user-requested label, not a claim that the original task was named 010.
