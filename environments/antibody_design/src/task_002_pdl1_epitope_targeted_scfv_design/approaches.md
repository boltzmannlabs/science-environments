# Task 002 approaches

Task: PD-L1 epitope-targeted scFv design.

## Considered approaches

### A — Epitope-conditioned CDR design
Tools: `epitope_abgen` -> `AntiBMPNN` -> `Boltz2` -> `Antibody_Prediction`.

Suitability: highest. It directly conditions CDR generation on PD-L1 residues A37, A39, A41, A96 and A98 while preserving the supplied antibody framework.

Status: submitted as Boltzmann job `epitope_abgen`, doc_id `6af33484b2d9f21f0dc8d50e`; no output was returned after more than two hours. No downstream stage ran. This is retained as a failed/pending attempt, not as completed scientific output.

### B — RF-Antibody generation
Tools: `rfdiffusion_proteinmpnn` -> local open-source Boltz-2 -> `Antibody_Prediction`.

Suitability: practical fallback. It generates sequences and structural candidates in one platform job, but conditions on the whole antigen surface rather than the declared epitope. Epitope targeting was therefore evaluated post-hoc from predicted structures.

Status: executed. The platform output contained 20 generated candidates. The local Boltz-2 batch explicitly evaluated 10 candidates; 5 were shortlisted for platform property prediction.

### C — AgCDR-Diff
Tools: `agcdr_diff` -> sequence design -> Boltz2 -> property prediction.

Suitability: low for this input because the method requires an antibody-antigen complex already positioned in one coordinate frame. The task input was a free generic framework plus a free PD-L1 V-like domain.

Status: not run.

## Selection decision

Workflow A was selected during planning because it best matched the epitope-targeted objective. Because it produced no output, Workflow B became the executed workflow. The final recommendation is based on Workflow B's measured post-hoc hotspot engagement and interface confidence, with the epitope-abgen failure explicitly reported.
