from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents import AuditDecision, SPEArtifactAuditor  # noqa: E402


def artifact(*, status: str = "completed", converged: bool = True) -> dict:
    settings = {"method": "B3LYP", "basis_set": "6-31G*", "charge": 0, "multiplicity": 1}
    return {
        "input": dict(settings),
        "result": {
            "status": status,
            "converged": converged,
            "total_energy_hartree": -76.0 if converged else None,
        },
        "provenance": {"engine_version": "fixture-1", "actual_input": dict(settings)},
    }


class SPEArtifactAuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.auditor = SPEArtifactAuditor()

    def test_accepts_completed_converged_consistent_artifact(self) -> None:
        self.assertEqual(self.auditor.audit(artifact()).decision, AuditDecision.ACCEPT)

    def test_rejects_non_converged_artifact(self) -> None:
        report = self.auditor.audit(artifact(status="failed", converged=False))
        self.assertEqual(report.decision, AuditDecision.REJECT)
        self.assertIn("not_converged", {finding.code for finding in report.findings})

    def test_flags_recorded_basis_conflict(self) -> None:
        value = artifact()
        value["provenance"]["actual_input"]["basis_set"] = "def2-SVP"
        report = self.auditor.audit(value)
        self.assertEqual(report.decision, AuditDecision.FLAG)
        self.assertIn("settings_conflict", {finding.code for finding in report.findings})


if __name__ == "__main__":
    unittest.main()
