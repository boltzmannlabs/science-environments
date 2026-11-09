# Paper reference

- **Title:** Assessing the effect of forcefield parameter sets on the accuracy of relative binding free energy calculations
- **DOI:** https://doi.org/10.3389/fmolb.2022.972162
- **Code/data:** https://github.com/shansun7994/Alchaware_v5.0
- **Selected target:** CDK2, PDB 1H1Q
- **Engine:** OpenMM 7.2 with OpenMMTools Hamiltonian replica exchange
- **Ligand force field:** GAFF 2.11
- **Charge methods:** AM1-BCC and RESP (paper comparison arms)
- **Preparation:** local energy minimization for all states; ligand alignment by maximum common substructure
- **Legs:** ligand A→B in protein complex and in solvent
- **Unresolved:** exact selected ligand edge and complete parameter/topology files must be pinned from the public code/data before production FEP.
