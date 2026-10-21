from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .models import Approach, CaseExpectation, CaseRun, RunStatus, Split


class EvaluationError(ValueError):
    pass


@dataclass(frozen=True)
class ReferenceRecord:
    reference_id: str
    expected_outcome: CaseExpectation
    energy_hartree: float | None
    tolerance_hartree: float | None
    method: str | None
    basis: str | None
    failure_class: str | None
    expected_initial_failure_class: str | None
    expected_preflight_substring: str | None


class ReferenceStore:
    """Evaluator-owned references. Run policies never receive this object."""

    def __init__(self, path: Path | str):
        self.path = Path(path).resolve()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or not isinstance(raw.get("references"), list):
            raise EvaluationError("reference store must contain a references array")
        records: dict[str, ReferenceRecord] = {}
        for item in raw["references"]:
            if not isinstance(item, dict):
                raise EvaluationError("reference entries must be objects")
            reference_id = str(item["reference_id"])
            if reference_id in records:
                raise EvaluationError(f"duplicate reference ID: {reference_id}")
            expectation = CaseExpectation(str(item["expected_outcome"]))
            energy = item.get("energy_hartree")
            tolerance = item.get("tolerance_hartree")
            records[reference_id] = ReferenceRecord(
                reference_id=reference_id,
                expected_outcome=expectation,
                energy_hartree=(float(energy) if energy is not None else None),
                tolerance_hartree=(float(tolerance) if tolerance is not None else None),
                method=(str(item["method"]) if item.get("method") else None),
                basis=(str(item["basis"]) if item.get("basis") else None),
                failure_class=(str(item["failure_class"]) if item.get("failure_class") else None),
                expected_initial_failure_class=(
                    str(item["expected_initial_failure_class"])
                    if item.get("expected_initial_failure_class")
                    else None
                ),
                expected_preflight_substring=(
                    str(item["expected_preflight_substring"])
                    if item.get("expected_preflight_substring")
                    else None
                ),
            )
        self.records = records
        self.metadata = {key: value for key, value in raw.items() if key != "references"}

    def get(self, reference_id: str) -> ReferenceRecord:
        try:
            return self.records[reference_id]
        except KeyError as exc:
            raise EvaluationError(f"unknown reference ID: {reference_id}") from exc


@dataclass(frozen=True)
class CaseEvaluation:
    case_id: str
    split: Split
    approach: Approach
    expectation: CaseExpectation
    passed: bool
    valid_completion: bool
    input_classification_correct: bool
    reference_error_hartree: float | None
    recovery_success: bool | None
    findings: tuple[str, ...]
    failure_class: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "split": self.split.value,
            "approach": self.approach.value,
            "expectation": self.expectation.value,
            "passed": self.passed,
            "valid_completion": self.valid_completion,
            "input_classification_correct": self.input_classification_correct,
            "reference_error_hartree": self.reference_error_hartree,
            "recovery_success": self.recovery_success,
            "findings": list(self.findings),
            "failure_class": self.failure_class,
        }


@dataclass(frozen=True)
class EvaluationBundle:
    cases: tuple[CaseEvaluation, ...]
    metrics: Mapping[str, Mapping[str, Any]]
    reference_scope: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reference_scope": self.reference_scope,
            "cases": [case.to_dict() for case in self.cases],
            "metrics": {key: dict(value) for key, value in self.metrics.items()},
        }


class BenchmarkEvaluator:
    def __init__(self, references: ReferenceStore):
        self.references = references

    def evaluate(self, runs: Iterable[CaseRun], case_reference_ids: Mapping[str, str]) -> EvaluationBundle:
        evaluations: list[CaseEvaluation] = []
        run_list = list(runs)
        for run in run_list:
            reference_id = case_reference_ids.get(run.case_id)
            if not reference_id:
                raise EvaluationError(f"case {run.case_id} has no evaluator reference mapping")
            reference = self.references.get(reference_id)
            evaluations.append(self._evaluate_case(run, reference))
        metrics = {
            approach.value: self._metrics(
                [run for run in run_list if run.approach is approach],
                [item for item in evaluations if item.approach is approach],
            )
            for approach in Approach
            if any(run.approach is approach for run in run_list)
        }
        return EvaluationBundle(
            tuple(evaluations),
            metrics,
            str(self.references.metadata.get("reference_scope", "unspecified")),
        )

    @staticmethod
    def _evaluate_case(run: CaseRun, reference: ReferenceRecord) -> CaseEvaluation:
        findings: list[str] = []
        if run.expectation is not reference.expected_outcome:
            findings.append("manifest expectation conflicts with evaluator reference")
        invalid = reference.expected_outcome is CaseExpectation.INVALID
        if invalid:
            finding_match = (
                reference.expected_preflight_substring is None
                or any(
                    reference.expected_preflight_substring in finding
                    for finding in run.preflight_findings
                )
            )
            input_correct = (
                run.status is RunStatus.REJECTED
                and run.tool_call_count == 0
                and finding_match
            )
            if not input_correct:
                findings.append(
                    "invalid input was not rejected with the expected finding before backend submission"
                )
            return CaseEvaluation(
                run.case_id,
                run.split,
                run.approach,
                run.expectation,
                input_correct and not run.protocol_violations,
                False,
                input_correct,
                None,
                None,
                tuple(findings),
                reference.failure_class,
            )

        if reference.expected_outcome is CaseExpectation.EXPECTED_FAILURE:
            last_failure = run.attempts[-1].failure_class if run.attempts else None
            handled = (
                run.status is RunStatus.FAILED
                and run.final_energy_hartree is None
                and bool(run.attempts)
                and not run.protocol_violations
                and (
                    reference.failure_class is None
                    or last_failure == reference.failure_class
                )
            )
            if not handled:
                findings.append(
                    f"expected safe terminal failure {reference.failure_class!r}, got status={run.status.value} class={last_failure!r}"
                )
            return CaseEvaluation(
                run.case_id,
                run.split,
                run.approach,
                run.expectation,
                handled and not findings,
                False,
                True,
                None,
                None,
                tuple(findings),
                reference.failure_class,
            )

        input_correct = run.status is not RunStatus.REJECTED
        valid_completion = (
            run.status is RunStatus.COMPLETED
            and run.final_energy_hartree is not None
            and math.isfinite(run.final_energy_hartree)
            and not run.protocol_violations
        )
        error: float | None = None
        reference_pass = False
        if reference.expected_initial_failure_class:
            initial = run.attempts[0].failure_class if run.attempts else None
            if initial != reference.expected_initial_failure_class:
                findings.append(
                    f"expected initial failure {reference.expected_initial_failure_class!r}, got {initial!r}"
                )
        if reference.method != run.method or reference.basis != run.basis:
            findings.append("method or basis conflicts with evaluator reference")
        elif valid_completion and reference.energy_hartree is not None and reference.tolerance_hartree is not None:
            error = abs(run.final_energy_hartree - reference.energy_hartree)
            reference_pass = error <= reference.tolerance_hartree
            if not reference_pass:
                findings.append(
                    f"reference error {error:.12g} Ha exceeds tolerance {reference.tolerance_hartree:.12g} Ha"
                )
        else:
            findings.append("valid finite energy or numerical reference is unavailable")
        if not valid_completion:
            findings.append(f"run did not produce a valid completion: {run.status.value}")
        recovery = (
            valid_completion if reference.expected_outcome is CaseExpectation.RECOVERABLE else None
        )
        return CaseEvaluation(
            run.case_id,
            run.split,
            run.approach,
            run.expectation,
            valid_completion and reference_pass and input_correct and not findings,
            valid_completion,
            input_correct,
            error,
            recovery,
            tuple(findings),
            reference.failure_class or reference.expected_initial_failure_class,
        )

    @staticmethod
    def _metrics(runs: list[CaseRun], evaluations: list[CaseEvaluation]) -> dict[str, Any]:
        valid_evaluations = [
            item
            for item in evaluations
            if item.expectation in {CaseExpectation.VALID, CaseExpectation.RECOVERABLE}
        ]
        invalid_evaluations = [
            item for item in evaluations if item.expectation is CaseExpectation.INVALID
        ]
        terminal_failures = [
            item for item in evaluations if item.expectation is CaseExpectation.EXPECTED_FAILURE
        ]
        errors = [
            item.reference_error_hartree
            for item in evaluations
            if item.reference_error_hartree is not None
        ]
        recoverable = [item for item in evaluations if item.recovery_success is not None]
        held_out = [item for item in evaluations if item.split is Split.HELD_OUT]
        successful = sum(item.valid_completion for item in valid_evaluations)
        total_wall = sum(run.total_wall_seconds for run in runs)
        decisions = sum(len(run.decisions) for run in runs)
        usage_records = [
            usage
            for run in runs
            for decision in run.decisions
            if isinstance(decision, Mapping)
            for response in [decision.get("response")]
            if isinstance(response, Mapping)
            for usage in [response.get("agent_scientist_usage")]
            if isinstance(usage, Mapping)
        ]
        agent_api_calls = sum(
            _usage_number(usage, "api_calls", include_auxiliary=True)
            for usage in usage_records
        )
        agent_tokens = sum(
            _usage_number(usage, "total_tokens", include_auxiliary=True)
            for usage in usage_records
        )
        agent_cost = sum(
            _usage_number(usage, "estimated_cost_usd", include_auxiliary=True)
            for usage in usage_records
        )
        recovered = sum(run.recovered for run in runs)
        decision_quality_denominator = sum(
            1 for run in runs if run.decisions and run.expectation is CaseExpectation.RECOVERABLE
        )
        return {
            "case_count": len(evaluations),
            "valid_completion_rate": _ratio(successful, len(valid_evaluations)),
            "median_reference_error_hartree": statistics.median(errors) if errors else None,
            "mean_reference_error_hartree": statistics.fmean(errors) if errors else None,
            "max_reference_error_hartree": max(errors) if errors else None,
            "reference_error_count": len(errors),
            "input_validation_accuracy": _ratio(
                sum(item.input_classification_correct for item in evaluations), len(evaluations)
            ),
            "invalid_case_count": len(invalid_evaluations),
            "safe_failure_handling_rate": _ratio(
                sum(item.passed for item in terminal_failures), len(terminal_failures)
            ),
            "recovery_success_rate": _ratio(
                sum(bool(item.recovery_success) for item in recoverable), len(recoverable)
            ),
            "mean_runtime_seconds": statistics.fmean(run.total_wall_seconds for run in runs) if runs else None,
            "median_runtime_seconds": statistics.median(run.total_wall_seconds for run in runs) if runs else None,
            "compute_seconds_per_valid_result": (total_wall / successful if successful else None),
            "tool_call_count": sum(run.tool_call_count for run in runs),
            "decision_call_count": decisions,
            "agent_api_call_count": int(agent_api_calls),
            "agent_total_tokens": int(agent_tokens),
            "agent_reported_estimated_cost_usd": agent_cost,
            "decision_quality": _ratio(recovered, decision_quality_denominator),
            "held_out_cases_passed": sum(item.passed for item in held_out),
            "held_out_case_count": len(held_out),
            "protocol_violation_count": sum(bool(run.protocol_violations) for run in runs),
            "failure_class_results": _failure_class_results(evaluations),
        }


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _usage_number(
    usage: Mapping[str, Any], key: str, *, include_auxiliary: bool
) -> float:
    source: Mapping[str, Any] = usage
    if include_auxiliary:
        combined = usage.get("total_including_auxiliary")
        if isinstance(combined, Mapping):
            source = combined
    value = source.get(key, 0)
    return float(value) if isinstance(value, (int, float)) else 0.0


def _failure_class_results(evaluations: list[CaseEvaluation]) -> dict[str, Any]:
    labels = sorted({item.failure_class for item in evaluations if item.failure_class})
    return {
        label: {
            "case_count": len(items),
            "passed": sum(item.passed for item in items),
            "pass_rate": _ratio(sum(item.passed for item in items), len(items)),
        }
        for label in labels
        for items in [[item for item in evaluations if item.failure_class == label]]
    }
