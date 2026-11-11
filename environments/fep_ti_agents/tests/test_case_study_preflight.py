import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_case_study_preflight_preserves_catalogued_status():
    data = json.loads((ROOT / "results/case_study_preflight.json").read_text())
    by_id = {item["case_id"]: item for item in data["cases"]}
    assert by_id["CDK2_RBFE_001"]["execution"] == "DELEGATED_TO_CANONICAL_TASK"
    assert by_id["PTP1B_RBFE_001"]["execution"] == "DELEGATED_TO_CANONICAL_TASK"
    assert by_id["FORCE_FIELD_SENSITIVITY_001"]["status"] == "CATALOGUED"
    assert by_id["SECOND_RBFE_001"]["status"] == "CATALOGUED"
