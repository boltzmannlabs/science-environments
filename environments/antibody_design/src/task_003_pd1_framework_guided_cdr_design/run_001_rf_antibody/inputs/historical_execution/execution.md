# run_001 execution log — task_003 PD-1 framework-guided CDR design

All timestamps UTC 2026-11-14. This log records ONLY executed work; planned stages stay in the plan section of provenance.json/workflow.md.

## Stage: input staging + verification (COMPLETED — local evidence in inputs/)

- Paper main text + Supplementary (MOESM1-3 PDFs) retrieved from Springer static CDN (PMC PDF links were bot-blocked HTML; discarded).
- Table 1 framework template extracted verbatim (8 FR blocks + CDR length ranges, Chothia numbering) — saved inputs/framework_table1.json.
- H965 full VH/VL + KD 81.6 nM extracted from Supplementary Table 7; full 10-member PD-1 binder panel extracted with KD values — inputs/h965_and_pd1_panel.fasta + .json.
- PD-1 target verified: UniProt Q15116 fetched; 4ZQK chain B = PD-1 ECD 33-146 observed (85-92 disordered; S93 construct substitution vs UniProt C93 — disclosed).
- PD-L1 interface on PD-1 (4ZQK, CA<10A proxy): residues 63-84 + 124-134 — inputs/pd1_interface_contacts.txt.
- Cross-check 5GGS (pembrolizumab Fab:PD-1): Fab-contacting PD-1 residues (60-92, 124-134) overlap the same ligand-binding surface.
- H965 VH/VL decomposed against Table 1 blocks: framework byte-identical to template; CDR content: H1=GFTFSSY, H2=ISGGGS (plus embedded AMS in FR-H2 per paper block layout), H3=EYINTFTY(8), L1=RASQSISSWLA, L2=AASRLQS, L3=QQSYSYPPLT.

## Stage: CDR boundary definition (COMPLETED, local)

- Platform Antibody_Numbering job BLOCKED by deployment drift: connector contract enum requires
  capitalized schemes (Kabat/Chothia/Aho/IMGT) while the live backend rejects them and demands
  lowercase (imgt/aho/chothia/kabat); omitting scheme is also rejected ("Scheme is required").
  Deadlock confirmed over 4 documented attempts (2 terminal backend failures, 2 client validation
  failures). Reported as tool blocker; NOT a scientific blocker.
- CDR boundaries frozen instead from the paper's own Table 1 block layout (Chothia), validated by
  exact decomposition of all 10 published PD-1 panel sequences (parse_panel.py, byte-identical FR
  anchors). Editable mask (1-based per chain, applies to any candidate on this framework):
  VH: H1 26-32, H2 52-57, H3 98-(98+H3len-1); VL: L1 24-34, L2 50-56, L3 89-(89+L3len-1).

## Stage: framework PDB staging (COMPLETED)

- pd1_frk_fv_complex.pdb built (build_complex.py): PD-1 chain P (5GGS chain Z, 33-134) + Fv chains H/L
  (paper framework on pembrolizumab Fab A/B backbone from 5GGS). Wrong-chain-pair bug found and fixed
  (Y+Fab A/B -> Z+Fab A/B): min CA P-H 3.6 A, P-L 5.9 A. Split into fv_scaffold.pdb (H/L) and
  pd1_antigen.pdb (P). Uploaded with allow_partial_validation after user approval.

## Stage: design tracks (COMPLETED)

- RF-Antibody (rfdiffusion_proteinmpnn, doc 6af8769f239a6b9f38beba18, 20 designs -> 40 pairs):
  39/40 carry a 7-residue H2 window and edit the locked framework at FR/CDR junctions (tool behavior,
  alignment-verified); 1 failed length extraction. 0 promoted; raw kept.
- AntiBMPNN on Fv scaffold (docs 6af87806d29658acc304df8c 40 seqs + 6af8799d445ae94313c3b012 60 seqs):
  edit mask verified 100/100 position-by-position, but 100/100 place a novel Cys at CDR-L3 pos 92 ->
  0 eligible (no-Cys gate). Deterministic backbone-driven artifact, not resubmitted at lower stringency.
- agcdr_diff (doc 6af879a3d29658acc304e059, 20 backbones, CDR RMSD ~10.9 A, framework preserved) ->
  renumbered per-residue ZIP -> AntiBMPNN (doc 6af87c36445ae94313c3b280, 160 seqs, mask verified
  160/160) -> 115 unique gate-passing candidates (agcdr_pool.json).

## Stage: screening (COMPLETED)

- select_screening.py (frozen rule: medoid seed + greedy max-min CDR Hamming): 5 candidates, min
  pairwise distance 32/60 CDR positions. H965 runs alongside as control.
- Boltz2 x6 submitted+completed: H965 control 6af87d71445ae94313c3b729; cand1 6af87d939030bff416447c9a;
  cand2 6af87d99239a6b9f38bebe2d; cand3 6af87da39030bff416447cb6; cand4 6af87da99de6b44b075d81f2;
  cand5 6af87db19850a93adf67d249. Note: platform emitted pairwise predictions (PD1:VH, PD1:VL) per
  3-chain submission, not one ternary complex; metrics kept per pair.
- Construct drift disclosed: control antigen = 33-145 S93 form; candidates = 33-134 C93 form
  (design construct). Ranking uses candidates only; cross-form comparison flagged in report.
- Antibody_Prediction x3 completed: Thermal_Stability_ESM 6af87dd4d29658acc304e596,
  Solubility_ESM 6af87dda445ae94313c3b7bb, CDR_Prediction 6af87ded445ae94313c3b850.
  Antigen_Antibody_binding rejected by active connector enum (contract drift) — not run.
- Downloads: boltzmann_download 400 on Boltz2 outputs.zip; retrieved via status re-poll + direct
  signed-URL fetch inside the 300 s window (all 6 Boltz2 archives + 3 property CSVs).
- Metrics (assemble_metrics.py -> metrics_raw.json; build_bundle.py -> results bundle):
  H965 control ipTM PD1:VH 0.895 / PD1:VL 0.717; candidates PD1:VH 0.722-0.945, PD1:VL 0.677-0.916.
  Top PD1T3-019 (cand_rank2, H3 AAAGAFAF): ipTM PD1:VH 0.945, PD1:VL 0.916, 75/67 contacts,
  27 PD-1 interface residues (union), 26 on the PD-L1-binding surface; Tm_pred 79.0 C.
- Results bundle written to results/task_003_pd1_framework_guided_cdr_design/run_001/pd1_results/:
  designed_sequences.fasta (115 candidates), published_controls.fasta (10), shortlist.csv,
  metrics.json, benchmark_comparison.csv, report.md, structures/ (12 Boltz2 models), raw_outputs/ (15).

## Boltzmann job ledger

| # | job_name | purpose | status |
|---|----------|---------|--------|
| 1 | Antibody_Numbering | IMGT numbering on H965 VH/VL | BLOCKED (connector/backend scheme-enum drift, 4 attempts) |
| 2 | rfdiffusion_proteinmpnn | primary design track | COMPLETED doc 6af8769f239a6b9f38beba18 (0 eligible) |
| 3 | AntiBMPNN | conservative track r1 | COMPLETED doc 6af87806d29658acc304df8c (0 eligible) |
| 4 | AntiBMPNN | conservative track r2 | COMPLETED doc 6af8799d445ae94313c3b012 (0 eligible) |
| 5 | agcdr_diff | backbone diversification | COMPLETED doc 6af879a3d29658acc304e059 |
| 6 | AntiBMPNN | agcdr backbone design | COMPLETED doc 6af87c36445ae94313c3b280 (115 eligible) |
| 7 | Boltz2 | H965 control complex | COMPLETED doc 6af87d71445ae94313c3b729 |
| 8-12 | Boltz2 | 5 screening candidates | COMPLETED docs 6af87d93.../6af87d99.../6af87da3.../6af87da9.../6af87db1... |
| 13 | Antibody_Prediction | Thermal_Stability_ESM | COMPLETED doc 6af87dd4d29658acc304e596 |
| 14 | Antibody_Prediction | Solubility_ESM | COMPLETED doc 6af87dda445ae94313c3b7bb |
| 15 | Antibody_Prediction | CDR_Prediction | COMPLETED doc 6af87ded445ae94313c3b850 |
| 16 | Antibody_Prediction | Antigen_Antibody_binding | UNAVAILABLE (absent from active connector enum) |
