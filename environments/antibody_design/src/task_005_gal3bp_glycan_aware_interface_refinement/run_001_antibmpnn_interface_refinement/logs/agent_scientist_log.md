# Agent-Scientist activity — run_001_antibmpnn_interface_refinement

Task: `task_005_gal3bp_glycan_aware_interface_refinement`. Saved status: **completed_with_caveats**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log — task_005 run_001_antibmpnn_interface_refinement

Chronological observable activity (session 20261114_110418_c0bdfc, host boltzmann10). Times UTC, approximate to tool-call granularity.

- 11:19 Task md read; anchors recorded (161/165 interactions, ~67% H-bond share, 5 A RMSD boundary, 3 replicas, E1 dSASA 2.9 A2). Skill antibody-design-benchmark loaded.
- 11:2x BDBV-43 identified as PDB 7KEW Fv (borrowed scaffold, no Gal-3BP binding history).
- 11:3x Gal-3BP Q08380 fetched: mature 19-585 (567 aa), 7 N-glycosites, SRCR/BTB/BACK domains.
- 12:0x Package tree created; 7KEW + AF-Q08380 downloaded; ANARCI germlines: IGHV1-69*02/IGHJ5*01, IGKV3-15*01/IGKJ1*01.
- 12:1x Boltz2 submitted (doc 6af844cd9de6b44b075d7a93) -> completed 7.6 min; returned PAIR models (VH:VL 0.945, VH:ag 0.317), no ternary.
- 12:2x Boltz2 Multimer submit failed "Insufficient credits" (no doc_id). Local fallback prepared: MSA run launched (completed 15:11), Protenix verified.
- 13:0x-14:0x Pair-model ternary assembly + interface mapping (7 FR-only pairs) — superseded later by AFM ternary.
- 15:1x Credits returned; AFM ternary reference submitted (doc 6af879cf9de6b44b075d7a93f4c full: 6af879cf9de6b44b075d7f4c) -> completed 17:14 (2h10m), iptm 0.26-0.32 across 5 models.
- 17:2x AntiBMPNN submit #1 (doc 6af8999b9030bff4164485c2) validation_failed: position 113 > chain B length 106 (gapped IMGT mask). Mask recomputed from non-gap ANARCI indices.
- 17:33 AntiBMPNN #2 (doc 6af89b4ed29658acc304eef4) accepted; completed 85 s; 20 designs, 19 unique; scores 0.336-0.400. Download via fresh signed URL after 300 s expiry 403.
- 17:3x Top-3 selection (G3BPD-14/-04/-17 by score). ERROR EPISODE: five Multimer submits (6af89c88, 6af89c8f, 6af89c96, 6af89d1e, 6af89d26) carried hand-typed payload corruption (wrong VLs, truncated antigen, transposition). Detected by programmatic diff against candidate_designs.json; all voided; payloads regenerated programmatically (sha256-verified segments 122/106/567) and resubmitted.
- 17:41 G3BPD-14 (doc 6af89d409850a93adf67dbf3) + G3BPD-04 (doc 6af89d539030bff41644864d) accepted.
- 17:38-18:29 G3BPD-17 first job (6af89cb19de6b44b075d8b69) downloaded, sequence-verified -> CHIMERA (VH-17 + VL-14 S32N); voided; clean resubmit doc 6af8a897445ae94313c3cfa6.
- 18:1x G3BPD-14 results: iptm 0.68/0.50/0.29/0.28/0.28; 512 contacts, 5 H-bonds, Prodigy -8.7. G3BPD-04: iptm 0.66/0.55/0.30/0.30/0.29; 608 contacts, 5 H-bonds, Prodigy -8.7.
- 18:48 G3BPD-17 clean results: iptm 0.56; 665 contacts, 6 H-bonds, 2 salt bridges, Prodigy -8.6. Sequences verified.
- Parallel local work: Protenix 3 seeds x 5 samples with real MSAs (4m19s GPU) -> iptm 0.146-0.166; persistence histogram 0 pairs shared beyond single samples; ANARCI on candidates (IGHV1-69*06 0.90-0.91); interface_chemistry.py written/debugged (element-filter and self-pair bugs fixed, re-run on all structures).
- 18:5x Package finalized per monoclonal.md sections 3-6: config JSON, run.yaml, workflow.md, logs, results tree (candidates/shortlist/sequences/metrics/benchmark_comparison + structures + raw).

- 19:0x-19:2x End-to-end completion pass vs task md Expected Output: computed candidate-side glycan occlusion (glycan_dsasa.py, 222.2/217.2/217.5 A2, 0 clashes), candidate per-sample persistence across all 5 AFM models (candidate_persistence.py; 0 rank-1 pairs persist >=3/5; RMSD 6.1-45.3 A), wrote metrics.json (task-required bundle file with structure sha256 provenance), designed_sequences.fasta, extended shortlist.csv with supported-improvements/unresolved-criteria columns, added Mut1 control + glycan/persistence rows to benchmark_comparison.csv, updated report.md, staged W2/W4 inputs. Config updated (w3-glycan, w3-persistence calls); run.yaml hash refreshed.


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110418_c0bdfc`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T11:23:57.395199+00:00 | `C01.R01` | Boltz2 | Success | `6af844cd9de6b44b075d7a93` |
| 2026-11-14T11:23:57.395199+00:00 | `C14.R01` | Boltz2 | Success | `6af844cd9de6b44b075d7a93` |
| 2026-11-14T15:10:07.431908+00:00 | `C02.R01` | Multimer_Structure_Prediction | Success | `6af879cf9de6b44b075d7f4c` |
| 2026-11-14T17:25:47.501736+00:00 | `C04.R01` | AntiBMPNN | failed | `6af8999b9030bff4164485c2` |
| 2026-11-14T17:33:02.073750+00:00 | `C05.R01` | AntiBMPNN | Success | `6af89b4ed29658acc304eef4` |
| 2026-11-14T17:41:20.047491+00:00 | `C06.R01` | Multimer_Structure_Prediction | Success | `6af89d409850a93adf67dbf3` |
| 2026-11-14T17:41:39.549926+00:00 | `C07.R01` | Multimer_Structure_Prediction | Success | `6af89d539030bff41644864d` |
| 2026-11-14T18:29:42.863248+00:00 | `C08.R01` | Multimer_Structure_Prediction | Success | `6af8a897445ae94313c3cfa6` |
| not recorded | `C01` | Boltz2 (boltzmann platform) | completed_superseded | `6af844cd9de6b44b075d7a93` |
| not recorded | `C02` | Multimer_Structure_Prediction (colabfold_multimer, AF2-Multimer v3) | completed | `6af879cf9de6b44b075d7f4c` |
| not recorded | `C03` | interface_map.py, interface_chemistry.py, glycan_dsasa.py (skill script), Prodigy (conda base) | completed | `w1-local` |
| not recorded | `C04` | AntiBMPNN (boltzmann platform) | validation_failed | `w2-antibmpnn-1` |
| not recorded | `C05` | AntiBMPNN (boltzmann platform) | completed | `w2-antibmpnn-2` |
| not recorded | `C06` | Multimer_Structure_Prediction | completed | `w3-g14` |
| not recorded | `C07` | Multimer_Structure_Prediction | completed | `w3-g04` |
| not recorded | `C08` | Multimer_Structure_Prediction | completed | `w3-g17` |
| not recorded | `C09` | ANARCI (igdesign env) | completed | `w3-anarci` |
| not recorded | `C10` | glycan_dsasa.py (skill script, open_source) | completed | `w3-glycan` |
| not recorded | `C11` | candidate_persistence.py (local) | completed | `w3-persistence` |
| not recorded | `C12` | w4_interface_sampling.py (local) | completed | `w4-afm` |
| not recorded | `C13` | Protenix local (protenix_base_default_v1.0.0) | completed | `w4-protenix` |
| not recorded | `C14` | Boltz2 (aux evidence) | completed | `w4-boltz2-aux` |
