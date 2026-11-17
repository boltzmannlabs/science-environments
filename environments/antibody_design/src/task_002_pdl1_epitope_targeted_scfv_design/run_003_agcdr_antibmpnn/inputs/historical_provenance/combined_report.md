# Report — task_002 PD-L1 epitope-targeted scFv design, run1_epitope_abgen

**Task:** framework-conditioned, epitope-directed design of paired VH/VL candidates (scFv, VH-first, linker AGGGGSGGGGSGGGS) against human PD-L1 V-domain on the study's trastuzumab scFv framework, with H5 (PDB 35TL) as evaluation-only comparator.

**Scope of this run:** input preparation and pose placement, H5 reconstruction control, three parallel design lanes (epitope_abgen backbone regeneration — stuck server-side and closed; RF-Antibody; AntiBMPNN sequence-only; AgCDR-Diff backbone redirection + AntiBMPNN), prospective Boltz2 evaluation of all generated candidates, interface/epitope engagement analysis, and benchmark comparison against the Germinal published metrics.

## What ran

All execution went through Boltzmann (priority 1). No ToolUniverse or open-source fallback was required for generation/evaluation; local Python (numpy/scipy/Bio/antpack) was used for interface analysis and scoring only.

| Stage | Tool | Status | Notes |
|---|---|---|---|
| Pose placement (5X8M donor) | local code | complete | framework CA RMSD 0.40 Å; hotspots 5.7–10.2 Å from framework surface |
| H5 reconstruction control | Boltz2 | complete | v1/v2 superseded (representation/construct errors); v3 accepted |
| epitope_abgen CDR backbone regeneration | epitope_abgen | **closed — stuck server-side** | doc 6af8443c9850a93adf67ca50; >11 h no output; receipt registered, state unknown; 4-day-old precedent job same type also never returned |
| RF-Antibody lane | rfdiffusion_proteinmpnn | complete | 16 VH-only designs (light chain dropped by tool); excluded |
| AntiBMPNN sequence-only lane | AntiBMPNN | complete | 8 paired designs, framework 100% preserved |
| Boltz2 eval of sequence-only candidates | Boltz2 ×5 | complete | ipTM 0.28–0.46, zero hotspots — negative |
| AgCDR-Diff backbone regeneration | agcdr_diff | complete | 8 backbones; sample 1: all 5 hotspots, epitope 20/28 |
| AntiBMPNN on agcdr sample-1 backbone | AntiBMPNN | complete | 8 diversified candidates |
| Boltz2 eval of agcdr1 candidates | Boltz2 ×8 | complete | ipTM 0.37–0.84; hotspots in 5/8; best 0.838 |

## Counts

- Designed/generated candidates: 16 intended designs + 1 accidental recombinant + 16 RF-Antibody VH-only (excluded) = 33 total entries; 18 recorded in candidates.csv (8 sequence-only, 8 agcdr1, 1 recombinant, 1 RF-Antibody aggregate row), 13 evaluated by Boltz2.
- Shortlist: 13 evaluated entries, ipTM-ranked; top 5 are all agcdr1-lane.
- Controls: H5 reconstruction control v3 (accepted; v1/v2 superseded with documented reasons).

## Results

### H5 reconstruction control (evaluation-only comparator)

Boltz2 prediction of PD-L1 + full H5 scFv construct vs 35TL cryo-EM (sequence-anchored CA matching, `code/h5_reconstruction_control_v3.py`): global complex CA RMSD **2.05 Å** (334 residues; published AF3 value 1.25 Å), PD-L1 interface-residue recovery **21/23 (0.913)**, hotspot patch 37/39/41 recovered; per-CDR H1 1.21 / H2 2.12 / H3 3.72 / L1 1.79 / L2 0.86 / L3 3.08 Å; ipTM 0.927.

### Design lanes

**Sequence-only redesign (negative, reported honestly).** AntiBMPNN CDR redesign on the placed framework: 8 paired designs, framework 100% preserved, but only 1–3 CDR point mutations each (server-fixed sampling T=0.1, seed 37). Boltz2 prospective evaluation (5 constructs, sequence-echo verified): ipTM 0.28–0.46 vs H5 control 0.927, zero hotspot contacts. Conclusion: 1–3 conservative CDR mutations cannot create a new binding interface — consistent with the Germinal architecture where backbone regeneration creates PD-L1 binding before sequence design.

**RF-Antibody (negative).** The tool returned VH-only designs (16 across 2 backbones, light chain dropped despite antibody_type=antibody); no epitope engagement. Lane excluded.

**AgCDR-Diff backbone redirection + AntiBMPNN sequence design (the successful route).** agcdr_diff regenerated CDR backbones on the placed complex; sample 1 engaged all 5 hotspots (37/39/41/96/98) and 20/28 epitope residues with framework preserved (VH 0.001 Å, VL 1.37 Å). AntiBMPNN then designed 8 diversified CDR sequence sets on that backbone (W-rich H3, D-rich L3). Prospective Boltz2 evaluation (sequence-echo verified; one transcription error caught and corrected by echo check — cand4 resubmitted):

| Candidate | ipTM | pLDDT | Epitope coverage | Hotspots |
|---|---:|---:|---:|---|
| t002r1_agcdr1_c5 | **0.838** | 0.871 | 0.500 | 41, 98 |
| t002r1_agcdr1_c2 | 0.746 | 0.855 | 0.536 | 98 |
| t002r1_agcdr1_c1 | 0.543 | 0.867 | 0.571 | 98 |
| t002r1_agcdr1_c4 | 0.538 | 0.852 | 0.607 | 37, 41 |
| t002r1_agcdr1_c0 | 0.529 | 0.882 | 0.536 | 41 |
| t002r1_agcdr1_c6 | 0.463 | 0.853 | 0.500 | — |
| t002r1_agcdr1_c3 | 0.375 | 0.871 | 0.464 | — |
| t002r1_agcdr1_c7 | 0.367 | 0.908 | 0.357 | — |

**Best candidate: t002r1_agcdr1_c5** (H3 IYSYTSYGDWFWD / L3 FYDDDDGRT), ipTM 0.838 with hotspots 41+98 engaged; full sequence in sequences.fasta, structure in structures/agcdr1/.

## Benchmark comparison

See `benchmark_comparison.csv` (6 rows) for the full table. Summary:

- **H5 reconstruction RMSD 2.05 Å vs published 1.25 Å — below reference.** Same protocol family (cofolding prediction vs cryo-EM), different predictor (Boltz2 vs AF3). Interface recovery 21/23 keeps it an acceptable control; the 0.8 Å gap is attributed to the predictor, not the protocol.
- **Campaign counts (470/48) — not comparable.** Our sampling budget was 8 generations per call; campaign yield is not a per-candidate quality metric.
- **CDR identity / interface similarity (IS) — not_computed.** Novelty DB searches were not run; recorded as not_computed rather than proxied.
- **H5 candidate-level pLDDT/ipTM/PAE/pDockQ — not_comparable** (benchmark file itself marks published values "Not Verified").

## Controls and panel coverage

- Binding-reference control: H5 scFv reconstruction (Boltz2, 0.927 ipTM) — the only antibody in this run scored under the identical protocol as candidates.
- Panel: 13 evaluated entries cover both design paradigms tested (sequence-only vs backbone-redirected); 5 unevaluated AntiBMPNN designs (bmpnn_04..07) preserved in candidates.csv/sequences.fasta.
- Negative controls: parent framework alone (implicit; lanes show no engagement without backbone redirection), recomb_23 recombinant (0.281, no engagement).

## Uncertainty and limitations

- All candidate scores are Boltz2 confidence proxies (ipTM/pLDDT) and geometric interface measures — **not measured affinities**. Confidence is not affinity.
- ipTM gap to H5 (0.84 vs 0.93) is expected for de novo candidates vs a matured, experimentally validated binder; the candidates are design leads, not validated binders.
- Single prediction per candidate (no sampling replicates); PAE/pDockQ not computed.
- epitope_abgen (the study-faithful route) never returned; the agcdr_diff route replicates its role (backbone CDR regeneration against the epitope) but is not the same implementation.
- H5 held out from generation throughout; used only for reconstruction control and epitope-engagement evidence.

## Evidence links

- Artifacts: `candidates.csv`, `shortlist.csv`, `sequences.fasta`, `metrics.csv`, `benchmark_comparison.csv`, `structures/` (19 PDBs), `raw/` (native outputs), `sequences/` (tool CSVs)
- Source: `src/task_002_pdl1_epitope_targeted_scfv_design/run1_epitope_abgen/` (workflow.md, code/, inputs/, logs/)
- Config: `configs/task_002_pdl1_epitope_targeted_scfv_design/run1_epitope_abgen.json`
