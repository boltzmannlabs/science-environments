from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class Approach(str, Enum):
    FIXED = "fixed"
    AGENT = "agent-scientist"
    AGENT_SPECIALIST = "agent-scientist-plus-specialist"


class Split(str, Enum):
    DEVELOPMENT = "development"
    HELD_OUT = "held-out"


class CaseExpectation(str, Enum):
    VALID = "valid"
    RECOVERABLE = "recoverable"
    INVALID = "invalid"
    EXPECTED_FAILURE = "expected-failure"


class DecisionAction(str, Enum):
    RETRY = "retry"
    STOP = "stop"


class RunStatus(str, Enum):
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    BUDGET_EXHAUSTED = "budget-exhausted"
    PROTOCOL_VIOLATION = "protocol-violation"


@dataclass(frozen=True)
class BenchmarkBudget:
    max_tool_calls: int
    max_retries: int
    per_attempt_timeout_seconds: float
    max_case_wall_seconds: float

    def __post_init__(self) -> None:
        if self.max_tool_calls < 1:
            raise ValueError("max_tool_calls must be positive")
        if self.max_retries < 0 or self.max_retries >= self.max_tool_calls:
            raise ValueError("max_retries must be non-negative and less than max_tool_calls")
        if self.per_attempt_timeout_seconds <= 0 or self.max_case_wall_seconds <= 0:
            raise ValueError("timeouts must be positive")


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    split: Split
    expectation: CaseExpectation
    structure_file: Path
    structure_sha256: str
    charge: int
    multiplicity: int
    method: str
    basis: str
    requested_properties: tuple[str, ...]
    initial_settings: Mapping[str, Any]
    permitted_setting_values: Mapping[str, tuple[Any, ...]]
    reference_id: str | None
    notes: str = ""
    fault_rules: tuple[Mapping[str, Any], ...] = ()
    specialist_context: Mapping[str, Any] = field(default_factory=dict)

    def public_payload(self, *, include_specialist_context: bool = False) -> dict[str, Any]:
        """Context visible to a decision policy; never includes reference answers."""
        payload = {
            "case_id": self.case_id,
            "split": self.split.value,
            "expectation": self.expectation.value,
            "structure_file": str(self.structure_file),
            "structure_sha256": self.structure_sha256,
            "charge": self.charge,
            "multiplicity": self.multiplicity,
            "method": self.method,
            "basis": self.basis,
            "requested_properties": list(self.requested_properties),
            "initial_settings": dict(self.initial_settings),
            "permitted_setting_values": {
                key: list(values) for key, values in self.permitted_setting_values.items()
            },
            "notes": self.notes,
        }
        if include_specialist_context:
            payload["specialist_context"] = dict(self.specialist_context)
        return payload


@dataclass(frozen=True)
class Decision:
    action: DecisionAction
    settings: Mapping[str, Any] = field(default_factory=dict)
    reason: str = ""
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "settings": dict(self.settings),
            "reason": self.reason,
            "evidence": list(self.evidence),
        }


@dataclass(frozen=True)
class Attempt:
    sequence: int
    settings: Mapping[str, Any]
    status: str
    wall_seconds: float
    engine_seconds: float | None = None
    job_id: str | None = None
    energy_hartree: float | None = None
    converged: bool | None = None
    failure_class: str | None = None
    failure_message: str | None = None
    artifacts: tuple[Mapping[str, Any], ...] = ()
    synthetic_fault: bool = False

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["settings"] = dict(self.settings)
        result["artifacts"] = [dict(item) for item in self.artifacts]
        return result


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    kind: str
    payload: Mapping[str, Any]
    elapsed_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "kind": self.kind,
            "payload": dict(self.payload),
            "elapsed_seconds": self.elapsed_seconds,
        }


@dataclass(frozen=True)
class CaseRun:
    case_id: str
    split: Split
    expectation: CaseExpectation
    approach: Approach
    status: RunStatus
    method: str
    basis: str
    charge: int
    multiplicity: int
    attempts: tuple[Attempt, ...]
    decisions: tuple[Mapping[str, Any], ...]
    trace: tuple[TraceEvent, ...]
    total_wall_seconds: float
    protocol_violations: tuple[str, ...] = ()
    preflight_findings: tuple[str, ...] = ()

    @property
    def final_energy_hartree(self) -> float | None:
        for attempt in reversed(self.attempts):
            if attempt.status == "completed" and attempt.converged:
                return attempt.energy_hartree
        return None

    @property
    def tool_call_count(self) -> int:
        return len(self.attempts)

    @property
    def recovered(self) -> bool:
        return len(self.attempts) > 1 and self.status is RunStatus.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "split": self.split.value,
            "expectation": self.expectation.value,
            "approach": self.approach.value,
            "status": self.status.value,
            "method": self.method,
            "basis": self.basis,
            "charge": self.charge,
            "multiplicity": self.multiplicity,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
            "decisions": [dict(item) for item in self.decisions],
            "trace": [event.to_dict() for event in self.trace],
            "total_wall_seconds": self.total_wall_seconds,
            "tool_call_count": self.tool_call_count,
            "recovered": self.recovered,
            "final_energy_hartree": self.final_energy_hartree,
            "protocol_violations": list(self.protocol_violations),
            "preflight_findings": list(self.preflight_findings),
        }
