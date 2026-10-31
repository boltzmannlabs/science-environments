# Scientific and code review — 29 October 2026

**Scope:** environment specifications, task/example inputs, configuration/schemas, six runtime modules, tests and supporting research notes. This is a source and software review; no enzyme-design, property or chemistry job was launched.

The scientific framework separates exploratory generation, computational assessment and experimental activity. The reaction/assembly requirements, distinct property endpoints, control-based method assessment and distinction between potential-energy and free-energy evidence are appropriate within the declared soluble, cofactor-free monomer/homodimer scope. Supporting primary sources are recorded in [references](../../../research/Denovo-Enzyme-Design/references.md).

Corrections made:

- Required user property targets now bind to explicit required rules with unchanged endpoints, units and criteria. Finalization rechecks the qualification contract.
- Each declared active site needs a directed reactant-to-product path. Final profiles preserve the generation site's catalytic-map identity. These checks do not calculate reaction energetics or verify atom-resolved mechanisms.
- Hosted-tool locks can record actual service provenance and undisclosed backend details without invented code/weight hashes. Hosted checks no longer universally require private inference internals.
- Execution records reject empty receipts or wholly empty raw outputs. Captured invocations and chemistry-exception evidence must be nonempty.
- Structure preparation rejects ambiguous PDB mappings, multiple models and undefined geometric measurements. A collinear dihedral cannot be reported as a cis peptide. Installed software versions replace a hardcoded version label.
- The development adapter's cis-Pro limitation and the current template-free independent-prediction contract are explicit. PARTIAL and NO_QUALIFYING_DESIGNS are reportable outcomes, not successful scientific qualification.

Validation results and current source hashes are in [runtime-validation.json](runtime-validation.json) and [specification-validation.json](specification-validation.json). Tests use synthetic records where stated; they are not provider attestations or molecular measurements.

Both example net reactions passed elemental/charge-balance checks. The L-DEX example's S substrate and R product were checked against the saved reference SDFs with RDKit. These checks establish molecular bookkeeping only; they do not qualify a mechanism or designed enzyme.

Remaining limits:

- Actual generator, property, assembly and chemistry capabilities still need applicable controls and execution evidence. The full workflow has not qualified an enzyme.
- An agent's review, schema compliance and matching hashes cannot establish the truth of self-reported scientific results. Original outputs, method applicability and uncertainty must be reviewed.
- Hosted backend opacity can limit reproducibility and comparability. Template-assisted structural assessment and non-Pro cis preparation need supported extensions/routes.
- RL is a specified extension; the delivered controller executes fixed stages with bounded agent review and recovery.
