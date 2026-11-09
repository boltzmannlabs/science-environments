# Paper reference

- **Title:** Exploring ligand binding pathways on proteins using hypersound-accelerated molecular dynamics
- **DOI:** https://doi.org/10.1038/s41467-021-23157-1
- **Data:** BSM-00027 (published trajectories and processed data)
- **Selected system:** CDK2–CS3; crystal structure PDB 4EK5
- **Engine:** modified GROMACS 4.6.5
- **Electrostatics:** PME; 10 Å cutoff
- **Constraints:** P-LINCS; all bond lengths constrained
- **Timestep:** 2 fs
- **Equilibration:** 100 ps NVT, then 100 ps NPT with protein-heavy-atom restraints
- **Production:** NPT, 298 K, 1 bar, no positional restraints, 100 ns per conventional run
- **Thermostat/barostat:** stochastic velocity rescaling / Parrinello–Rahman; time constants 0.1 ps and 2 ps
- **Unresolved:** exact protein force-field revision and complete CS3 topology are not inferred from this article alone; supplementary/input archive must be retained as provenance.
