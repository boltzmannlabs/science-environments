# FEP-PAPER-005 — force-field sensitivity

- **Paper:** Sun and Huggins (2022).
- **DOI:** `10.3389/fmolb.2022.972162`.
- **System:** CDK2 `1H1Q`, ligand `17 → 1h1q`.
- **Inputs:** frozen copies of the pinned CDK2 protein and ligand endpoints.
- **Paper-derived fields:** OpenMM 7.2, GAFF 2.11, AM1-BCC/RESP charge
  comparison, AMBER protein force field, TIP3P water and Hamiltonian replica
  exchange workflow.

The local task evaluates parameter extraction and controlled configuration
construction. It does not infer missing values from a successful run.
