import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_role_audit_counts_documented_roles_without_overclaiming():
    data = json.loads((ROOT / "results/operational_role_audit.json").read_text())
    assert data["contracted_specialists"] == 15
    assert data["contracted_problem_solving"] == 10
    assert sum(data["counts"].values()) == 25
    assert data["claim"] == "25 documented roles; not 25 autonomous AI agents"

def test_orchestrator_selects_neutral_edge_without_charge_agent():
    data = json.loads((ROOT / "results/paper_orchestration.json").read_text())
    assert data["selected_edge"] == "17->1h1q"
    assert data["net_charge_change"] is False
    assert "FEP-AG05" not in data["selected_roles"]
    assert data["status"] == "REVIEW"

def test_architecture_benchmark_has_three_experiments():
    data = json.loads((ROOT / "results/agent_architecture_benchmark.json").read_text())
    assert set(data["experiments"]) == {"A_general_agent", "B_specialist_assisted", "C_orchestrated_with_problem_solving"}
    assert data["status"] == "REVIEW"
