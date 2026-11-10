# FEP paper-reproduction benchmark — milestone update

## Independent paper-protocol reconstruction and endpoint-readiness validation

Implemented locally on the `Boltsim` branch and committed as `c6a3241`.

### Demonstrated capabilities

- Literature-to-configuration reconstruction from the published protocol and public source configuration.
- Molecular system identification with the CDK2 edge `17 -> 1h1q` pinned to a specific source revision.
- Constrained MCS atom mapping plus an OpenFE/Lomap candidate mapping with
  explicit limitations and provenance.
- Protocol fidelity: Config B independently reconstructed and matched 20/20 evaluated reference fields.
- Readiness assessment that reports missing scientific evidence instead of treating setup success as FEP success.

### Validation evidence

- FEP task tests: `8 passed`.
- SAMPL6 manifest validation: passed.
- Config B explicit parameter comparison: `20/20`, accuracy `1.0`.
- Endpoint-readiness gate: `REVIEW`.
- OpenFE/Lomap mapping: one candidate, 45 mapped atoms, topology validation
  still required.
- Protein-only endpoint preparation: OpenMM system generated for all 9,013
  CDK2 particles using AMBER ff14SB plus the pinned phosphoamino-acid
  parameters. This is not yet a complex or solvent FEP endpoint.
- GAFF2 ligand parameterization completed for both endpoints using the
  source-provided Jaguar charges; `tleap` generated both unsolvated complex
  and ligand-solvent endpoint topologies. Solvation, ion composition and the
  alchemical hybrid topology remain separate validation gates.

### Current qualification

The protocol reconstruction is complete for the evaluated fields. Production FEP
qualification is not complete. Complex and solvent endpoint topologies, an
approved alchemical topology, lambda-window trajectories, replica metadata,
overlap, convergence, uncertainty, and publication-equivalent free-energy
comparison remain outstanding. No production ΔΔG or paper-level reproduction is
claimed.

### Next execution order

1. Solvate and ionize both endpoint systems, then independently validate the
   resulting complex and solvent coordinates and charges.
2. Generate all source-consistent lambda windows and preserve inputs, logs,
   checkpoints and trajectories.
3. Run overlap, convergence, effective-sample-size, uncertainty and replica
   checks for both legs.
4. Calculate complex and solvent ΔG and derive ΔΔG only after the evidence gates
   pass.
5. Compare Config A, Config B, Config C and Config D using frozen independent
   evaluators; keep Config B isolated from evaluator reference data.

### Boss-ready update

Config B now independently reconstructs the published FEP protocol for the
pinned CDK2 transformation. The agent achieved 100% accuracy across 20
evaluated protocol fields, with eight task tests and SAMPL6 manifest validation
passing. This milestone demonstrates independent paper-protocol reconstruction
and endpoint-readiness validation, not production FEP reproduction. The next
milestone is complete endpoint preparation followed by lambda-window execution
and scientific qualification.
