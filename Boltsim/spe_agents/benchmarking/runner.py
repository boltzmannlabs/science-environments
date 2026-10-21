from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol

from spe_agents.adapters import Atom, SPERequest
from spe_agents.campaign import CampaignConfigurationError, parse_xyz, validate_electron_parity

from .models import (
    Approach,
    Attempt,
    BenchmarkBudget,
    BenchmarkCase,
    CaseRun,
    DecisionAction,
    RunStatus,
    TraceEvent,
)
from .policies import DecisionPolicy, DecisionProviderError


class ExecutionBackend(Protocol):
    def execute(self, request: SPERequest, *, timeout_seconds: float) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class LocalSubprocessBackend:
    run_root: Path
    module_root: Path | None = None

    def execute(self, request: SPERequest, *, timeout_seconds: float) -> Mapping[str, Any]:
        attempt_id = f"attempt-{uuid.uuid4().hex[:12]}"
        attempt_root = self.run_root / attempt_id
        request_path = attempt_root / "request.json"
        result_path = attempt_root / "worker_result.json"
        artifact_root = attempt_root / "artifacts"
        attempt_root.mkdir(parents=True, exist_ok=False)
        request_path.write_text(
            json.dumps(request.canonical_payload(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        command = [
            sys.executable,
            "-m",
            "spe_agents.benchmarking.worker",
            "--request",
            str(request_path),
            "--artifact-root",
            str(artifact_root),
            "--result",
            str(result_path),
        ]
        if self.module_root is not None:
            command.extend(["--module-root", str(self.module_root)])
        environment = dict(os.environ)
        src_root = str(Path(__file__).resolve().parents[2])
        existing_path = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = src_root if not existing_path else f"{src_root}:{existing_path}"
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "wall_seconds": time.perf_counter() - started,
                "failure_class": "timeout",
                "failure_message": f"attempt exceeded {timeout_seconds:.3f} seconds",
                "retryable": True,
            }
        if not result_path.is_file():
            return {
                "status": "failed",
                "wall_seconds": time.perf_counter() - started,
                "failure_class": "worker_error",
                "failure_message": (completed.stderr or completed.stdout or "worker produced no result")[:2000],
                "retryable": False,
            }
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                "status": "failed",
                "wall_seconds": time.perf_counter() - started,
                "failure_class": "output_parse_error",
                "failure_message": str(exc),
                "retryable": False,
            }
        result["worker_exit_code"] = completed.returncode
        return result


class BenchmarkRunner:
    def __init__(
        self,
        backend: ExecutionBackend,
        budget: BenchmarkBudget,
        *,
        supported_methods: tuple[str, ...] | None = None,
        supported_basis_sets: tuple[str, ...] | None = None,
    ):
        self.backend = backend
        self.budget = budget
        self.supported_methods = frozenset(supported_methods or ())
        self.supported_basis_sets = frozenset(supported_basis_sets or ())

    def run_case(self, case: BenchmarkCase, policy: DecisionPolicy) -> CaseRun:
        started = time.perf_counter()
        trace: list[TraceEvent] = []
        attempts: list[Attempt] = []
        decisions: list[Mapping[str, Any]] = []
        violations: list[str] = []
        fault_counts = [0 for _ in case.fault_rules]
        event_counter = 0

        def record(kind: str, payload: Mapping[str, Any]) -> None:
            nonlocal event_counter
            event_counter += 1
            trace.append(TraceEvent(event_counter, kind, payload, time.perf_counter() - started))

        findings, atoms = self._preflight(case)
        record("preflight", {"passed": not findings, "findings": list(findings)})
        if findings:
            return CaseRun(
                case.case_id,
                case.split,
                case.expectation,
                policy.approach,
                RunStatus.REJECTED,
                case.method,
                case.basis,
                case.charge,
                case.multiplicity,
                (),
                (),
                tuple(trace),
                time.perf_counter() - started,
                preflight_findings=tuple(findings),
            )

        settings: Mapping[str, Any] = dict(case.initial_settings)
        attempted_settings: list[Mapping[str, Any]] = []
        retries = 0
        final_status = RunStatus.FAILED
        while True:
            elapsed = time.perf_counter() - started
            if len(attempts) >= self.budget.max_tool_calls or retries > self.budget.max_retries:
                final_status = RunStatus.BUDGET_EXHAUSTED
                record("budget-stop", {"tool_calls": len(attempts), "retries": retries})
                break
            remaining = self.budget.max_case_wall_seconds - elapsed
            if remaining <= 0:
                final_status = RunStatus.BUDGET_EXHAUSTED
                record("budget-stop", {"reason": "case wall-clock budget exhausted"})
                break
            request = SPERequest(
                task_id=f"{case.case_id}-{policy.approach.value}-attempt-{len(attempts) + 1}",
                atoms=atoms,
                coordinate_unit="angstrom",
                charge=case.charge,
                multiplicity=case.multiplicity,
                method=case.method,
                basis=case.basis,
                requested_properties=case.requested_properties,
                settings=settings,
            )
            attempted_settings.append(dict(settings))
            record("tool-submit", {"settings": dict(settings), "request_fingerprint": request.fingerprint()})
            injected = self._injected_failure(case, settings, fault_counts)
            if injected is not None:
                raw = injected
                record(
                    "synthetic-fault",
                    {
                        "failure_class": raw["failure_class"],
                        "message": raw["failure_message"],
                    },
                )
            else:
                raw = self.backend.execute(
                    request,
                    timeout_seconds=min(self.budget.per_attempt_timeout_seconds, remaining),
                )
            attempt = Attempt(
                sequence=len(attempts) + 1,
                settings=dict(settings),
                status=str(raw.get("status", "failed")),
                wall_seconds=float(raw.get("wall_seconds", 0.0)),
                engine_seconds=(float(raw["engine_seconds"]) if raw.get("engine_seconds") is not None else None),
                job_id=(str(raw["job_id"]) if raw.get("job_id") else None),
                energy_hartree=(float(raw["energy_hartree"]) if raw.get("energy_hartree") is not None else None),
                converged=(bool(raw["converged"]) if raw.get("converged") is not None else None),
                failure_class=(str(raw["failure_class"]) if raw.get("failure_class") else None),
                failure_message=(str(raw["failure_message"]) if raw.get("failure_message") else None),
                artifacts=tuple(raw.get("artifacts", [])),
                synthetic_fault=bool(raw.get("synthetic_fault", False)),
            )
            attempts.append(attempt)
            record("tool-result", attempt.to_dict())
            if attempt.status == "completed" and attempt.converged and attempt.energy_hartree is not None:
                final_status = RunStatus.COMPLETED
                break
            observation = {
                "failure_class": attempt.failure_class or "unknown",
                "failure_message": attempt.failure_message or "",
                "retryable": bool(raw.get("retryable", False)),
                "attempt": attempt.sequence,
                "elapsed_seconds": time.perf_counter() - started,
            }
            try:
                decision, decision_trace = policy.decide(case, observation, attempted_settings)
            except DecisionProviderError as exc:
                final_status = RunStatus.FAILED
                record("decision-provider-error", {"message": str(exc)})
                break
            decisions.extend(decision_trace)
            record("decision", decision.to_dict())
            if decision.action is DecisionAction.STOP:
                final_status = RunStatus.FAILED
                break
            proposed = dict(decision.settings)
            violation = self._validate_retry(case, proposed, attempted_settings)
            if violation:
                violations.append(violation)
                final_status = RunStatus.PROTOCOL_VIOLATION
                record("protocol-violation", {"message": violation})
                break
            settings = proposed
            retries += 1

        return CaseRun(
            case.case_id,
            case.split,
            case.expectation,
            policy.approach,
            final_status,
            case.method,
            case.basis,
            case.charge,
            case.multiplicity,
            tuple(attempts),
            tuple(decisions),
            tuple(trace),
            time.perf_counter() - started,
            tuple(violations),
        )

    def _preflight(self, case: BenchmarkCase) -> tuple[list[str], tuple[Atom, ...]]:
        findings: list[str] = []
        if self.supported_methods and case.method not in self.supported_methods:
            findings.append(f"unsupported method: {case.method}")
        if self.supported_basis_sets and case.basis not in self.supported_basis_sets:
            findings.append(f"unsupported basis set: {case.basis}")
        try:
            structure = parse_xyz(case.structure_file)
            validate_electron_parity(structure, case.charge, case.multiplicity)
        except CampaignConfigurationError as exc:
            findings.append(str(exc))
            return findings, ()
        atoms = tuple(
            Atom(element, *coordinates)
            for element, coordinates in zip(structure.elements, structure.coordinates, strict=True)
        )
        return findings, atoms

    @staticmethod
    def _injected_failure(
        case: BenchmarkCase,
        settings: Mapping[str, Any],
        counts: list[int],
    ) -> Mapping[str, Any] | None:
        """Apply a frozen harness fault without disclosing it to the policy in advance."""
        for index, rule in enumerate(case.fault_rules):
            match = rule.get("match_settings", {})
            if not isinstance(match, Mapping) or any(settings.get(key) != value for key, value in match.items()):
                continue
            maximum = int(rule.get("max_occurrences", 1))
            if counts[index] >= maximum:
                continue
            counts[index] += 1
            return {
                "status": "failed",
                "wall_seconds": float(rule.get("wall_seconds", 0.01)),
                "failure_class": str(rule["failure_class"]),
                "failure_message": str(rule["failure_message"]),
                "retryable": bool(rule.get("retryable", False)),
                "synthetic_fault": True,
            }
        return None

    @staticmethod
    def _validate_retry(
        case: BenchmarkCase,
        settings: Mapping[str, Any],
        attempted_settings: list[Mapping[str, Any]],
    ) -> str | None:
        if not settings:
            return "retry settings must not be empty"
        missing = sorted(set(case.permitted_setting_values) - set(settings))
        if missing:
            return f"retry omitted required frozen settings: {', '.join(missing)}"
        unknown = sorted(set(settings) - set(case.permitted_setting_values))
        if unknown:
            return f"retry used settings outside the frozen action space: {', '.join(unknown)}"
        for key, value in settings.items():
            if value not in case.permitted_setting_values[key]:
                return f"retry value {key}={value!r} is outside the frozen action space"
        if any(dict(previous) == dict(settings) for previous in attempted_settings):
            return "retry repeated identical settings without a changed action"
        return None
