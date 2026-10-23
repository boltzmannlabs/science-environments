from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from .models import Approach, BenchmarkCase, Decision, DecisionAction


class DecisionProviderError(RuntimeError):
    pass


class DecisionProvider(Protocol):
    def request(self, payload: Mapping[str, Any]) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class CommandDecisionProvider:
    """Invoke an external controller through a small JSON stdin/stdout contract."""

    command: tuple[str, ...]
    timeout_seconds: float = 90.0

    @classmethod
    def from_command_line(cls, command: str, *, timeout_seconds: float = 90.0) -> "CommandDecisionProvider":
        parsed = tuple(shlex.split(command))
        if not parsed:
            raise ValueError("decision command must not be empty")
        return cls(parsed, timeout_seconds)

    def request(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        encoded = json.dumps(dict(payload), sort_keys=True)
        environment = dict(os.environ)
        # Some managed Agent Scientist launchers re-exec under their pinned
        # interpreter and cannot preserve piped stdin.  The benchmark payload
        # contains no reference answers or credentials, so carry the same JSON
        # through a narrowly named environment fallback as well.
        environment["BOLTZMANN_SPE_DECISION_PAYLOAD"] = encoded
        try:
            completed = subprocess.run(
                self.command,
                input=encoded,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
                env=environment,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DecisionProviderError(f"decision provider failed: {exc}") from exc
        if completed.returncode != 0:
            error = completed.stderr.strip() or completed.stdout.strip()
            raise DecisionProviderError(
                f"decision provider exited {completed.returncode}: {error[:1000]}"
            )
        try:
            value = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise DecisionProviderError("decision provider did not return one JSON object") from exc
        if not isinstance(value, dict):
            raise DecisionProviderError("decision provider response must be a JSON object")
        return value


class DecisionPolicy(Protocol):
    approach: Approach

    def decide(
        self,
        case: BenchmarkCase,
        observation: Mapping[str, Any],
        attempted_settings: Sequence[Mapping[str, Any]],
    ) -> tuple[Decision, tuple[Mapping[str, Any], ...]]: ...


def _parse_decision(raw: Mapping[str, Any]) -> Decision:
    try:
        action = DecisionAction(str(raw["action"]))
    except (KeyError, ValueError) as exc:
        raise DecisionProviderError("decision action must be 'retry' or 'stop'") from exc
    settings = raw.get("settings", {})
    evidence = raw.get("evidence", [])
    if not isinstance(settings, dict):
        raise DecisionProviderError("decision settings must be an object")
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise DecisionProviderError("decision evidence must be an array of strings")
    return Decision(
        action=action,
        settings=settings,
        reason=str(raw.get("reason", "")),
        evidence=tuple(evidence),
    )


@dataclass(frozen=True)
class FixedWorkflowPolicy:
    """Frozen conventional policy with one deterministic SCF retry."""

    approach: Approach = Approach.FIXED

    def decide(
        self,
        case: BenchmarkCase,
        observation: Mapping[str, Any],
        attempted_settings: Sequence[Mapping[str, Any]],
    ) -> tuple[Decision, tuple[Mapping[str, Any], ...]]:
        failure_class = observation.get("failure_class")
        if failure_class == "non_convergence" and len(attempted_settings) == 1:
            decision = Decision(
                DecisionAction.RETRY,
                {**dict(attempted_settings[-1]), "max_cycles": 200},
                "frozen rule: retry one SCF non-convergence with max_cycles=200",
                ("failure_class=non_convergence",),
            )
        elif failure_class == "timeout" and len(attempted_settings) == 1:
            proposed = dict(attempted_settings[-1])
            proposed["use_gpu"] = False
            decision = Decision(
                DecisionAction.RETRY,
                proposed,
                "frozen rule: retry one interrupted GPU attempt on CPU",
                ("failure_class=timeout",),
            )
        else:
            decision = Decision(
                DecisionAction.STOP,
                reason="frozen workflow has no further permitted recovery rule",
                evidence=(f"failure_class={observation.get('failure_class', 'unknown')}",),
            )
        return decision, ({"role": "fixed-policy", **decision.to_dict()},)


@dataclass(frozen=True)
class AgentScientistPolicy:
    provider: DecisionProvider
    approach: Approach = Approach.AGENT

    def decide(
        self,
        case: BenchmarkCase,
        observation: Mapping[str, Any],
        attempted_settings: Sequence[Mapping[str, Any]],
    ) -> tuple[Decision, tuple[Mapping[str, Any], ...]]:
        payload = _decision_payload("general-controller", case, observation, attempted_settings)
        raw = self.provider.request(payload)
        decision = _parse_decision(raw)
        return decision, (
            {"role": "general-controller", "request": payload, "response": dict(raw)},
        )


@dataclass(frozen=True)
class SpecialistAssistedPolicy:
    provider: DecisionProvider
    approach: Approach = Approach.AGENT_SPECIALIST

    def decide(
        self,
        case: BenchmarkCase,
        observation: Mapping[str, Any],
        attempted_settings: Sequence[Mapping[str, Any]],
    ) -> tuple[Decision, tuple[Mapping[str, Any], ...]]:
        specialist_payload = _decision_payload(
            "spe-specialist", case, observation, attempted_settings
        )
        specialist_raw = self.provider.request(specialist_payload)
        specialist = _parse_decision(specialist_raw)
        controller_payload = _decision_payload(
            "general-controller-review",
            case,
            observation,
            attempted_settings,
            specialist_recommendation=specialist.to_dict(),
        )
        controller_raw = self.provider.request(controller_payload)
        decision = _parse_decision(controller_raw)
        return decision, (
            {
                "role": "spe-specialist",
                "request": specialist_payload,
                "response": dict(specialist_raw),
            },
            {
                "role": "general-controller-review",
                "request": controller_payload,
                "response": dict(controller_raw),
            },
        )


def _decision_payload(
    role: str,
    case: BenchmarkCase,
    observation: Mapping[str, Any],
    attempted_settings: Sequence[Mapping[str, Any]],
    *,
    specialist_recommendation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "protocol": "boltzmann-spe-decision-v1",
        "role": role,
        "objective": "Choose one scientifically justified action without changing geometry, charge, multiplicity, method, or basis.",
        "case": case.public_payload(include_specialist_context=role == "spe-specialist"),
        "observation": dict(observation),
        "attempted_settings": [dict(item) for item in attempted_settings],
        "allowed_actions": {
            "retry": "Return complete settings using only permitted_setting_values.",
            "stop": "Stop when no justified permitted recovery remains.",
        },
        "response_schema": {
            "action": "retry|stop",
            "settings": {},
            "reason": "non-empty scientific justification",
            "evidence": ["diagnostic observations used"],
        },
        "hidden_reference_policy": "Reference energies and evaluator outcomes are unavailable to the decision maker.",
    }
    if specialist_recommendation is not None:
        payload["specialist_recommendation"] = dict(specialist_recommendation)
        payload["objective"] = (
            "Review the specialist recommendation and return the final permitted action. "
            "Do not accept it merely because it came from a specialist."
        )
    return payload
