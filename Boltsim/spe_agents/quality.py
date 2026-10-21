"""Independent audit rules for SPE result artifacts (environment 20)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class AuditDecision(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    FLAG = "flag"


@dataclass(frozen=True)
class AuditFinding:
    code: str
    message: str


@dataclass(frozen=True)
class AuditReport:
    decision: AuditDecision
    findings: tuple[AuditFinding, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision.value,
            "findings": [
                {"code": finding.code, "message": finding.message}
                for finding in self.findings
            ],
        }


class SPEArtifactAuditor:
    """Audit explicit result evidence without executing quantum chemistry."""

    _SETTING_FIELDS = ("method", "basis_set", "charge", "multiplicity")

    def audit(self, artifact: Mapping[str, Any]) -> AuditReport:
        findings: list[AuditFinding] = []
        submitted = artifact.get("input")
        result = artifact.get("result")
        provenance = artifact.get("provenance")
        if not isinstance(submitted, Mapping):
            findings.append(AuditFinding("missing_input", "submitted input is missing"))
        if not isinstance(result, Mapping):
            findings.append(AuditFinding("missing_result", "structured result is missing"))
        if not isinstance(provenance, Mapping):
            findings.append(AuditFinding("missing_provenance", "provenance is missing"))
        if findings:
            return AuditReport(AuditDecision.FLAG, tuple(findings))

        actual = provenance.get("actual_input")
        if not isinstance(actual, Mapping):
            findings.append(
                AuditFinding("missing_actual_input", "provenance does not preserve actual engine input")
            )
        else:
            for field in self._SETTING_FIELDS:
                if submitted.get(field) != actual.get(field):
                    findings.append(
                        AuditFinding(
                            "settings_conflict",
                            f"recorded {field}={submitted.get(field)!r} conflicts with "
                            f"actual input {actual.get(field)!r}",
                        )
                    )

        engine_version = provenance.get("engine_version")
        if not isinstance(engine_version, str) or not engine_version.strip():
            findings.append(AuditFinding("missing_engine_version", "engine version is missing"))

        if findings:
            return AuditReport(AuditDecision.FLAG, tuple(findings))

        completed = result.get("status") == "completed"
        converged = result.get("converged") is True
        if not completed or not converged:
            if not completed:
                findings.append(AuditFinding("execution_incomplete", "execution did not complete"))
            if not converged:
                findings.append(AuditFinding("not_converged", "SCF convergence is not demonstrated"))
            return AuditReport(AuditDecision.REJECT, tuple(findings))

        energy = result.get("total_energy_hartree")
        if isinstance(energy, bool) or not isinstance(energy, (int, float)) or not math.isfinite(energy):
            findings.append(
                AuditFinding("invalid_energy", "one finite total energy in Hartree is required")
            )
            return AuditReport(AuditDecision.REJECT, tuple(findings))

        return AuditReport(AuditDecision.ACCEPT, ())
