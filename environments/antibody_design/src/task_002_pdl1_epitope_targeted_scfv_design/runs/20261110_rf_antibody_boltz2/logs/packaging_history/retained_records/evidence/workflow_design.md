# task_002 — PD-L1 Epitope-Targeted scFv Design: Workflow Design & Selection

## Study Inputs (Germinal, Nat Biotechnol 2026, PMC13366713; code: github.com/SantiagoMille/germinal)

**Starting framework (the actual parent, NOT H5):** generic paired scFv from `germinal/pdbs/scfv.pdb`
- VH (120 aa): EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS
- Linker (15 aa): GGGGSGGGGSGGGGS (G4S x3)
- VL (107 aa): DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK
- CDR lengths (IMGT, from configs/run/scfv_pdl1.yaml): HCDR1/2/3 = 8/8/13, LCDR1/2/3 = 6/6/9
- Orientation: VH-first (vh_first: true), VH-linker-VL
- The framework carries placeholder CDRs; Germinal designs CDRs de novo, preserving FRs and CDR lengths.

**Target construct:** human PD-L1 (CD274) V-like domain, `germinal/pdbs/pdl1.pdb` chain A (115 aa)
- Sequence: AFTVTVPKDLYVVEYGSNMTIECKFPVEKQLDLAALIVYWEMEDKNIIQFVHGEEDLKVQHSSYRQRARLLKDQLSLGNAALQITDVKLQDAGVYRCMISYGGADYKRITVKVNA
- Epitope hotspots (configs/target/pdl1.yaml): A37(I), A39(Y), A41(E), A96(R), A98(M) — matches the paper's I37/Y39/E41 key hotspots
- Glycosylation: the V-like domain has NO N-glycan (PD-L1's N297 is in the C-like domain, excluded). Design target is unglycosylated.
- Residue numbering: V-like domain mature numbering (post-signal-peptide), consistent with the paper.

**Comparator:** H5 (Germinal-designed anti-PD-L1 scFv, cryo-EM PDB 35TL / EMDB EMD-77181). H5 is evaluation evidence only, excluded from generation.

## Candidate Workflows (Boltzmann platform-tools)

### Workflow A — Epitope-conditioned CDR backbone design (design-selected)
Tools: `epitope_abgen` → `AntiBMPNN` → `Boltz2` → `Antibody_Prediction`
1. epitope_abgen: antigen (PD-L1 V-like) + framework (VH-H/VL-L) + mask all_cdrs + epitope [A:37,A:39,A:41,A:96,A:98] → CDR backbone PDBs
2. AntiBMPNN: structure-conditioned sequence design on H+L chains
3. Reassemble scFv (VH+linker+VL); Boltz2 predicts scFv+PD-L1 complex (ipTM/pLDDT/PAE)
4. Antibody_Prediction: Thermal_Stability_Protbert, Thermal_Stability_ESM, Solubility_ESM, CDR_Prediction
5. Rank by interface confidence + epitope engagement + properties; shortlist
- Strengths: direct epitope conditioning (most "epitope-directed"), explicit framework+CDR-length preservation, paired H/L, full evidence chain
- Limitations: multi-step; backbone→sequence is a separate inverse-fold; needs scFv reassembly
- **EXECUTION STATUS: SUBMITTED, NO OUTPUT.** Job `epitope_abgen` doc_id `6af33484b2d9f21f0dc8d50e` was accepted but returned "No Output Found" after >2 h of polling. No backbones, sequences, or downstream products were generated. This workflow is therefore **not completed** and cannot be benchmarked against outputs.

### Workflow B — RF-Antibody (comparison; EXECUTED)
Tools: `rfdiffusion_proteinmpnn` → `Boltz2` → `Antibody_Prediction`
1. rfdiffusion_proteinmpnn: framework PDB + antigen PDB + antibody_type=antibody + num_sequences → ZIP (seqs+structs+metrics)
2. Boltz2 independent structure prediction
3. Antibody_Prediction properties
- Strengths: end-to-end single generation step, produces seqs+structs together, ProteinMPNN sequence quality
- Limitations: RFdiffusion conditions on the whole antigen surface, not specifically the epitope residues; framework preservation less explicit; may drift CDR lengths
- **EXECUTION STATUS: COMPLETED.** 20 candidates were returned (doc_id `68d12a5de5b6a2fdc0e3c443`); 10 were included in the retained local Boltz-2 evaluation panel; 5 were shortlisted and property-predicted with platform Antibody_Prediction (doc_id `6af36e74d982f81aac5b4ec8`).

### Workflow C — AgCDR-Diff (alternative, not selected)
Tools: `agcdr_diff` → sequence design → `Boltz2` → `Antibody_Prediction`
- Requires antibody+antigen already positioned in the SAME coordinate frame (a pre-docked complex). We have a free generic framework, not a bound complex, so this needs an extra docking step and is less suitable here.
- **EXECUTION STATUS: NOT RUN** (excluded at design stage; no pre-docked complex available).

## Selection & Rationale

**Design selection:** Workflow A (epitope_abgen) was selected as the most suitable for "framework-conditioned epitope-directed design" — it is the only tool that directly conditions CDR generation on the declared epitope residues while preserving the user-specified framework. Workflow B was designated the comparison; Workflow C excluded (needs a pre-docked complex).

**Execution outcome:** Workflow A did not produce output after >2 h and is recorded as pending/failed. Workflow B completed end-to-end and is the workflow whose outputs are reported and benchmarked here. This is an important, honest finding: the design-optimal (epitope-conditioned) workflow was not executable in this session, and the executed workflow (RF-Antibody) conditions on the whole antigen surface rather than the declared epitope — so its candidates' epitope engagement is an *outcome measured post-hoc* (hotspot contacts), not a guaranteed design constraint.

**Post-hoc epitope filter:** Because Workflow B does not enforce epitope conditioning, the 10 candidates were screened for actual engagement of the declared hotspots (I37, Y39, E41, R96, M98) in the predicted complexes. 8 of 10 contacted all 5 hotspots; 2 (rf0_d0, rf1_d6) bound PD-L1 but showed no hotspot engagement (off-epitope mode) and are reported for contrast only.
