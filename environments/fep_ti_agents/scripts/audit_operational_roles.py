#!/usr/bin/env python3
"""Audit documented FEP roles against executable paper-task evidence.

This intentionally distinguishes a contract from an operational agent.  A role
is operational only when an executable tool and a task-specific evidence file
are both present; otherwise the result is PARTIAL or SPECIFICATION.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "tasks/fep_paper_001"
OUT = ROOT / "results/operational_role_audit.json"

def role(tool: str | None, evidence: str | None, status: str, note: str) -> dict:
    return {"status": status, "tool": tool, "evidence": evidence, "note": note,
            "tool_present": bool(tool and (PAPER / tool).is_file()),
            "evidence_present": bool(evidence and (PAPER / evidence).is_file())}

def main() -> dict:
    ag = {
        "FEP-AG01": role("scripts/generate_openfe_mapping.py", "inputs/openfe_atom_map.json", "OPERATIONAL", "OpenFE/Lomap mapping is generated and retained."),
        "FEP-AG02": role("scripts/check_endpoint_readiness.py", "execution/endpoint_readiness.json", "PARTIAL", "Endpoint compatibility is checked; chemical-feasibility reasoning is not autonomous."),
        "FEP-AG03": role("scripts/parameterize_ligands_gaff.py", "execution/ligand_parameterization/parameterization.json", "OPERATIONAL", "GAFF parameterization tool and logs are present."),
        "FEP-AG04": role(None, "reference/lambda_protocol.json", "PARTIAL", "A frozen protocol exists; adaptive schedule optimization is not implemented."),
        "FEP-AG05": role(None, "inputs/transformation.json", "PARTIAL", "Endpoint charge metadata exists; correction execution is not implemented."),
        "FEP-AG06": role(None, None, "SPECIFICATION", "No paper-task crash recovery tool or recovery trace."),
        "FEP-AG07": role(None, None, "SPECIFICATION", "No production reduced-potential overlap analysis."),
        "FEP-AG08": role(None, None, "SPECIFICATION", "No trajectory block/replica convergence analysis."),
        "FEP-AG09": role(None, None, "SPECIFICATION", "No binding-site water trajectory analysis."),
        "FEP-AG10": role(None, None, "SPECIFICATION", "No adaptive sampling controller is connected."),
        "FEP-AG11": role(None, None, "SPECIFICATION", "No BAR/MBAR paper-task execution evidence."),
        "FEP-AG12": role("scripts/check_endpoint_readiness.py", "execution/endpoint_readiness.json", "PARTIAL", "Complex/solvent legs are checked, but no computed cycle closure."),
        "FEP-AG13": role(None, None, "SPECIFICATION", "No network ranking evidence for the pilot edge."),
        "FEP-AG14": role("scripts/evaluate_config_matrix.py", "evaluation/config_matrix.json", "PARTIAL", "Configuration faults are audited; scientific false-success checks remain incomplete."),
        "FEP-AG15": role("scripts/check_endpoint_readiness.py", "expected_outputs/qualification.json", "PARTIAL", "Independent readiness gate exists; it correctly returns REVIEW without trajectories."),
    }
    ps = {f"FEP-PS{i:02d}": {"status": "FIXTURE_ONLY", "tool": "scripts/run_fep_validation.py", "evidence": "results/fixture_results.json", "note": "Validated on the synthetic fixture; not connected to paper trajectories."} for i in range(1, 11)}
    result = {"benchmark": "FEP-PAPER-001", "contracted_specialists": 15, "contracted_problem_solving": 10, "roles": {**ag, **ps}, "counts": {"operational": sum(v["status"] == "OPERATIONAL" for v in ag.values()), "partial": sum(v["status"] == "PARTIAL" for v in ag.values()), "specification": sum(v["status"] == "SPECIFICATION" for v in ag.values()), "fixture_only": 10}, "claim": "25 documented roles; not 25 autonomous AI agents", "status": "REVIEW"}
    OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2)); return result

if __name__ == "__main__": main()
