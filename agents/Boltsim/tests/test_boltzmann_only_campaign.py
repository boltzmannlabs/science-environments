from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_primary_policy_excludes_external_engines() -> None:
    policy = load("campaign/manifests/boltzmann_only_validation_policy_v1.json")
    assert policy["calculation_backend"] == "Boltzmann SPE module"
    assert policy["external_engines_in_primary_gate"] is False
    assert policy["external_validation"]["included_in_agent_status"] is False


def test_frozen_water_reference_matches_primary_policy() -> None:
    policy = load("campaign/manifests/boltzmann_only_validation_policy_v1.json")
    baseline = load("campaign/manifests/common_water_baseline.json")
    regression = policy["common_water_regression"]
    assert baseline["reference_energy_hartree"] == regression["reference_energy_hartree"]
    assert baseline["tolerance_hartree"] == regression["absolute_tolerance_hartree"]
    assert regression["accuracy_claim"] == "none"


def test_frozen_historical_v1_report_covers_its_20_agents_and_six_gates() -> None:
    report = load("reports/boltzmann_only_validation/campaign_report.json")
    assert report["external_engines_in_primary_gate"] is False
    assert all(report["primary_gates"].values())
    assert len(report["primary_gates"]) == 6
    assert [item["environment_id"] for item in report["agents"]] == [
        f"{number:02d}" for number in range(1, 21)
    ]
    assert report["summary"]["status_counts"] == {"pass": 16, "review": 4}


def test_boltzmann_water_regression_runs_are_within_frozen_tolerance() -> None:
    report = load("reports/boltzmann_only_validation/campaign_report.json")
    regression = report["common_water_regression"]
    runs = regression["historical_runs"] + regression["fresh_runs"]
    assert len(regression["historical_runs"]) == 6
    assert len(regression["fresh_runs"]) == 3
    assert all(item["passed"] for item in runs)
    assert all(
        item["absolute_difference_hartree"] <= regression["tolerance_hartree"]
        for item in runs
    )


def test_cp2k_report_is_explicitly_optional() -> None:
    external = load("reports/external_validation/cp2k_water/external_validation_report.json")
    assert external["classification"] == "optional_external_validation"
    assert external["included_in_primary_agent_gate"] is False
    assert external["included_in_agent_status"] is False
