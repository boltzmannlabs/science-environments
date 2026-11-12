# Task 005 — Gal-3BP Glycan-Aware Interface Refinement: Boltzmann Workflow Design

## 1. Verified inputs (the hard gate)

| Input | Status | Source |
|---|---|---|
| BDBV-43 VH (112 aa, IGHV1, CDR-H3=`ARDEIIGADS`) | VERIFIED | PDB 7KEW chain G |
| BDBV-43 VL (106 aa, IGKV3 kappa) | VERIFIED | PDB 7KEW chain J |
| LGALS3BP full sequence (585 aa) | VERIFIED | UniProt Q08380 |
| LGALS3BP domain map | VERIFIED | UniProt Q08380 |
| LGALS3BP N-glycosylation sites (69,125,192,362,398,551,580) | VERIFIED | UniProt Q08380 |
| Modeled reference complex (BDBV-43 Fab + LGALS3BP) | CREATED (Boltz2) | task005_ref_bdbv43.pdb |
| **Exact E1 residue mapping** | **UNAVAILABLE** | paper only (repositorio.usp.br down) |
| **Study glycan model** | **UNAVAILABLE** | paper only |
| **Mut1 sequence** | **UNAVAILABLE** | paper only (point mutations in BDBV-43) |
| **Study mature Gal-3BP construct** | **UNAVAILABLE** | paper only |

**Consequence:** the BDBV-43 paired sequences and a modeled reference complex are verified, so a matched-conditions computational design is executable. The study-specific E1 residue list, glycan model, Mut1, and exact mature construct are NOT verified (paper inaccessible), so a like-for-like reproduction of the published 161/165/67%/5Å/2.9Å² benchmark is not possible. We use the verified BACK-domain location of E1 (260-360) and the verified N-glycosylation sites for the glycan-aware analysis, and label all study-specific gaps explicitly.

**Key structural fact:** E1/E2 are glycan-free epitopes within the BACK domain (260-360). The nearest N-glycosylation sites are 192 (N-terminal flank) and 362 (C-terminal flank). Glycan occlusion of the BACK-domain surface by the 362 (and 192) glycans is the central glycan-aware question.

## 2. Tool inventory (relevant Boltzmann jobs)

| Job | Module | Role |
|---|---|---|
| `AntiBMPNN` | Target-Aware Antibody | structure-conditioned sequence variants of selected chains/residues (CDR-only design) |
| `rfdiffusion_proteinmpnn` | Target-Aware Antibody | RF-Antibody backbone + ProteinMPNN sequence design (more de novo) |
| `agcdr_diff` | Target-Aware Antibody | CDR backbone conformations preserving framework+antigen (AgCDR-Diff) |
| `epitope_abgen` | Target-Aware Antibody | epitope-conditioned CDR backbones (needs E1 residue list) |
| `Boltz2` | Structure Prediction | sequence-based complex prediction (VH:VL:antigen), ipTM/pLDDT/PAE |
| `Multimer_Structure_Prediction` | Structure Prediction | AlphaFold-Multimer from colon-separated sequences (cross-check) |
| `ipsae-protein` | Structure Prediction | interface confidence from Boltz2/AF2 bundle |
| `Antibody_Prediction` | Property Prediction | Thermal_Stability_Protbert/ESM, Solubility_ESM, CDR_Prediction (paired VH/VL) |
| `stability-binding-ddg` | Optimization | mutation-induced binding ΔΔG from WT complex (chains A/B) |
| `Prodigy` | Toolbox | PPI binding-affinity estimate + interface residues |
| `MDS_openMM` | Molecular Dynamics | MD simulation (protein-ligand workflow) |
| `Mol_Probity` | Toolbox | structural quality |
| `tm_align` | Toolbox | structural alignment vs reference |

## 3. Workflows (stage graphs)

All workflows share the same evaluation ladder: sequence filter → structure → interface metrics → glycan-aware accessibility → property prediction → shortlist → (optional) heated-MD stability. `[local]` = step Boltzmann does not perform.

### W1 — AntiBMPNN CDR-H3 redesign (RECOMMENDED)
1. `[local]` Stage 0: prepare BDBV-43 Fab (H+L) + LGALS3BP (A) complex PDB in one frame (use the Boltz2 reference complex).
2. `AntiBMPNN`: chains_to_design=[H], residue_positions_to_design={H: CDR-H3}, generation_count=30. Framework + VL + CDR-H1/H2 fixed.
3. `[local]` Stage 2: sequence filter — framework intact, unique, humanness, developability liabilities (aggregation, deamidation, oxidation, PGP).
4. `Boltz2`: VH:VL + LGALS3BP for top ~5 candidates.
5. `Antibody_Prediction`: Thermal_Stability_Protbert + Solubility_ESM (paired CSV).
6. `[local]` Stage 6: matched interface metrics (Cα–Cα<8Å, vdW<4.5Å, H-bond N/O<3.5Å) + glycan-aware ΔSASA (add N-glycans at 192/362, compute epitope SASA with/without glycan, check interface clashes).
7. Shortlist by matched ipTM + interface extent + glycan accessibility + developability.

**Strengths:** directly enforces the task's "protected framework, declared CDR editing boundaries"; structure-conditioned (retains BDBV-43 backbone context); paired-chain design; lowest risk of framework drift. **Limitations:** sequence-only design (no backbone sampling); CDR-H3-only edit may be too narrow if E1 needs CDR-H1/H2/L contributions.

### W2 — RF-Antibody (rfdiffusion_proteinmpnn)
1. `[local]` Stage 0: same complex PDB.
2. `rfdiffusion_proteinmpnn`: antibody_pdb=BDBV-43 Fab, antigen_pdb=LGALS3BP, num_sequences=20, antibody_type=antibody.
3-7. Same as W1.
**Strengths:** samples CDR backbone + sequence jointly (more conformational diversity). **Limitations:** higher risk of framework/CDR-H1/H2 drift (violates "protected framework"); less controlled edit boundary; backbone changes may not fold back to the reference.

### W3 — agcdr_diff backbone + ProteinMPNN
1. `[local]` Stage 0: same complex PDB.
2. `agcdr_diff`: antibody_pdb, antigen_pdb, num_samples=15, num_steps=50 (CDR backbone conformations, framework+antigen preserved).
3. `[local]` Stage 3: ProteinMPNN sequence design on each new backbone (local, since the platform's sequence-design-on-backbone is a separate step).
4-7. Same as W1.
**Strengths:** explicit CDR backbone sampling while preserving framework+antigen (closest to the paper's "CDR swap / loop redesign" spirit). **Limitations:** two-stage (backbone then sequence); local ProteinMPNN step; backbone changes may disrupt the reference interface.

### W4 — epitope_abgen epitope-conditioned design (most glycan-aware)
1. `[local]` Stage 0: same complex PDB.
2. `epitope_abgen`: antigen_pdb, antibody_pdb, mask_cdrs=hcdr3 (or all_cdrs), heavy_chain_id, light_chain_id, antigen_chain_ids, epitope_residues=E1 (BACK-domain surface residues), samples_per_task=4.
3. `[local]` Stage 3: ProteinMPNN sequence design.
4-7. Same as W1.
**Strengths:** explicitly conditions CDR generation on the E1 epitope → most directly "glycan-aware interface refinement." **Limitations (BLOCKING):** requires the exact E1 residue list, which is unavailable (paper inaccessible). We can only approximate E1 as the BACK-domain (260-360) solvent surface, which is coarser than the paper's E1. Listed as non-executable at the paper's E1 resolution; executable only at the approximate BACK-surface resolution.

### W5 — W1 + heated MD (benchmark fidelity)
W1 + `MDS_openMM` heated replicas (3 per system, elevated temperature) to reproduce the paper's interface-stability criterion (5 Å interface-RMSD boundary).
**Strengths:** the only route to a like-for-like interface-stability comparison with the paper's 5 Å boundary. **Limitations (BLOCKING):** MDS_openMM is a protein-ligand workflow (Complex_pdb or Protein+Ligand); an antibody–antigen complex does not map cleanly onto the "ligand" slot; heated-MD setup (restraints, force field, ion/water choices) requires user-confirmed parameters with no documented defaults; computationally expensive. Listed as non-executable with the current contract without additional setup.

## 4. Decision matrix

| Workflow | Protected framework | CDR edit boundary | Glycan-aware | Paired design | Executable now | Risk |
|---|---|---|---|---|---|---|
| W1 AntiBMPNN | YES | CDR-H3 explicit | via post-hoc ΔSASA | YES | YES | low |
| W2 RF-Antibody | NO (drift risk) | implicit | via post-hoc ΔSASA | YES | YES | medium |
| W3 agcdr_diff | YES | CDR backbone | via post-hoc ΔSASA | YES | YES (2-stage) | medium |
| W4 epitope_abgen | YES | CDR explicit | YES (epitope-conditioned) | YES | PARTIAL (E1 unresolved) | low-medium |
| W5 W1+heatedMD | YES | CDR-H3 explicit | YES + MD stability | YES | NO (MD contract) | high |

## 5. Selection and justification

**Selected: W1 (AntiBMPNN CDR-H3 redesign + Boltz2 + Antibody_Prediction + local glycan-aware ΔSASA).**

Justification:
1. W1 is the only workflow that cleanly satisfies the task's hard constraints — "preserve the supplied chain pairing and protected framework" and "declare CDR editing boundaries" — via `residue_positions_to_design`. W2 risks framework drift; W3/W4 need a separate local sequence-design step; W5 is blocked by the MD contract.
2. W1 is fully executable now with verified inputs (BDBV-43 complex PDB + LGALS3BP). W4 is the most glycan-aware but is blocked by the unavailable E1 residue list; we approximate its glycan-awareness with a post-hoc N-glycan ΔSASA step that uses the verified UniProt glycosylation sites.
3. W1's structure-conditioned design retains the BDBV-43 backbone context, which is the right prior for a "reference-derived interface refinement" (not a de novo design).
4. The glycan-aware question (does the E1/BACK-domain interface stay accessible when the flanking 192/362 N-glycans are present) is answered by a matched local ΔSASA + clash analysis, which is the same quantity the paper reports (E1 glycan-associated ΔSASA 2.9 Å²).

**Portfolio note:** W1 is the primary executed workflow. W3 (agcdr_diff) is the natural secondary if CDR-H3-only editing proves too narrow. W4 and W5 are documented as blocked by unavailable study inputs / contract limitations, respectively — not silently dropped.

## 6. Shared evaluation ladder (all candidates)
1. Sequence filter (framework intact, unique, developability).
2. Boltz2 structure (ipTM, pLDDT, PAE).
3. Matched interface metrics (Cα–Cα<8Å residue pairs, vdW atom pairs<4.5Å, H-bonds N/O<3.5Å, H-bond share, antigen-residue count).
4. Glycan-aware accessibility (N-glycan ΔSASA on the BACK-domain epitope, interface-glycan clashes).
5. Property prediction (thermal stability, solubility).
6. Shortlist (matched ipTM + interface extent + glycan accessibility + developability).
7. (Optional, blocked) heated-MD interface stability vs the 5 Å boundary.
8. Experimental validation is ground truth (not performed).
