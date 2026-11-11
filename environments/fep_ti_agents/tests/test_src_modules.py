import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from src.agents import select_setup_roles
from src.assessment import summarize_configuration_matrix
from src.structure_preparation import endpoint_status

def test_shared_agent_layer_matches_recorded_setup_roles():
    assert select_setup_roles() == ["FEP-AG01", "FEP-AG02", "FEP-AG03", "FEP-AG05", "FEP-AG15"]

def test_shared_assessment_layer_reads_paper_matrix():
    matrix = json.loads((ROOT / "tasks/fep_paper_002/execution/config_comparison.json").read_text())
    summary = summarize_configuration_matrix(matrix)
    assert summary["agent"] == "SETUP_PASS"
    assert summary["alternative"] == "REVIEW"
    assert summary["perturbed"] == "FAIL"

def test_shared_preparation_layer_validates_both_endpoints():
    directory = ROOT / "tasks/fep_paper_002/execution/parameterization"
    assert endpoint_status(directory, "23477")["status"] == "PASS"
    assert endpoint_status(directory, "23482")["status"] == "PASS"
