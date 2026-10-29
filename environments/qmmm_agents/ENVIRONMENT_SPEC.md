# QM/MM Environment Specification

## Inputs

Prepared coordinates and topology, QM region and boundary, link-atom policy,
MM parameters, QM method/basis, total and region charges, multiplicity,
embedding mode, engine/version, convergence settings, trajectory/checkpoint,
and reference energy/force criteria.

## Outputs

Region and boundary audit, charge/embedding audit, QM SCF evidence, coupling
and force checks, sensitivity report, trajectory recovery record, provenance,
and typed PASS/FAIL/REVIEW status.

## Non-negotiable rules

Preserve original inputs and evaluator thresholds. Do not silently change the
QM region, charge, embedding, link atoms, force field, or method. Running QM
and MM separately is not evidence that the coupled calculation is valid.
