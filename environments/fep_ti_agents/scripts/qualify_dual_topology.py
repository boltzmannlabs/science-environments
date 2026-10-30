"""Independent, non-agent qualification checks for the dual-topology result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def qualify(source: Path, output: Path) -> None:
    data = json.loads(source.read_text())
    checks = data["checks"]
    required = ["dual_topology", "complex_leg_finite", "solvent_leg_finite", "lambda_coverage", "independent_replicas"]
    convergence_checks = {
        "complex_overlap_proxy_present": data["complex"].get("adjacent_overlap_proxy_min", 0.0) > 0.0,
        "solvent_overlap_proxy_present": data["solvent"].get("adjacent_overlap_proxy_min", 0.0) > 0.0,
        "complex_replica_uncertainty_present": "replica_stderr_kj_mol" in data["complex"],
        "solvent_replica_uncertainty_present": "replica_stderr_kj_mol" in data["solvent"],
    }
    passed = all(checks.get(key) is True for key in required) and all(convergence_checks.values())
    decision = "PASS" if passed else "FAIL"
    report = {
        "task_id": data["task_id"],
        "qualification": decision,
        "independent_checks": {key: checks.get(key, False) for key in required},
        "sampling_checks": convergence_checks,
        "complex_estimate_kj_mol": data["complex"]["estimate_kj_mol"],
        "solvent_estimate_kj_mol": data["solvent"]["estimate_kj_mol"],
        "relative_binding_estimate_kj_mol": data["relative_binding_estimate_kj_mol"],
        "evidence_scope": data["scope"],
        "limitations": data["limitations"],
        "interpretation": "PASS means the bounded dual-topology fixture executed with finite complex and solvent legs, complete lambda coverage, and independent replicas; it is not a claim of converged SAMPL6 production FEP.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/dual_topology_qualification_001.json"))
    args = parser.parse_args()
    qualify(args.source, args.output)
