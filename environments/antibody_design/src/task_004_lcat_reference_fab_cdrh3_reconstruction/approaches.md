# Task 004 approaches

## Target and objective

Reconstruct the 19-residue heavy-chain CDR-H3 of the 5BV7 reference Fab and compare sequence recovery, contact-residue recovery, structural recovery, interface preservation and basic developability.

## Considered and executed approaches

| ID | Approach | Execution status | Role | Main result |
|---|---|---|---|---|
| W1 | AgCDR-Diff -> AntiBMPNN | Completed | Primary Boltzmann target-aware backbone plus sequence workflow | 24 backbones, 240 sequences; best AAR 0.2105; best loop RMSD 7.448 Å; interface largely lost |
| W2 | CDR_Generator/EvoDiff | Completed | Boltzmann sequence-only baseline | 24 sequences; best AAR 0.2632; no structures |
| W3 | IG-Design | Failed | Boltzmann target-aware sequence design | Internal worker `KeyError: 'aa_regions'`; no scientific output |
| W4 | Epitope AbGen | Pending/no output | Boltzmann epitope-aware generation | No output produced in the run |
| W5 | ProteinMPNN -> Boltz2 | Completed in prior work | Open-source comparison and validation workflow | 20 designs, top 3 structured; best AAR 0.4737, CAAR 0.5714, RMSD 6.456 Å |

## Selection decision

W1 was selected as the primary Boltzmann workflow because it combines target-aware backbone generation with sequence design. W2 was retained as a sequence baseline. W5 was retained as the complete comparison workflow because it was the strongest measured result and supplied both sequence and structure outputs.

## Suitability assessment

- W1 is suitable for target-conditioned exploration but was not suitable for final selection here because its generated loops did not preserve the antigen interface.
- W2 is suitable for fast sequence-library generation and sequence recovery screening, but it cannot establish structure or binding competence alone.
- W3 and W4 cannot support a conclusion in this run because they did not produce usable scientific artifacts.
- W5 was most effective for this single-case reconstruction, but its structural result remains computational and its confidence did not imply native-loop recovery.
