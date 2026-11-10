#!/usr/bin/env python3
"""Deterministic specialist-selection policy for FEP-PAPER-001.

This is an auditable orchestration harness, not a claim of LLM autonomy.  It
selects only roles justified by the task evidence and records missing gates.
"""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent / "fep_paper_reproduction/tasks/fep_paper_001"
OUT = ROOT / "results/paper_orchestration.json"

def select() -> dict:
    tr = json.loads((PAPER / "inputs/transformation.json").read_text())
    readiness = json.loads((PAPER / "execution/endpoint_readiness.json").read_text())
    charge_change = tr.get("net_charge_a") != tr.get("net_charge_b")
    selected = ["FEP-AG01", "FEP-AG02", "FEP-AG03", "FEP-AG04", "FEP-AG12", "FEP-AG14", "FEP-AG15", "FEP-PS01", "FEP-PS02", "FEP-PS03", "FEP-PS10"]
    if charge_change: selected += ["FEP-AG05", "FEP-PS08"]
    if readiness["checks"].get("lambda_trajectories_present"):
        selected += ["FEP-AG07", "FEP-AG08", "FEP-AG11", "FEP-PS04", "FEP-PS05", "FEP-PS07"]
    else:
        selected += ["FEP-AG07", "FEP-AG08", "FEP-AG11", "FEP-PS04", "FEP-PS05", "FEP-PS07"]
    return {"task": "FEP-PAPER-001", "selected_edge": tr["direction"], "net_charge_change": charge_change, "selected_roles": selected, "selection_policy": "mapping/feasibility/parameter/schedule/legs/audit always; charge only for charge-changing edges; sampling roles selected but return REVIEW when trajectories are absent", "missing_gates": readiness.get("missing", []), "status": "REVIEW" if readiness.get("status") != "PASS" else "PASS", "autonomy_scope": "deterministic policy harness; no LLM decision or tool-call claim"}

def main() -> dict:
    result = select(); OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2)); return result
if __name__ == "__main__": main()
