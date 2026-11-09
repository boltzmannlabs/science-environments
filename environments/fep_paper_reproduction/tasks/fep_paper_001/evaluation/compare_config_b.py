#!/usr/bin/env python3
"""Independent evaluator for the generated Config B setup."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
generated = json.loads((ROOT / "execution/generated_inputs/config_B_agent_generated.json").read_text())["configuration"]
reference = json.loads((ROOT / "reference/extracted_parameters.json").read_text())

checks = {
    "engine": generated["engine"] == reference["engine"],
    "toolkit": generated["toolkit"] == reference["toolkit"],
    "ligand_forcefield": generated["ligand_forcefield"] == reference["ligand_forcefield"],
    "complex_and_solvent_legs": set(generated["legs"]) == set(reference["legs"]),
    "mapping": generated["mapping"].lower() == reference["mapping"].lower(),
    "charge_methods": set(generated["charge_methods"]) == set(reference["charge_methods"]),
    "target": generated["target"] == reference["target"] and generated["pdb_id"] == reference["pdb_id"],
    "selected_edge": generated["ligand_a"] == reference["ligand_a"] and generated["ligand_b"] == reference["ligand_b"] and generated["direction"] == reference["direction"],
}
checks.update({
    key: generated["protocol"].get(key) == reference[key]
    for key in ("water_model", "ionic_strength_molar", "box_padding_nm", "sterics_steps", "electrostatics_steps", "sterics_exponent", "timestep_fs", "steps_per_iteration", "equilibration_iterations", "production_iterations", "extension_iterations", "iterations_per_checkpoint")
})
result = {
    "agent_config": "execution/generated_inputs/config_B_agent_generated.json",
    "checks": checks,
    "matched": sum(checks.values()),
    "total": len(checks),
    "parameter_accuracy": sum(checks.values()) / len(checks),
    "status": "REVIEW" if generated["unresolved"] else ("PASS" if all(checks.values()) else "FAIL"),
    "reason": "source-pinned endpoint and protocol fields are compared; unresolved topology, mapping, trajectory and replica evidence prevent scientific PASS",
}
(ROOT / "evaluation/config_B_comparison.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
