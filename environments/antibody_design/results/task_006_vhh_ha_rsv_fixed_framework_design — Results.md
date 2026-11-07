
**Task ID:** `task_006_vhh_ha_rsv_fixed_framework_design`

## Candidate and finalized workflow

Candidate: `ppiflow_HA_nanobody_run_2_s1` (short name `run_2_s1`).
Campaign: influenza HA; RSV is used as the comparison antigen.

Workflow: native scaffold/antigen preparation → PPIFlow CDR-backbone design → AntiBMPNN CDR sequencing → framework and sequence correspondence checks → Boltz-2 complex assessment → surface-hydrophobicity and repertoire-match scoring → matched HA/RSV PRODIGY scoring → candidate-level comparison.

## 1. Inputs and residue mapping

- Scaffold: PDB 3EAK chain A, observed parent positions 1–127.
- Editable parent positions: CDR1 26–35, CDR2 55–60, CDR3 102–117; the remaining 95 residues form the protected framework.
- HA reference: PDB 5VLI; requested hotspots B521, B545 and B552.
- HA assessment segment: 170 residues; hotspot mapping 521→21, 545→45 and 552→52.
- RSV comparison segment: 7LUC residues 250–380, 131 residues. This segment is a crop, not the complete interprotomer site containing residues 305 and 456.
- Assessment chains: A = VHH, B = antigen.

## 2. Backbone generation — PPIFlow

Ten HA backbones were generated. The retained backbone is `nanobody_run_2.pdb`.

| Backbone metric | Value |
|---|---:|
| VHH length | 121 residues |
| CDR1 / CDR2 / CDR3 lengths | 7 / 6 / 13 residues |
| Framework RMSD reported by PPIFlow | 0.1614 Å |
| Declared framework tolerance | 0.5 Å |
| Hotspot coverage reported by PPIFlow | 1.0000 (3/3) |
| CDR fraction of interface residues, PPIFlow definition | 0.8000 |
| Reported clash flag | False |

The hotspot coverage and interface fraction describe the canonical PPIFlow backbone, not a separately predicted assessment pose.

## 3. CDR sequence design — AntiBMPNN

Five sequences were sampled per backbone (50 sequences total). The retained sequence is sample 1 of backbone 2.

| Region | Candidate positions, one-based | Sequence | Length |
|---|---|---|---:|
| CDR1 | 26–32 | GFTFSRY | 7 |
| CDR2 | 52–57 | STGGGS | 6 |
| CDR3 | 99–111 | EVRNVPPDDKFDY | 13 |

Protected framework sequence matches the parent at all 95 mapped positions (100%). The full sequence matches chain A of the retained HA and RSV assessment structures.

```fasta
>ppiflow_HA_nanobody_run_2_s1 target=HA length=121
QVQLVESGGGLVQPGGSLRLSCAASGFTFSRYSLGWFRQAPGQGLEAVAAISTGGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAAEVRNVPPDDKFDYWGQGTLVTVS
```

Canonical backbone coordinates are retained separately from the sequence-based assessment structures. The canonical CDR backbone contains the generator's placeholder residue identities; the FASTA defines the AntiBMPNN sequence.

## 4. Complex confidence — Boltz-2

| Metric | Value |
|---|---:|
| Mean cross-chain PAE, both directions | 6.895 Å |
| VHH→HA PAE block mean | 6.402 Å |
| HA→VHH PAE block mean | 7.388 Å |
| ipTM, service-reported | 0.8147 |
| Mean VHH pLDDT, converted from 0–1 to 0–100 | 88.65 |
| VHH Cα RMSD to canonical backbone, VHH-self-aligned | 1.929 Å |
| Framework Cα RMSD to canonical backbone, framework-self-aligned | 0.638 Å |

PAE is the arithmetic mean over all VHH–HA residue pairs in the two directed matrix blocks. VHH-self-aligned RMSD describes internal VHH geometry, not recovery of the antigen-relative docking pose.

The confidence-assessment HA has P at segment position 9; the HA used for the energy and surface scores below has F at that position. These are separate construct-tagged assessments.

## 5. Surface-hydrophobicity assessment

Structure: retained HA energy-assessment complex, VHH chain A. Shrake–Rupley exposure was calculated over the assembled complex using a 1.4 Å probe and 100 sphere points per atom. Relative exposure uses the normalization table retained with the calculation; residues with relative exposure >0.3 were selected.

| Metric | Value |
|---|---:|
| Surface-residue KD mean | -1.242 |
| Selected exposed VHH residues | 55 / 121 |
| Whole-sequence KD mean, separate sequence-only metric | -0.217 |

The surface metric is an exposure-filtered Kyte–Doolittle hydrophobicity proxy. It is distinct from SAP and is not calibrated to an aggregation probability.

## 6. Human-repertoire sequence matching

The whole-VHH score is the fraction of unique 9-mers present in the retained human-immunoglobulin reference sequence collection.

| Metric | Value |
|---|---:|
| Whole-VHH 9-mer match fraction | 0.5487 |
| Matching / unique candidate 9-mers | 62 / 113 |

## 7. Target and decoy affinity scoring — PRODIGY

Partner selection: chains A and B. Both complexes were scored using the same service protocol.

| Candidate | HA ΔG estimate | RSV-crop ΔG estimate | HA preference difference |
|---|---:|---:|---:|
| run_2_s1 | -12.2 kcal/mol | -10.8 kcal/mol | +1.4 kcal/mol |

Preference difference = ΔG(RSV crop) − ΔG(HA); positive values favor HA in this paired score comparison. Panel coverage: 2/2 declared assessment constructs, one HA segment and one RSV segment. The result describes this pair of constructs rather than a broader antigen panel.

PRODIGY supplies a contact-based affinity estimate; bound and separated component energies were not returned.

## 8. Candidate summary

| Task property | Retained candidate result | Definition |
|---|---:|---|
| Surface aggregation-related proxy | -1.242 | Exposure-filtered surface KD mean |
| Whole-VHH repertoire-match proxy | 0.5487 | 62/113 unique 9-mers present in the reference collection |
| HA interface-affinity estimate | -12.2 kcal/mol | PRODIGY |
| HA-versus-RSV-crop preference | +1.4 kcal/mol | ΔG(RSV crop) − ΔG(HA) |

## Evidence and implementation

Local analysis: Biopython 1.84, NumPy 1.26.4. Platform model/service build versions were not exposed in the retained result records.

- `sample_metrics.csv`: native PPIFlow metrics.
- `candidate_properties.json`: AntiBMPNN sequence-level properties.
- `canonical_backbone_run2.pdb`: retained canonical backbone.
- `HA_energy_complex.pdb`, `RSV_energy_complex.pdb`, `prodigy.csv`: energy-scoring structures and native output.
- `HA_confidence_1_model_0.pdb`, `HA_confidence_pae_1_model_0.npz`, `HA_confidence_plddt_1_model_0.npz`, `HA_confidence_confidence_1_model_0.json`: confidence-assessment artifacts.
- `surface_residue_contributions.csv`: residue-level surface contributions.
- `audit.json`, `audit_method.py`, `sha256_manifest.json`: verified mappings, RMSD calculations and provenance.
