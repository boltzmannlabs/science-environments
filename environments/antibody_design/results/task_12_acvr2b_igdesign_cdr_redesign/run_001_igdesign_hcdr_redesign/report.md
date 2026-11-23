# ACVR2B / Bimagrumab — IgDesign CDR redesign results

Run: `run_001_igdesign_hcdr_redesign`.

Reference-backbone-conditioned heavy-chain CDR redesign generated a verified twenty-candidate library across two scopes (HCDR3-only, HCDR123), with all twenty receiving matched AlphaFold2-Multimer v3 structural evaluation alongside the native reference.

## Methods and preparation

The workflow used the Bimagrumab Fv (PDB 5NGV: chain H = VH 113 aa, chain L = VL 111 aa) and the exact supplied ACVR2B reference construct (chain A fragment, human ACVR2B UniProt Q13705 mature residues 25–117, 93 aa, verified 93/93). CDR windows (0-indexed) were HCDR1 24:32, HCDR2 49:57, HCDR3 95:103.

IgDesign (ACVR2B-holdout checkpoint, with ProteinMPNN) generated 100 samples per scope under reference-backbone conditioning (VH backbone + VL + ACVR2B antigen), preserving the light chain and all framework/protected VH residues. Sequence checks verified the CDR edit mask and native recovery (AAR). Deduplication retained 44 (HCDR3-only) and 89 (HCDR123) unique candidates; the top 10 per scope by summed independent cross-entropy loss were advanced.

AlphaFold2-Multimer v3 (Boltzmann Multimer_Structure_Prediction, rank-1 model) predicted the native reference and all 20 candidates under an identical protocol: C-alpha atoms, whole-Fv (224 C-alpha) Kabsch superposition onto 5NGV, regional C-alpha RMSD for HCDR1/2/3/123 (VH) and Fv (VH+VL).

## Reference and candidate results

scRMSD values are C-alpha RMSD in Å after whole-Fv Kabsch alignment; lower is better. Native reference HCDR123 = 0.4434 Å.

| Rank | Candidate | Scope | CDR changes | HCDR123 | Δ vs native | Fv | ce_loss |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | T12-C008 | HCDR3-only | HCDR3 ARGGWFDY→ARGSEFDY | 0.3803 | −0.0631 | 1.1399 | 0.6378 |
| 2 | T12-C007 | HCDR3-only | HCDR3 ARGGWFDY→ARGSYMDY | 0.3805 | −0.0629 | 1.1999 | 0.6313 |
| 3 | T12-C001 | HCDR3-only | HCDR3 ARGGWFDY→ARGSYFDY | 0.3849 | −0.0585 | 1.2033 | 0.5019 |
| 4 | T12-C011 | HCDR123 | HCDR2 INPVSGST→INPVTGNT; HCDR3 ARGGWFDY→ARGSYFDY | 0.3879 | −0.0555 | 1.2199 | 0.9748 |
| 5 | T12-C017 | HCDR123 | HCDR2 INPVSGST→INPITGNT; HCDR3 ARGGWFDY→ARGSYFDY | 0.3883 | −0.0551 | 1.1901 | 1.0365 |

Native-recovery AAR (per-position identity vs native; higher is better):

| Scope | CDR | 1-shot | Best-of-100 | Mean (100) |
| --- | --- | ---: | ---: | ---: |
| HCDR3-only | HCDR3 | 0.875 | 0.875 | 0.750 |
| HCDR123 | HCDR1 | 0.750 | 1.000 | 0.897 |
| HCDR123 | HCDR2 | 0.750 | 0.875 | 0.703 |
| HCDR123 | HCDR3 | 0.750 | 1.000 | 0.757 |

## Candidate highlights

**T12-C008** (HCDR3-only, HCDR3 ARGGWFDY→ARGSEFDY) achieves the lowest HCDR123 scRMSD (**0.3803 Å**, −0.0631 Å vs the native 0.4434 Å) and the lowest Fv scRMSD (**1.1399 Å**). **T12-C011** (HCDR123) is the best three-CDR redesign (**0.3879 Å**, −0.0555 Å). Seventeen of the twenty evaluated candidates are at or below the native HCDR123 scRMSD, and Fv scRMSD spans 1.13–1.24 Å (native 1.2140 Å), i.e. the VH/VL assembly is essentially unperturbed by the CDR edits.

## Reference comparison and metric definitions

The published benchmark reports native-reference scRMSD for ABB2, ABB3, ABB3-LM and ESMFold. Those use different structure predictors than the executed AlphaFold2-Multimer v3 and are retained side-by-side in `benchmark_comparison.csv`, not as a like-for-like comparison. The like-for-like comparison is candidate versus native within the executed predictor. AAR is per-position identity vs the native CDR over generated samples (1-shot = first sample; best-of-100 = maximum over 100). scRMSD is C-alpha RMSD in Å after whole-Fv Kabsch alignment.

The results folder retains the top five candidates by HCDR123 scRMSD (T12-C008, T12-C007, T12-C001, T12-C011, T12-C017); the complete twenty-candidate run is archived as a backup in the workspace.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Raw](raw) · [Task comparison](benchmark_comparison.csv).
