import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_case_study_catalogue_has_two_validated_and_two_catalogued_cases():
    data = json.loads((ROOT / "case_studies/catalogue.json").read_text())
    assert len(data["case_studies"]) == 4
    statuses = [case["status"] for case in data["case_studies"]]
    assert statuses.count("SETUP_VALIDATED") == 2
    assert statuses.count("CATALOGUED") == 2
    assert all((ROOT / "case_studies" / case["id"] / "TASK.md").exists()
               for case in data["case_studies"])
