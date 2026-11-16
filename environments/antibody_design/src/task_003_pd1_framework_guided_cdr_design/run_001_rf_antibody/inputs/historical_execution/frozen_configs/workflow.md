# task_003 PD-1 framework-guided CDR design — run_001

## Objective
Design paired VH/VL candidates against the human PD-1 ligand-binding region on the paper's
humanized IGHV3-23/IGKV1-5 + IGHJ4/IGKJ1 framework (Table 1 template), and compare candidate
evidence with the published anti-PD-1-H965 final design (Suppl. Table 7; KD 81.6 nM measured).

## Verified inputs (see inputs/, provenance.json)
- Framework: 8 FR blocks verbatim from Table 1 (Chothia layout). Editable = six CDRs only,
  lengths H1=7, H2=6, L1=11, L2=7, H3 7-18, L3 9-11.
- Target: PD-1 Q15116 ECD; structural frame from 5GGS (PD-1:pembrolizumab) and 4ZQK (PD-1:PD-L1).
  Ligand-binding interface (4ZQK CA<10A): 63-84, 124-134. Construct note: S93 substitution,
  85-92 disordered in 4ZQK — design uses sequence-derived ECD 33-134 and 5GGS coordinates.
- Controls: 10 published PD-1 designs incl. H965 (comparison only, never design inputs).

## Methods (chosen independently within task constraints)
1. CDR boundary confirmation: Antibody_Numbering (IMGT) on H965 VH/VL + paper-layout positions.
2. Design context: Boltz2 folds the framework Fv (H965 sequences = paper framework with published
   CDRs, used solely as placement scaffold); framework grafted onto 5GGS Fab position over the
   PD-1 ligand-binding surface; complex = PD-1 (chain P) + Fv (chains A=VH, B=VL).
3. Primary track: rfdiffusion_proteinmpnn (RF-Antibody), antigen-conditioned CDR redesign, 20 designs.
4. Conservative track: AntiBMPNN on the staged complex, CDR-only masks
   (A: 26-32,52-57,99-106; B: 24-34,50-56,89-98 — 1-based, H3=8/L3=10 staged scaffold), 20 samples.
5. Candidate QC (local): framework byte-identity, CDR lengths, no-Cys-in-CDR, novelty vs published panel.
6. Complex plausibility: Boltz2 [PD-1, VH, VL] for top distinct candidates + H965 control;
   ipTM/PAE + local interface contact analysis vs PD-L1-interface residues.
7. Properties: Antibody_Prediction (imgt) — Thermal_Stability_ESM, Solubility_ESM,
   Antigen_Antibody_binding, CDR_Prediction on shortlist + H965.
8. agcdr_diff backbone track: NOT EXECUTED this run (backbone-to-sequence stage doubles job count);
   recorded as unexecuted.

## Ranking policy — FROZEN before any candidate scores are seen (2026-11-14)
Hard gates (fail = excluded, no relaxation):
  G1 all 8 FR blocks byte-identical to Table 1 template;
  G2 CDR lengths within declared ranges;
  G3 zero Cys in designed CDRs;
  G4 novelty: paired CDR set not identical to any of the 10 published panel members;
  G5 dedupe: unique (VH,VL) pair within the new pool.
Evidence tiers (reported, no composite score):
  T1 complex plausibility (Boltz2 ipTM, interface PAE, antigen-recovery sanity);
  T2 epitope evidence: contacts within PD-L1 interface set (63-84,124-134); >=1 hotspot contact required;
  T3 developability predictions (stability, solubility; liabilities flagged, framework-inherited separated);
  T4 distance to H965/published panel (CDR-H3 identity, whole-VH identity).
Shortlist: top 5 candidates passing all gates, ranked by T1 ipTM then T2 contact count, retaining
H3-length diversity (at most 2 per H3 length). H965 Boltz2 complex run as the control row.
Selection frozen before any wet-lab or held-out data is consulted (none available: NEEDS_INPUT).

## Honest-reporting rules
- Nothing computed here is a binding measurement; H965 KD 81.6 nM is the only measured value (SPR, paper).
- Paper aggregate metrics (AUROC 0.76 / EF 7.41 / discrimination AUROC 0.95 / AAR 0.317) are never
  assigned to new candidates or to H965 individually.
- Individual H965 ipTM/PAE/DockQ were never published: the H965 control row here is OUR Boltz2
  prediction, not the paper's number.
