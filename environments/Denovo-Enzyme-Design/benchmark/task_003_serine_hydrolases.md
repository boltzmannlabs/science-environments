
**Task ID:** `task_003_serine_hydrolases`

**Task:** [Serine hydrolase motif scaffolding and multistate assessment](../tasks/task_003_serine_hydrolases.md)

## Published Results

**Source:** [Lauko et al., *Computational design of serine hydrolases*, Science 388, eadu2454 (2025)](https://doi.org/10.1126/science.adu2454), Figure 5C and its accompanying text; [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12288761/).

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Predicted Ser–His catalytic angle, turnover-design group | **Median 94°**, pooled across the reported states. | Figure 5C. Ser(Oγ)–His(Nε)–His(Cε), with His Nε at the vertex. The group is defined by the authors' activity classification; the reported quantity is a predicted structural angle. |
| Predicted Ser–His catalytic angle, inactive-design group | **Median 108°**, pooled across the reported states. | Figure 5C, same atom definition. This is a group median, not an individual-design rejection threshold. |

Neither median supplies an exact per-state distribution or a substrate-specific reference for every campaign. The task's phenylacetate cohort and five-state assessment must not be silently pooled with other substrates or different state panels to reproduce the published medians. A new candidate's angle does not assign it to either published activity class.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Angle definition | Use Ser(Oγ)–His(Nε)–His(Cε), with His Nε as vertex; retain residue/atom mappings and report degrees. | Calculate independently of generation restraints. Mapping failures and genuine geometric outliers remain distinct. |
| State distributions | Report individual observations, medians and counts for apo, substrate, first tetrahedral, acyl-enzyme and second tetrahedral states before pooling. | Use declared state weights and retain incomplete sampling explicitly; pooled statistics do not replace per-state evidence. |
| Published group comparison | Keep phenylacetate, acetate and butyrate cohorts and sequence-only versus contact-assisted prediction regimes separate. | 94° and 108° are published pooled group medians, not individual candidate acceptance thresholds or activity classifiers. |
| Input and design validity | Verify the protected motif segments, serine–histidine–acid network and state-specific ligand topology and serine modification. | A numerical angle is valid only for the declared chemical state and correct ordered atoms; it does not establish catalytic activity. |
