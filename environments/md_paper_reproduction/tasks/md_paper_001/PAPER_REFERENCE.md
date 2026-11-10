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
- **Source archive:** `https://bmdi-db.med.kyoto-u.ac.jp/owncloud/index.php/s/L8rwegnll6yXj5l`, directory `hypersound_MD/input_files/CDK2_CS3/`.
- **Pinned source system:** `em.gro` contains 60,120 atoms, 50 `LIG` molecules, 17,820 waters, 54 sodium ions and 58 chloride ions in an 8.43544 nm cubic box. Its `topol_fin.top`, ligand include and three MDP files are retained under `inputs/paper_source/cdk2_cs3/` with hashes in `evaluation/paper_source_provenance.json`.
- **Unresolved:** the source topology references an `amber99sb-ildn.ff` directory that is not redistributed, and the archive system is a 50-ligand preparation rather than a single-ligand bound pose. Coordinate readability is validated; topology preprocessing and production dynamics remain REVIEW.
