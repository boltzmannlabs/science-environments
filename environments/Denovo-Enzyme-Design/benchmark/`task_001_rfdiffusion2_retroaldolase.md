
**Task ID:** `task_001_rfdiffusion2_retroaldolase`

**Task:** [Retro-aldolase active-site scaffold design](../tasks/task_001_rfdiffusion2_retroaldolase.md)

## Published Results

**Source:** [Ahern et al., *Atom-level enzyme active site scaffolding using RFdiffusion2*, Nature Methods 23, 96–105 (2026)](https://doi.org/10.1038/s41592-025-02975-x), Figure 4a; [Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-025-02975-x/MediaObjects/41592_2025_2975_MOESM1_ESM.pdf), section D.1.1 and the filter table below Figure S10, printed pages 68–69.

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Catalytic sidechain heavy-atom RMSD from the design | Published selection thresholds: **Lys1083 <0.95 Å; Tyr1051 <1.26 Å; Tyr1180 <1.25 Å; Asn1110 <1.02 Å**. | D.1.1 filter table. Per-residue ensemble means are averaged over six chemical states. These are selection boundaries, not observed candidate scores or cohort means. |
| Within-ensemble catalytic sidechain RMSF | Published selection thresholds: **Lys1083 <0.34 Å; Tyr1051 <0.92 Å; Tyr1180 <0.93 Å; Asn1110 <0.28 Å**. | D.1.1 filter table; the same six-state averaging applies. RMSF measures variation within an ensemble, rather than displacement from the design. |
| Substrate hydrogen-bond occupancy | Published selection thresholds: **Tyr1051 ≥38%; Tyr1180 ≥18%**. | D.1.1 filter table, `hbond_fraction_res2` and `hbond_fraction_res3`. Average the interaction fractions over the five ligand-containing states; exclude apo from this denominator. |
| Structural similarity to a known protein | **TM-score 0.47** against **PDB 6SU3** for the depicted design. | Figure 4a. This is one selected design's structural match, not a universal novelty cutoff or a cohort mean. |

The PLACER assessment uses **50 models for each of six states**: apo, noncovalent enzyme–substrate complex, and four carbinolamine stereoisomers. The filter identifiers `res1`–`res4` map to **Lys1083, Tyr1051, Tyr1180 and Asn1110**, respectively. The preceding motif-description sentence contains an inconsistent asparagine number; use the explicit filter mapping and the task's verified residue correspondence.

Exact individual RMSD, RMSF and occupancy observations are not supplied by the threshold table. Do not replace missing candidate-level reference data with the threshold values.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Catalytic-site recovery | Match sidechain-heavy-atom selections, design alignment, atom equivalence and six-state averaging. Preserve residue mappings. | Published selection boundaries: Lys1083 <0.95 Å; Tyr1051 <1.26 Å; Tyr1180 <1.25 Å; Asn1110 <1.02 Å. These are method-matched filter values, not observed candidate outcomes. |
| Active-site flexibility | Match within-ensemble alignment and sidechain RMSF; retain each state before six-state averaging. | Published selection boundaries: Lys1083 <0.34 Å; Tyr1051 <0.92 Å; Tyr1180 <0.93 Å; Asn1110 <0.28 Å. RMSF is distinct from displacement from the design. |
| Substrate interaction occupancy | Match donor/acceptor definitions, geometric hydrogen-bond predicate and five ligand-containing states; exclude apo from the denominator. | Published selection boundaries: Tyr1051 ≥38%; Tyr1180 ≥18%. Altered states, definitions or denominators require separate reporting. |
| Structural novelty | Retain database snapshot, nearest-neighbour method, alignment chains and TM-score normalization. | The depicted design has TM-score 0.47 against 6SU3. This is an individual reference observation, not a universal novelty cutoff; fixed-pair alignment is not a database search. |
| Input and design validity | Verify catalytic identities, nine protected atoms, modified residues, LLK connectivity, state chemistry and source/prepared mappings. | Required mappings and chemistry must be valid; a favorable structural score cannot compensate for an invalid motif or state. |
