from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Mapping

from .models import SPEEnvironment


class EvaluationDecision(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NEEDS_REVIEW = "needs-review"
    NOT_EVALUATED = "not-evaluated"


@dataclass(frozen=True)
class EvaluationReport:
    environment_id: str
    decision: EvaluationDecision
    passed: tuple[str, ...] = field(default_factory=tuple)
    failed: tuple[str, ...] = field(default_factory=tuple)
    missing: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["decision"] = self.decision.value
        return result


class IndependentEvaluator:
    """Evaluate explicit evidence separately from tool execution.

    Evidence keys must exactly match the selected environment's acceptance criteria.
    Values are true, false, or null/omitted when evidence is unavailable. This interface
    intentionally does not infer scientific success from a completed tool call.
    """

    def evaluate(
        self,
        environment: SPEEnvironment,
        evidence: Mapping[str, bool | None],
        *,
        execution_completed: bool,
    ) -> EvaluationReport:
        if not execution_completed and not evidence:
            return EvaluationReport(
                environment_id=environment.id,
                decision=EvaluationDecision.NOT_EVALUATED,
                missing=environment.acceptance_criteria,
                notes=("execution did not complete and no acceptance evidence was supplied",),
            )

        passed: list[str] = []
        failed: list[str] = []
        missing: list[str] = []
        for criterion in environment.acceptance_criteria:
            value = evidence.get(criterion)
            if value is True:
                passed.append(criterion)
            elif value is False:
                failed.append(criterion)
            else:
                missing.append(criterion)

        unknown = sorted(set(evidence) - set(environment.acceptance_criteria))
        notes = tuple(f"ignored unknown evidence key: {key}" for key in unknown)
        if failed:
            decision = EvaluationDecision.FAIL
        elif missing or not execution_completed:
            decision = EvaluationDecision.NEEDS_REVIEW
        else:
            decision = EvaluationDecision.PASS
        return EvaluationReport(
            environment_id=environment.id,
            decision=decision,
            passed=tuple(passed),
            failed=tuple(failed),
            missing=tuple(missing),
            notes=notes,
        )
