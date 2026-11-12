# Models and Tools

**Evidence note.** Active benchmark evidence is the [completed-only
registry](benchmark/BENCHMARK_RUNS.md) (seven native-model/endpoint evaluations; model
benchmarks, not application validation). Executed model evaluations, source-score
replays and uninstalled tools are distinct states — read the availability markers below
alongside the per-task evidence status in [tasks/README.md](tasks/README.md); older
mixed evidence is preserved in [execution_history](execution_history/before_completed_only_20261112T061830Z/README.md).

Curated 2026-11-10 from the source-verified registry
(`~/IMRAN/NOV26/cirspr-sci-env/01_tools/TOOL_REGISTRY.csv` — full leakage notes, dataset
pointers, and per-tool sources there; citations in
[research references](../../research/CRISPR-Design/references.md)).
Availability: **[L]** installed & verified locally · **[R]** runnable (install path
documented) · **[C]** curated web/API only · **[G]** gap (no verified tool exists).

## Battery-stage map

| Stage | Tools (role) |
| --- | --- |
| C1 enumerate/validate | crisprDesign **[L]** · CHOPCHOP v3 **[C]** · CRISPOR **[C]** |
| C2 on-target (multi-endpoint, never averaged) | **Locally verified (2026-11-10):** RuleSet1 **[L]** · RuleSet3-Sequence **[L, rs3-env]** · CRISPRater **[L]** · CRISPRscan (T7/IVT context) **[L]** · **CRISPRon [L — installed + regression `TEST ok` 2026-11-10; AGPL-3.0 internal-use; TF 2.14/Keras-2 pin documented]** · **Not in pinned crisprScore 1.17.2:** RS2/Azimuth (py2.7 path, BSD-3, archived — second wave), DeepSpCas9 (MIT subtree, py2.7/TF1 — third wave), DeepCpf1 (unlicensed — blocked) · DeepHF webserver-only + crisprScore deephf-env (heavy py3.8/TF env, pending) · DeepCas12a **[R — Apache-2.0, torch, checkpoints in-repo, 2025/26]** for Cas12a |
| C3 off-target | Bowtie 1.3.1 GRCh38 **[L]** · CFD **[L]** · Elevation/ElevationSC **[R, MIT]** · CRISPRitz **[R, VCF+bulges]** · CRISPRme **[R, allele-aware]** · CRISOT **[R, CC BY-NC ⚠]** · FlashFry **[R, libraries]** |
| C4 indel outcome | Lindel **[L, verified PASS]** |
| C5 application layers | BE-Hive **[C/CLI]** · DeepBE **[R, no-license ⚠]** · BEDICT2.0 **[C+CLI]** · BE-dataHIVE **[R/API]** · PRIDICT2.0 **[C+CLI]** · DeepPrime **[R+C]** · Richardson/CUNE HDR rules **[method]** · Horlbeck rules + ScreenProcessing **[R]** · CRISPick CRISPRi/a **[C]** · Cas13design/TIGER **[C]** · EasyDesign **[C]** · PrimedSherlock **[R]** · **locally available via crisprScore 1.17.2 (env-pending):** DeepHF **[R]**, EnPAM-GB (prime editing) **[R]**, CasRxRF (Cas13 RF) **[R]** · CRISPRi/a DL 2024–26 **[G]** · CRISPRoff designer **[G]** |
| C6 physico-chem | rule cards (GC 40–80% band, ≥4-T homopolymer, self-complementarity, Tm) **[L]** |

## Registry (decision-relevant subset)

| Tool | Paper (venue, year) | License | Key dataset | Verified numbers | Caveats |
| --- | --- | --- | --- | --- | --- |
| DeepSpCas9 | Kim HK et al., *Sci Adv*, 2019 | research web; **NOT in pinned crisprScore 1.17.2 — use upstream code [R]** | 12,832 pairs, SRA SRP150719 | CV ρ up to ~0.77; best of 9 on 7 external U6 sets | NOT "Nat Methods ~51k" |
| DeepHF | Wang D et al., *Nat Commun*, 2019 | webserver-only (standalone repo DEAD — izhangcd/DeepHF is 404, verified 2026-11-10); crisprScore `deephf-env` is the only local path (env-pending) | 80,263 pairs, PRJNA522677 | held-out ρ 0.86–0.87 (internal) | cross-study drops to 0.4–0.6; NOT Cell Reports |
| CRISPRon | Xiang X et al., *Nat Commun*, 2021 | code GitHub+Zenodo | 23,902 gRNAs, GSE173708 | internal ρ 0.80 vs Azimuth 0.56 / DeepSpCas9 0.73 / DeepHF 0.74; external 0.46–0.68 | Kim-2019 rescaled is in training — split discipline required; NOT NAR |
| RS2/Azimuth | Doench & Fusi et al., *NBT*, 2016 | Broad portal research-use ⚠; **NOT in pinned crisprScore 1.17.2** | 4,390 sgRNAs | must-beat baseline | training widely exposed |
| RS3 | DeWeirdt et al., *Nat Commun*, 2022 | via crisprScore **[L, rs3-env; Run1-verified]** | 46,526 + 84,609 tiling, PRJNA832308 | > RS2 p<0.002 | NOT "Hart 2017"; native units scaled (can be negative) |
| DeepCpf1 | Kim HK et al., *NBT*, 2018 | research web | ~15,000 AsCpf1 targets | exact ρ UNVERIFIED (paywalled) | also a distinct Luo-2019 same-named tool |
| Lindel | Chen W et al., *NBT*, 2019 | via crisprScoreData (EH6128) | paper corpus | local interface test PASS (0.798) | — |
| CFD | Doench 2016 (same paper) | open matrix | GUIDE-seq-era | community-standard pair baseline | — |
| Elevation | Listgarten et al., *NBE*, 2018 | **MIT** (cleanest) | GUIDE-seq 13-guide set | aggregate beats MIT-sum (~random at times) | 13-guide truth set is tiny |
| CRISOT | Chuai et al., *Nat Commun*, 2023 | **CC BY-NC 2.0 ⚠** | CHANGE-seq 110/21,545 + SITE-seq (Zenodo 8420032) | ROC-AUC >0.984; beats MIT/CFD/CCTop/CROPit/uCRISPR/KinPred p<0.05 | non-commercial; never redistributed |
| CRISPRitz | Cancellieri et al., *Bioinformatics*, 2020 | non-SPDX repo; GPL-3 fork | — | > Cas-OFFinder sensitivity at similar scale | bulge+VCF aware |
| CRISPRme | Cancellieri et al., *Nat Genet*, 2023 | repo license on install | population VCF panels | found MAF-4.5% PAM-creating clinical off-target | needs VCF panels |
| BE-Hive | Arbab et al., *Cell*, 2020 | WS + bystander CLI | 38,538 targets, PMC7384975 | outcome R≈0.9 / efficiency R≈0.7; 3,388 pathogenic SNVs ≥90% precision | landing-pad training distribution; NOT "Song 2020 NBT" |
| DeepBE | Kim N et al., *NBT*, 2024 | **no license ⚠** | 7 BEs × 9 Cas9 variants | 2.9–20× editor-choice gains | NOT "Furman Nat Commun" |
| BEDICT2.0 | Kissling et al., *Genome Biol*, 2025 | WS + code | multi-context ABE | R 0.60–0.94 cell lines | ABE-focused |
| BE-dataHIVE | *BMC Bioinform*, 2024 | open (API+PyPI) | 460,000+ combos, 5 studies | harmonized fair-comparison substrate | cite per-source terms |
| PRIDICT2.0 | Mathis et al., *NBT*, 2023 | WS + CLI (uzh-dqbm-cmi) | 92,423 pegRNAs / 13,349 mutations | ρ 0.85 intended / 0.78 purity; score>70 ⇒ ~12× in vitro | all PE cross-tool claims self-reported |
| DeepPrime | Yu G et al., *Cell*, 2023 | CLI + WS | 338,996 pairs, 8 PE systems × 7 cell types | per-system ρ in paper | no PMC; dataset availability partial UNVERIFIED |
| Horlbeck rules | Horlbeck et al., *eLife*, 2016 | OA (PMC5094855) | K562 tiling γ-scores | >90% essential-gene detection, 5-guide libraries | K562 chromatin calibration |
| CRISPRoff (rules+data) | Nuñez et al., *Cell*, 2021 | OA data GSE168012 | ~116k tiling + 21,378-element screen | 3 design rules (±500 bp TSS; NDR; functional-CpG density) | **no dedicated designer tool — [G]** |
| Cas13design | Wessels et al., *NBT*, 2020 | GitLab code; mirror no-license ⚠ | 24,460 guides | spacer nt 15–21 mismatch intolerance | 2020 model; TIGER is newer |
| TIGER | Wessels & Stirn et al., *NBT*, 2023 | WS (HF Spaces) + code | ~200,000 RfxCas13d guides | outperforms Cas13design (deltas paywalled UNVERIFIED) | current Cas13 reference |
| EasyDesign | Huang et al., *iMeta*, 2024 | OA (PMC11316927) + WS | 11,496 validated detections | ρ 0.812; 4 held-out pathogens | only large diagnostics pair; no independent benchmark |
| CRISPick | Broad GPP (Sanson 2018 / DeWeirdt 2022 / Horlbeck 2016 calibrations) | portal terms (research) | Avana/Brunello lineage | library-design standard | portal terms bind commercial use |
| CHOPCHOP v3 | Labun et al., *NAR*, 2019 | WS free (license unstated) | — | meta-tool ranking | no own model |
| CRISPOR | Haeussler et al., *Genome Biol*, 2016 | WS free; score lib on GitHub | 8-study pooled benchmark | all-scores non-training ρ 0.341–0.436 | meta-tool |
| CRISPRon | Xiang et al., *Nat Commun*, 2021 | **AGPL-3.0** (internal use; no redistribution) — **[L] installed + `TEST ok` 2026-11-10** (crispron-env: py3.9/TF 2.14.1/Keras 2.14/ViennaRNA 2.2.5 + CRISPRoff from RTH-tools-admin/crisproff GPL-3.0) | 23,902 gRNAs (GSE173708 + Kim rescaled) | internal ρ 0.80 vs Azimuth 0.56/DeepSpCas9 0.73/DeepHF 0.74; external 0.46–0.68 best | Kim-2019 in training — split discipline disclosed per benchmark |
| DeepCas12a (bm2-lab-submission) | PMC13435508, 2025/26 | **Apache-2.0**; torch; 9 fold checkpoints in-repo | HT-variant Cas12a corpora | AP 0.783 / AUC 0.868 / ρ 0.630 (HT1) | best open Cas12a option; second wave |
| CCLMoff | *Commun Biol* 2025 (s42003-025-08275-6) | MIT; **weights external** (Figshare 27080566.v2); repro effort | RNAcentral-pretrained LM | cross-dataset off-target generalization (paper) | missing inference.py + hardcoded paths — blocked pending fixes |
| DeepCRISPR | Chuai et al., *Genome Biol*, 2018 | Apache-2.0; official Docker `michaelchuai/deepcrispr` | aggregated corpora | best on only 1/6 independent datasets (Konstantakos 2022) | **cautionary baseline only**; disjoint splits mandatory |
| FlashFry | McKenna & Shendure, *BMC Biol*, 2018 | non-SPDX (terms UNVERIFIED) | — | 30–70× faster enumeration | no VCF-aware search |
| Guo 2018 / Yu 2024 (bacterial) | *NAR* 2018 / *Genome Biol* 2024 | per paper | E. coli corpora | Yu 2024 = current best bacterial CRISPRi predictor | bacterial-specific |

## Negative findings (verified absences — do not cite these as existing)

"CRISPRi-ML" (named tool) · on-target "CRISPR-BERT" and "CRISPR-Net" (both are off-target
lineages) · "CRISPR-RT" · prime-editing "MULTIPRIME" (an NGS-primer tool) · dedicated
CRISPRi/a DL model 2024–26 · dedicated CRISPRoff guide-design tool · plant-specific
activity predictor · verified SpG/SpRY/HypaCas9 activity predictor · public therapeutic
guide sequences (exa-cel SPY101 redacted; NTLA-2001 patent-bound).
