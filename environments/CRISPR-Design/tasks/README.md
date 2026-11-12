# Tasks — CRISPR Design

One task per modality/application, plus the general routing task. All share the
environment core battery (E1–E6), draft gates and ranking contract
([ENVIRONMENT_SPEC](../ENVIRONMENT_SPEC.md)); application tasks add required stages,
hard vetoes, default weight emphasis, endpoint distinctions and honest benchmark status.
Example requests (in [config/](../config/)) illustrate syntax only.

**Runtime and evidence status.** Partial workflows and measured-label model evaluations
have executed. Active benchmark evidence is the [completed-only
registry](../benchmark/BENCHMARK_RUNS.md) (seven completed native-model/endpoint
evaluations — model benchmarks, not application validation); per-task result records
live in [results/](../results/README.md); older mixed Run-2/Run-3 reports are retained
as [execution history](../execution_history/before_completed_only_20261112T061830Z/README.md).
The published-anchor column below is literature context, not a list of validated local
capabilities. No full application validation is claimed for any task.

| Task | Application | Local executed evidence | Published-anchor status |
| --- | --- | --- | --- |
| [001_crispr_design_general](001_crispr_design_general.md) | general routing + all modes | shared components ([RS3](../benchmark/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) · [CRISPRon](../benchmark/002_CRISPRon/Run-4_2026-11-12/REPORT.md)) | routing corpus absent (by construction) |
| [002_crispr_knockout](002_crispr_knockout.md) | knockout / gene disruption | executed Run1 workflow + [RS3](../benchmark/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) · [CRISPRon](../benchmark/002_CRISPRon/Run-4_2026-11-12/REPORT.md) · [CFD](../benchmark/003_CFD2016/Run-4_2026-11-12/REPORT.md) | **strongest** (Kim-2019 12,832; DeepHF 80,263; Konstantakos-2022 protocol) |
| [003_crispr_therapeutic-in-vivo](003_crispr_therapeutic-in-vivo.md) | therapeutic in-vivo editing | specificity component ([CFD](../benchmark/003_CFD2016/Run-4_2026-11-12/REPORT.md)) | anchors: CHANGE-seq; Kaufmann-2026 independent benchmark; strategy-level therapeutic anchors only |
| [004_crispr_variant-correction](004_crispr_variant-correction.md) | variant correction & precision repair (modality router) | matched components ([BE-Hive](../benchmark/004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) · [PRIDICT2.0](../benchmark/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) · [DeepPrime](../benchmark/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md)) | BE-Hive 38,538 + PRIDICT1 92,423 + CUNE n=30 (HDR thin) |
| [005_crispr_base-editing](005_crispr_base-editing.md) | base editing (CBE/ABE, editor choice) | [BE-Hive BE4 external test](../benchmark/004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) (weak transfer) | BE-Hive R≈0.9; BE-dataHIVE 460k harmonized; no neutral benchmark |
| [006_crispr_prime-editing](006_crispr_prime-editing.md) | prime editing (pegRNA + PE3) | [PRIDICT2.0](../benchmark/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) · [DeepPrime](../benchmark/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) matched held-out | PRIDICT1 ρ 0.85 intended/0.78 unintended; PRIDICT2.0 intended 0.91 HEK293T/0.81 K562; DeepPrime 338,996 pairs |
| [007_crispr_regulation](007_crispr_regulation.md) | CRISPRi/a gene regulation | CRISPRi window-gate component test only | Horlbeck-2016 learned model and phenotypic labels |
| [008_crispr_epigenome-editing](008_crispr_epigenome-editing.md) | CRISPRoff epigenome editing | blocked — no matched epigenetic endpoint | GSE168012 tiling + 3 rules; no dedicated tool (gap) |
| [009_crispr_rna-targeting-cas13](009_crispr_rna-targeting-cas13.md) | Cas13 RNA targeting | [RFcombined refit](../benchmark/007_RFcombined/Run-4_2026-11-12/REPORT.md) (qualified) | TIGER ~200k guides (Cas13design 2020 lineage) |
| [010_crispr_diagnostics](010_crispr_diagnostics.md) | CRISPR diagnostics (Cas12/Cas13 biosensors) | incomplete metric replay; **review-gated for pathogen targets** | EasyDesign ρ 0.812 n=11,496 |
| [011_crispr_library-screen-design](011_crispr_library-screen-design.md) | pooled library / screen design | shared guide metrics ([RS3](../benchmark/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) · [CRISPRon](../benchmark/002_CRISPRon/Run-4_2026-11-12/REPORT.md)), not screen validation | RS3 tiling 84,609; Lukasiak-2024 screen-level; multi-targeting literature |
| [012_crispr_plant-editing](012_crispr_plant-editing.md) | plant / crop editing | **inactive** — author-score replay archived; no design runs | pending species adapter (no plant activity model verified) |
| [013_crispr_microbial](013_crispr_microbial.md) | microbial CRISPR design | author-score replay (MERF 642 comparisons) | Guo-2018 + Yu-2024 bacterial models |

Non-runnable scopes stay gated by design: pathogen-targeting diagnostics sequence design
is review-only (task 010 documents the gate; contrived/non-pathogen targets remain
runnable); plant editing is inactive pending a species adapter (task 012 documents the
refusal). Adding a task does not make its application biologically validated — benchmark
status is stated per task; local model/component evidence must not be generalized to an
unvalidated application.
