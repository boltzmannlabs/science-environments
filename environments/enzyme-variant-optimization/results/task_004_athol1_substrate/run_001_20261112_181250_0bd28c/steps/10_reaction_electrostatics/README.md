# Reaction-site electrostatics

Completed separate post-selection assessment: evaluated parent, reconstructed V140T reference and retained ATH_R2_09 candidate. Each exact 235-residue construct has one 30 ns trajectory (first 5 ns discarded), 250 field snapshots and 25 explicit C–I localized-orbital calculations. Primary field contributions use residues 13–228; the full construct participates in dynamics.

[predictions.csv](sha256-d3b9170840e9a3f906d3625d38a30ace1bcd3197134ccb02a163afe8ee70ed4d-420d706c_unreported_unreported_0bd28c_unreported_unreported.csv) retains numerical values, units, sample SD, conditional block intervals and source categories. Original published calculations, our alternative calculations, literature-converted measurements and uncomputed endpoints are explicitly separate. Only prediction rows are plotted in the benchmark.

OpenMM 8.6.1 uses ff14SB protein, TIP3P water and the deposited GAFF/AM1-BCC SAH/ethyl-iodide parameters at 293.15 K with 2 fs constrained-hydrogen steps. Sampling retains the declared reaction-coordinate restraints. PySCF 2.15.0 uses DF-PBE0/def2-TZVP (iodine def2 ECP), grid level 3 and Pipek–Mezey localized occupied orbitals. Protein-only Coulomb fields are evaluated at the ethyl-iodide C–I midpoint, positive along C→I, with factor 1439.96454784255 MV/cm per e/Å².

Our pre-reaction interaction is −μ_CI·E_protein. It is distinct from an activation barrier or activity. The alternative protocol uses 30 ns and a full 235-residue construct; the paper describes 110 ns and a truncated 216-residue model. Geometry and localized-dipole angles are separate endpoints. The paper's main-text stabilization is −7.8 kcal/mol; SI Table S2 gives −7.7.

Single-trajectory SD and conditional five-block intervals describe sampling, not biological replication or preparation/model uncertainty. Site/structure drift remains visible; trajectory convergence is not established. Candidate-minus-parent interaction is +0.177 kcal/mol with conditional interval [−0.124, +0.478], so no interaction improvement is resolved.

Sequence SHA-256:

- parent: `7a11b6534e3d4c598e2eabe3bb5b2c190400ffb83dd426d8b0b4a021895e4d52`
- reference: `092b3e5c32d83dff14a9657426e1be4a8c20d81855113a3228ce2117e8be74fb`
- retained_candidate: `2a85ab14a674db7b9dd324468245d9909ba4dc35cae1b93d52f9fb3afb319825`

Sources: [Shao et al.](https://doi.org/10.1016/j.checat.2025.101334), [released inputs and code](https://zenodo.org/records/14955076).
