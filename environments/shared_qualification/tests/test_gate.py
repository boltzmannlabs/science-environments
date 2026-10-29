from environments.shared_qualification import qualify


def test_adapter_failure_is_fail():
    result = qualify({"adapter_status": "ERROR"})
    assert result["status"] == "FAIL"


def test_missing_science_is_review():
    result = qualify(
        {"adapter_status": "PASS", "independent_evaluator": False},
        required_evidence=["trajectory", "reference"],
    )
    assert result["status"] == "REVIEW"
    assert "trajectory" in result["missing_evidence"]
    assert "independent_evaluator" in result["missing_evidence"]


def test_failed_check_is_fail():
    result = qualify(
        {"adapter_status": "PASS", "independent_evaluator": True, "finite_energy": False},
        required_checks=["finite_energy"],
    )
    assert result["status"] == "FAIL"


def test_complete_evidence_is_pass():
    result = qualify(
        {
            "adapter_status": "PASS",
            "independent_evaluator": True,
            "trajectory": "run.dcd",
            "reference": "reference.json",
            "finite_energy": True,
        },
        required_evidence=["trajectory", "reference"],
        required_checks=["finite_energy"],
    )
    assert result["status"] == "PASS"
