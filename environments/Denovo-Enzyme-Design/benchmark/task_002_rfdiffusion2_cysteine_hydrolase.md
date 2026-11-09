**Task ID:** `task_002_rfdiffusion2_cysteine_hydrolase`

**Task:** [Cysteine hydrolase design](../tasks/task_002_rfdiffusion2_cysteine_hydrolase.md)

## Published Results

**Source:** [Ahern et al., *Atom-level enzyme active site scaffolding using RFdiffusion2*, Nature Methods 23, 96–105 (2026)](https://doi.org/10.1038/s41592-025-02975-x), Figure 4b; [Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-025-02975-x/MediaObjects/41592_2025_2975_MOESM1_ESM.pdf), section D.2 and Figure S12.

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Global design–prediction agreement | **Global Cα RMSD 0.57 Å** for **Eta1**. | Figure S12 caption: AlphaFold2 prediction compared with the design model after LigandMPNN and constrained Rosetta FastRelax. This is a particular design's outcome. |
| Global and catalytic recovery | Published selection thresholds: **global Cα RMSD <1.5 Å; catalytic-residue Cα RMSD <1.0 Å; motif-residue heavy-atom RMSD <1.0 Å**. | Section D.2. Catalytic Cα RMSD is assessed after global Cα alignment. These selection conditions must remain distinct from Eta1's observed 0.57 Å global result. |
| Catalytic interaction geometry | Published median-distance filters: **Cys Sγ–His Nδ1 <3.8 Å; His Nε2–Asn Oδ1 <3.3 Å**. | Section D.2, PLACER assessment. These are geometric selection conditions, not observed per-design ensemble medians. |
| Acyl-enzyme oxyanion interactions | Published median-distance filters: **acyl carbonyl O–Cys backbone N <3.3 Å; acyl carbonyl O–Gln Nε2 <3.5 Å**. | Section D.2, acyl-enzyme predictions using the CY4 cysteine modification. The two donor interactions must be measured separately. |
| Structural similarity to a known protein | **TM-score 0.53** against **PDB 5K7V** for the depicted design. | Figure 4b. This selected-design match does not establish a universal acceptance boundary. |

The motif heavy-atom calculation and the globally aligned catalytic Cα calculation are different measurements. Constraint tolerances used during refinement are not observed recovery errors. Numerical state-geometry comparisons require the corresponding underlying ensemble records.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Global structural agreement | Compare corresponding final-design and independent-prediction Cα atoms after declared global alignment. | Published selection boundary <1.5 Å; Eta1’s observed 0.57 Å is a separate individual reference, not the pass threshold. |
| Catalytic-site recovery | Report globally aligned catalytic Cα RMSD separately from motif-aligned heavy-atom RMSD, with explicit atom symmetry handling. | Published selection boundaries: catalytic Cα RMSD <1.0 Å and motif heavy-atom RMSD <1.0 Å under matched definitions. |
| Catalytic interaction geometry | Match substrate-bound/acyl-state chemistry, protonation, topology, ensemble statistic and atom pairs. | Published median-distance filters: Cys Sγ–His Nδ1 <3.8 Å and His Nε2–Asn Oδ1 <3.3 Å; these are filters, not reported ensemble outcomes. |
| Acyl-enzyme oxyanion interactions | Measure carbonyl-oxygen interactions with Cys backbone N and Gln Nε2 separately in the covalent acyl state. | Published median-distance filters: <3.3 Å and <3.5 Å, respectively; a noncovalent substrate pose is not a substitute. |
| Structural similarity | Match database/search scope, chains and normalization. | The depicted design’s TM-score 0.53 against 5K7V is a reference observation, not a universal acceptance boundary. |
| Input and design validity | Preserve the catalytic atom mask, local backbone context, catalytic identities and exact substrate/intermediate definitions. | Missing covalent-state parameters or invalid mappings leave the affected state assessment unresolved rather than assigning a score. |
