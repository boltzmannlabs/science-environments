# FEP-ENV-01 — Protein–Ligand Relative Binding Affinity

**Purpose:** Estimate a ligand A→B relative binding free energy from matched complex and solvent legs. The repository currently provides a bounded dual-topology qualification fixture; it does not claim a production protein–ligand estimate.

**Inputs:** mapped ligand pair, validated topology/parameters, protein complex and solvent systems, charge/multiplicity, lambda protocol, replicas, seeds, and reference data.

**Procedure:** validate mapping and endpoints; execute identical lambda windows for both legs; analyse overlap, block convergence, replica agreement, cycle/sign conventions, and uncertainty.

**Acceptance:** PASS only when both legs complete, adjacent-window overlap and effective sample size meet frozen thresholds, replicas agree, and the result is reproducible. Otherwise REVIEW/FAIL with evidence. This task is not qualified by an exit code alone.
