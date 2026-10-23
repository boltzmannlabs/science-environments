# Result: geo_opt_12_gradient-force-validation

## Description

Validate gradient shape, finite values, signs, units, and consistency with energy changes.

## System input

- Task ID: `12` / `gradient_validation`
- Input fixture: `tasks/agent_inputs/agent_12_gradient_validation.json`
- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution was used
- Acceptance criteria: finite coordinates, finite energy, verified convergence where applicable

## Expected output

- decision
- scientific checks
- evidence references
- failure category
- cost and reproducibility fields

## Observed result

- Status: **pass**
- Execution: `live_gpu_engine`
- Energy: `-76.407024051240 Hartree`; max gradient: `2.588e-05 Hartree/Bohr`; backend: `GPU4PySCF+SciPy-BFGS`.

## Limitations and review notes

Live engine evidence is available for this case.
The result is scoped to this frozen input packet and does not claim capabilities outside the agent contract.
