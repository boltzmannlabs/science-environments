# Benchmark: PD-L1: Epitope-Targeted scFv Design

**Task ID:** `task_002_pdl1_epitope_targeted_scfv_design`

**Task:** [PD-L1: Epitope-Targeted scFv Design](../../tasks/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md)

**Reviewed:** 2026-11-05

## Benchmark Scope

Framework-conditioned paired-domain scFv design, with H5 as a published comparison antibody. Individual structural validation and campaign-level novelty are separate benchmarks.

## Published Results

**Source:** [Efficient generation of epitope-targeted antibodies with Germinal, Nature Biotechnology (June 2026)](https://doi.org/10.1038/s41587-026-03187-0); [accessible manuscript, scFv results and Figure 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC13366713/).

| Published metric | Reported value | Scope and interpretation |
| --- | ---: | --- |
| H5 predicted-versus-experimental global Cα RMSD | **1.25 Å** | Individual PD-L1/H5 complex; structural agreement with cryo-EM coordinates. Lower is better. |
| PD-L1 scFv designs passing computational filters | **470** | Campaign yield, not affinity or per-candidate quality. |
| Designs selected for experimental validation | **48** | Selection count; not a computational success rate. |
| CDR identity to known sequences | Approximately **40%; <52%** | Reported scFv novelty analysis across the PD-L1/IL3 design context; not an H5-specific score. |
| Interface similarity to known complexes | **IS ≤ 0.2** | Reported scFv novelty comparison; lower indicates greater interface novelty under that definition. |
| Final H5 pLDDT, ipTM, PAE and pDockQ | **Not verified** | No numeric candidate-level values established by the inspected evidence. |

The paper reports H5 structural deposition as PDB **35TL** and EMDB **EMD-77181**. Verify accession availability and chain mapping before use. The 1.25 Å result is the principal individual structural benchmark; dataset novelty results and campaign counts must remain separate. Do not substitute scores from other implementations or VHH campaigns.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| H5 structural reconstruction | Compare a prediction of H5 with independent H5 complex coordinates using documented Cα matching and alignment. | The 1.25 Å result is applicable to H5 reconstruction; it is not ground truth for a different generated sequence. |
| New candidates | Assess declared framework/linker constraints, epitope accessibility, geometry and per-candidate evidence. | Use a frozen evaluation protocol; campaign counts do not supply acceptance thresholds. |
| Novelty | Record the sequence/structure databases and exact similarity definition. | Do not substitute novelty for binding evidence. |
