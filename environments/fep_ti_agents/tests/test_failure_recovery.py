import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from diagnose_fep_failure import diagnose

CONFIG = ROOT / "tasks/inputs/fep_failure_recovery_001/failure_cases.json"


def test_failure_cases_are_classified_and_safe_actions_are_bounded(tmp_path):
    result = diagnose(CONFIG, tmp_path)
    assert result["status"] == "REVIEW"  # a mixed batch contains deliberate unsafe failures
    by_id = {case["case_id"]: case for case in result["cases"]}
    assert by_id["FEP-T06-recoverable-lincs"]["status"] == "PASS"
    assert by_id["FEP-T06-recoverable-lincs"]["failure_cause"] == "constraint_failure"
    assert by_id["FEP-T06-recoverable-lincs"]["allowed_action"] == "restart_from_last_valid_checkpoint"
    assert by_id["FEP-T06-recoverable-lincs"]["retry_limit"] == 1
    assert by_id["FEP-T06-nan-no-checkpoint"]["status"] == "FAIL"
    assert by_id["FEP-T06-nan-no-checkpoint"]["allowed_action"] == "stop_no_safe_restart"


def test_protocol_mismatch_never_restarts(tmp_path):
    result = diagnose(CONFIG, tmp_path)
    case = next(x for x in result["cases"] if x["case_id"] == "FEP-T07-incompatible-checkpoint")
    assert case["failure_cause"] == "checkpoint_incompatible"
    assert case["status"] == "FAIL"
    assert case["allowed_action"] == "stop_no_safe_restart"
    assert case["evidence"]["checkpoint_protocol_matches"] is False


def test_input_hash_and_recovery_history_are_written(tmp_path):
    result = diagnose(CONFIG, tmp_path)
    assert len(result["input_sha256"]) == 64
    assert (tmp_path / "failure_report.json").exists()
    assert (tmp_path / "recovery_plan.json").exists()
    assert len((tmp_path / "recovery_history.jsonl").read_text().splitlines()) == 4
