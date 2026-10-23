#!/usr/bin/env python3
"""Generate the frozen GeoOpt-Bench v0.1 specialist contracts and pilot cards."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = [
 ("01","structure-input-validation","Structure Input Validation Agent","Validate molecular files, coordinates, elements, missing atoms, duplicates, and malformed structures.","input_invalid"),
 ("02","molecular-connectivity","Molecular Connectivity Agent","Detect incorrect bonds, unusual valence, missing connectivity, and inconsistent bond orders.","connectivity_invalid"),
 ("03","initial-conformation","Initial Conformation Agent","Detect distorted starting geometries, steric clashes, and poor conformers before optimisation.","input_invalid"),
 ("04","charge-multiplicity","Charge and Multiplicity Agent","Validate charge, electron count, spin multiplicity, and electronic-state settings.","electronic_state_invalid"),
 ("05","qm-method-selection","QM Method Selection Agent","Select supported DFT method, basis, and settings with a reproducible rationale.","method_unsupported"),
 ("06","optimizer-selection","Optimizer Selection Agent","Choose BFGS, L-BFGS, trust-region, or another supported optimizer for the case.","optimizer_stagnation"),
 ("07","internal-coordinate-optimization","Internal Coordinate Optimisation Agent","Assess internal versus Cartesian coordinates and compare optimisation evidence.","geometry_unconverged"),
 ("08","constraints-boundaries","Constraints and Boundary Conditions Agent","Validate fixed atoms, distances, restraints, and symmetry requirements.","constraint_violation"),
 ("09","scf-convergence","SCF Convergence Agent","Diagnose SCF failures and propose bounded recovery settings without changing the state silently.","scf_failure"),
 ("10","geometry-convergence","Geometry Convergence Agent","Classify energy, gradient, displacement, and stopping-criterion evidence.","geometry_unconverged"),
 ("11","optimization-stagnation","Optimisation Stagnation Agent","Detect oscillation, repeated structures, and stalled progress with a controlled recovery plan.","optimizer_stagnation"),
 ("12","gradient-force-validation","Gradient and Force Validation Agent","Validate gradient shape, finite values, signs, units, and consistency with energy changes.","gradient_invalid"),
 ("13","hessian-minimum-verification","Hessian and Minimum Verification Agent","Distinguish a local minimum from a saddle point using Hessian or frequency evidence.","not_a_minimum"),
 ("14","multi-conformer-optimization","Multi-Conformer Optimisation Agent","Optimise, cluster, and rank multiple conformers at a consistent theory level.","geometry_unconverged"),
 ("15","protein-ligand-geometry","Protein-Ligand Geometry Agent","Check ligand clashes, binding-site geometry, coordination, and interaction preservation.","constraint_violation"),
 ("16","runtime-resource-recovery","Runtime and Resource Recovery Agent","Diagnose runtime, memory, checkpoint, and resumability failures without silent setting changes.","resource_failure"),
 ("17","optimized-structure-quality","Optimised Structure Quality Agent","Independently validate final coordinates, energies, gradients, metadata, and reference deviations.","reporting_error"),
 ("18","geo-opt-orchestrator","Geo-Opt Orchestrator Agent","Route cases conditionally, manage retries, and consolidate an auditable workflow trace.","review_required"),
]

def main() -> None:
    contracts = ROOT / "contracts"; tasks = ROOT / "tasks"; refs = ROOT / "references"
    contracts.mkdir(exist_ok=True); tasks.mkdir(exist_ok=True); refs.mkdir(exist_ok=True)
    task_rows = []
    for aid, slug, name, role, failure in AGENTS:
        contract = {
            "schema_version":"1.0", "id":aid, "slug":slug, "name":name,
            "role":role, "task_type":"single_step", "failure_category":failure,
            "required_inputs":["task card", "initial geometry or preserved artifact", "method/settings", "resource limits"],
            "required_outputs":["decision", "scientific checks", "evidence references", "failure category", "cost and reproducibility fields"],
            "acceptance_criteria":["all mandatory checks are explicit", "no unsupported scientific claim", "settings and artifacts are hashable", "decision is reproducible"],
            "agent_scientist_required":False
        }
        (contracts / f"agent_{aid}_{slug}.json").write_text(json.dumps(contract, indent=2)+"\n")
        task_id=f"GEOOPT-{aid}-PILOT-001"
        task={"task_id":task_id,"agent_id":aid,"title":name,"task_type":"single_step","role":role,"input_fixture":"references/pilot_initial_geometry.xyz","expected_failure_category":failure,"scoring":{"required_checks":["structure_valid","energy_finite","gradient_finite","convergence_classified"],"numerical_tolerance":"declared per task; never inferred from pass rate"}}
        (tasks / f"task_{aid}_{slug}.json").write_text(json.dumps(task, indent=2)+"\n")
        (tasks / "prompts").mkdir(exist_ok=True)
        (tasks / "prompts" / f"task_{aid}_{slug}.md").write_text(
            f"# {task_id}: {name}\n\n"
            f"Use only the supplied frozen input and declared tools. {role}\n\n"
            "Return a structured submission with a decision, evidence for every mandatory check, "
            "failure category when applicable, and wall time/retry/token provenance. Do not infer "
            "a minimum from energy alone.\n"
        )
        task_rows.append(task)
    workflows = [
      {"workflow_id":"GEOOPT-WF-001","name":"validate-optimize-verify","steps":["01","04","05","06","09","10","12","13","17"]},
      {"workflow_id":"GEOOPT-WF-002","name":"conditional-recovery","steps":["01","03","09","11","16","17","18"]},
      {"workflow_id":"GEOOPT-WF-003","name":"multi-conformer-quality","steps":["03","06","10","13","14","17","18"]},
      {"workflow_id":"GEOOPT-WF-004","name":"constrained-complex","steps":["01","02","08","15","17","18"]},
      {"workflow_id":"GEOOPT-WF-005","name":"failure-recovery-audit","steps":["04","09","11","12","16","17","18"]},
    ]
    (ROOT/"workflows").mkdir(exist_ok=True)
    (ROOT/"workflows/manifest.json").write_text(json.dumps({"schema_version":"0.1","workflow_count":len(workflows),"workflows":workflows},indent=2)+"\n")
    (refs/"pilot_initial_geometry.xyz").write_text("3\nwater pilot geometry; replace with frozen fixture before engine qualification\nO 0.000000 0.000000 0.000000\nH 0.758602 0.000000 0.504284\nH -0.758602 0.000000 0.504284\n")
    (tasks/"manifest.json").write_text(json.dumps({"schema_version":"0.1","benchmark":"GeoOpt-Bench","task_count":18,"tasks":task_rows,"workflow_count":5},indent=2)+"\n")
    (ROOT/"references/README.md").write_text("# Reference artifacts\n\nThe pilot geometry is a placeholder fixture for schema smoke tests. Replace it with hashed trusted optimization references before claiming scientific qualification.\n")
    print(json.dumps({"contracts":18,"tasks":18,"workflows":5}))

if __name__ == "__main__": main()
