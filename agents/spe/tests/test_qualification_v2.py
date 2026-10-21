from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v1_baseline_manifest_is_still_exact() -> None:
    manifest = load("campaign/manifests/qualification_v1_baseline_manifest.json")
    assert all(sha256(ROOT / item["path"]) == item["sha256"] for item in manifest["files"])


def test_v2_report_assesses_all_agents_without_external_engine_gate() -> None:
    report = load("reports/qualification_v2/campaign_report.json")
    assert report["external_engines_in_primary_gate"] is False
    assert all(report["regression_checks"].values())
    assert report["status"] == "pass"
    assert report["summary"]["status_counts"] == {"pass": 18}
    assert [item["environment_id"] for item in report["agents"]] == [
        f"{number:02d}" for number in range(1, 21) if number not in {13, 16}
    ]


def test_agent13_invalid_geometry_cannot_accept_energy() -> None:
    report = load("reports/qualification_v2/agent_13_geometry_audit.json")
    assert report["status"] == "rejected_invalid_geometry"
    assert report["clash_count"] > 0
    assert report["energy_acceptance"] == "rejected"


def test_removed_agent13_evidence_is_archived_and_not_in_active_roster() -> None:
    report = load("reports/qualification_v2/agent_13_root_cause.json")
    assert report["root_cause"] == {
        "classification": "synthetic_mock_source_geometry",
        "coordinate_corruption": True,
        "coordinate_unit_error": False,
        "duplicate_atoms": False,
        "atom_mapping_error": True,
        "extraction_artifact": False,
        "genuine_crystallographic_overlap": False,
        "explanation": report["root_cause"]["explanation"],
    }
    assert report["submitted_selection"]["extraction_is_coordinate_preserving"] is True
    assert report["submitted_selection"]["duplicate_coordinate_set_count"] == 0
    assert report["severe_clash_count"] == 9
    assert report["deposited_structure_control"]["contact_count"] == 5
    assert report["deposited_structure_control"]["selected_active_site_heavy_atom_clash_count"] == 0

    runner_path = ROOT / "scripts/run_bounded_agent13.py"
    spec = importlib.util.spec_from_file_location("agent13_bounded_runner", runner_path)
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    preflight = runner.geometry_preflight(runner.curated_atoms())
    assert preflight["passed"] is False
    assert preflight["clash_count"] == 9
    roster = load("campaign/manifests/active_18_agent_roster.json")
    assert "13" not in roster["active_environment_ids"]


def test_removed_agent16_evidence_is_archived_and_not_in_active_roster() -> None:
    packet = load("reports/qualification_v2/agent_16/approval_packet.json")
    assert packet["status"] == "awaiting_qualified_human_approval"
    assert packet["production_spe_authorized"] is False
    assert packet["calculation_status"] == "not_started"
    assert packet["exact_fragment"]["atom_count"] == 106
    comparison = packet["exact_fragment"]["reconstruction_comparison"]
    assert comparison["atom_order_and_elements_match"] is True
    assert comparison["heavy_atom_coordinate_mismatch_count"] == 0
    assert comparison["hydrogen_coordinate_mismatch_count"] == 31
    assert not all(packet["approval_checks"].values())
    roster = load("campaign/manifests/active_18_agent_roster.json")
    assert "16" not in roster["active_environment_ids"]


def test_agent15_positive_qmmm_path_is_complete() -> None:
    report = load("reports/qualification_v2/agent_15_qualification.json")
    assert report["status"] == "pass"
    assert all(report["checks"].values())
    assert report["system"]["embedding"] == "electronic"
    assert report["system"]["forcefield"] == "amber14"
    assert report["execution"]["scf_converged"] is True


def test_agent19_uses_boltzmann_references_and_scoped_mlip_comparison() -> None:
    report = load("reports/qualification_v2/agent_19_qualification.json")
    assert report["status"] == "pass"
    assert report["primary_backend_evidence"]["backend"] == "Boltzmann SPE module"
    assert report["primary_backend_evidence"]["fixed_geometry_runs"] == 7
    assert all(report["checks"].values())


def test_specialist_value_report_avoids_unmeasured_productivity_claims() -> None:
    report = load("reports/qualification_v2/specialist_value_report.json")
    assert report["summary"] == {
        "demonstrated": 18,
        "partial": 0,
        "not_demonstrated": 0,
    }
    assert report["campaign_level_observations"]["manual_intervention_time_measured"] is False


def test_fresh_v2_artifact_integrity() -> None:
    report = load("reports/qualification_v2/artifact_integrity.json")
    assert report["status"] == "pass"
    assert report["artifacts_checked"] == 128
    assert report["mismatches"] == []
