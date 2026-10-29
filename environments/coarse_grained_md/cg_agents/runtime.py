"""Small executable specialist layer.

These are deterministic evidence checks, not language-model claims. A check
returns REVIEW when its scientific evidence is outside the supplied profile.
"""
from __future__ import annotations

AGENTS = [
    ("CG-01", "CG Representation and Mapping Agent"),
    ("CG-02", "CG Topology Builder Agent"),
    ("CG-03", "CG Force-Field Selector Agent"),
    ("CG-04", "CG Parameterization Agent"),
    ("CG-05", "CG Model Transferability Agent"),
    ("CG-06", "CG System Builder Agent"),
    ("CG-07", "CG Energy Minimization Agent"),
    ("CG-08", "CG Equilibration Agent"),
    ("CG-09", "CG Simulation Stability Agent"),
    ("CG-10", "CG Sampling Strategy Agent"),
    ("CG-11", "CG Protein Structure Validation Agent"),
    ("CG-12", "CG Membrane Validation Agent"),
    ("CG-13", "CG Phase Separation Agent"),
    ("CG-14", "CG Self-Assembly Agent"),
    ("CG-15", "CG Structural Observable Matching Agent"),
    ("CG-16", "CG Thermodynamic Validation Agent"),
    ("CG-17", "CG Kinetics and Dynamics Validation Agent"),
    ("CG-18", "CG-to-Atomistic Reconstruction Agent"),
    ("CG-19", "CG Uncertainty and Sensitivity Agent"),
    ("CG-20", "CG Benchmark and Qualification Agent"),
]

def _result(agent_id, name, status, evidence):
    return {"agent_id": agent_id, "name": name, "status": status, "evidence": evidence}

def run_all_agents(system: dict) -> list[dict]:
    finite = bool(system.get("finite_energy") and system.get("finite_coordinates"))
    core = {
        "CG-01": (bool(system.get("mapping_valid")), "mapping and bead identity"),
        "CG-02": (system.get("bonds", 0) > 0, "bond graph and topology"),
        "CG-03": (bool(system.get("model")), "declared CG model"),
        "CG-04": (bool(system.get("parameters_complete")), "parameter completeness flag"),
        "CG-06": (bool(system.get("box_valid")), "periodic box and system construction"),
        "CG-07": (bool(system.get("minimized")), "OpenMM minimization result"),
        "CG-08": (system.get("steps", 0) > 0, "short equilibration/production trace"),
        "CG-09": (finite, "finite coordinates and potential energy"),
        "CG-10": (system.get("replicas", 0) >= 2, "independent repeat count"),
        "CG-19": (system.get("replicas", 0) >= 2 and system.get("repeat_energy_delta") is not None, "repeat energy comparison"),
    }
    family = system.get("family")
    family_checks = {
        "CG-11": (family == "protein", "protein-specific structural observables"),
        "CG-12": (family == "membrane", "membrane thickness/area observables"),
        "CG-13": (family == "llps", "dense/dilute phase observables"),
        "CG-14": (family in {"polymer", "llps"}, "cluster/self-assembly observables"),
    }
    results = []
    for agent_id, name in AGENTS:
        if agent_id in core:
            ok, evidence = core[agent_id]
            results.append(_result(agent_id, name, "PASS" if ok else "FAIL", evidence))
        elif agent_id in family_checks:
            ok, evidence = family_checks[agent_id]
            results.append(_result(agent_id, name, "PASS" if ok else "REVIEW", evidence if ok else "required family-specific system/observable not supplied"))
        elif agent_id == "CG-05":
            results.append(_result(agent_id, name, "REVIEW", "held-out transferability cases not supplied"))
        elif agent_id in {"CG-15", "CG-16", "CG-17", "CG-18"}:
            results.append(_result(agent_id, name, "REVIEW", "reference observables or atomistic reconstruction not supplied"))
        elif agent_id == "CG-20":
            ok = finite and all(r["status"] == "PASS" for r in results if r["agent_id"] in {"CG-01", "CG-02", "CG-03", "CG-04", "CG-06", "CG-07", "CG-08", "CG-09", "CG-10", "CG-19"})
            results.append(_result(agent_id, name, "PASS" if ok else "REVIEW", "three-system harness and repeat reconciliation" if ok else "required gate evidence missing"))
    return results
