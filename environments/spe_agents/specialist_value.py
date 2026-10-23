"""Independent specialist-on/off analysis benchmark support."""

from __future__ import annotations

import hashlib
import json
import math
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


WARNING_CODES = (
    "basis_metadata_mismatch",
    "charge_label_mismatch",
    "duplicate_geometry",
    "excessive_spin_contamination",
    "incomplete_convergence_series",
    "invalid_electron_parity",
    "malformed_structure",
    "method_metadata_mismatch",
    "missing_or_nonconverged_component",
    "orbital_unit_inconsistency",
    "reaction_energy_withheld",
    "stoichiometry_sign_mismatch",
    "unsupported_basis",
    "unsupported_method",
)

QUANTITY_SCOPES = (
    "basis_series_electronic_energy",
    "fixed_geometry_electronic_energy",
    "fixed_geometry_electronic_energy_difference",
    "fixed_geometry_electronic_reaction_energy",
    "input_validation",
    "method_sensitivity_electronic_energy",
    "open_shell_electronic_energy",
    "orbital_analysis",
    "spin_resolved_orbital_analysis",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


@dataclass(frozen=True)
class AnalysisDataset:
    root: Path
    manifest: Mapping[str, Any]
    cases: Mapping[str, Mapping[str, Any]]
    references: Mapping[str, Mapping[str, Any]]


def load_dataset(root: Path, manifest_path: Path) -> AnalysisDataset:
    root = root.resolve()
    manifest = load_json(manifest_path.resolve())
    for key in ("backend_evidence", "legacy_evidence", "reference_store"):
        item = manifest[key]
        path = root / item["path"]
        if sha256(path) != item["sha256"]:
            raise ValueError(f"{key} hash mismatch: {path}")
    cases: dict[str, Mapping[str, Any]] = {}
    for item in manifest["cases"]:
        path = root / item["case_file"]
        if sha256(path) != item["case_sha256"]:
            raise ValueError(f"case hash mismatch: {path}")
        case = load_json(path)
        if case["case_id"] != item["case_id"]:
            raise ValueError(f"case ID mismatch: {path}")
        cases[item["case_id"]] = case
    reference_data = load_json(root / manifest["reference_store"]["path"])
    references = {item["case_id"]: item for item in reference_data["references"]}
    if set(cases) != set(references):
        raise ValueError("case/reference IDs differ")
    return AnalysisDataset(root, manifest, cases, references)


@dataclass(frozen=True)
class CommandProvider:
    command: tuple[str, ...]
    timeout_seconds: float = 120.0

    @classmethod
    def from_line(cls, command: str, timeout_seconds: float = 120.0) -> "CommandProvider":
        parsed = tuple(shlex.split(command))
        if not parsed:
            raise ValueError("analysis command must not be empty")
        return cls(parsed, timeout_seconds)

    def request(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        completed = subprocess.run(
            self.command,
            input=json.dumps(dict(payload), sort_keys=True),
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"analysis provider failed ({completed.returncode}): {detail[:2000]}")
        value = json.loads(completed.stdout)
        if not isinstance(value, dict):
            raise ValueError("analysis provider must return one JSON object")
        return value


def response_schema() -> dict[str, Any]:
    return {
        "disposition": "accept|reject|review",
        "selected_records": ["labels safe to use"],
        "excluded_records": ["labels rejected or withheld"],
        "warning_codes": ["exact snake_case codes from warning_code_vocabulary"],
        "quantity_scope": "exactly one value from quantity_scope_vocabulary",
        "values": {
            "key from case.output_contract.value_keys_when_supported": "number|string|array"
        },
        "explanation": "concise evidence-based explanation",
    }


def analysis_payload(
    case: Mapping[str, Any],
    *,
    role: str,
    specialist_contract: Mapping[str, Any] | None = None,
    specialist_recommendation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "protocol": "boltzmann-spe-specialist-analysis-v1",
        "role": role,
        "objective": (
            "Audit the supplied fixed-geometry SPE request/results and return only the "
            "structured scientific decision. Do not run calculations, change inputs, infer "
            "missing energies, or claim free energies/accuracy not supported by the records."
        ),
        "case": dict(case),
        "common_rules": [
            "Accept only records with consistent input/output metadata and required convergence.",
            "Reject invalid requests before calculation and never silently repair charge, spin, method, basis, units, or stoichiometry.",
            "Use review when valid evidence remains but a component must be excluded or a scientific diagnostic prevents a clean acceptance.",
            "Return record labels exactly as supplied.",
            "Use case.output_contract.quantity_scope verbatim.",
            "When evidence supports a result, return every case.output_contract.value_keys_when_supported key verbatim; omit unavailable values rather than inventing them.",
            "Report values in the requested units; do not rename electronic energies as free energies or activation energies.",
        ],
        "warning_code_vocabulary": list(WARNING_CODES),
        "quantity_scope_vocabulary": list(QUANTITY_SCOPES),
        "response_schema": response_schema(),
        "hidden_reference_policy": "Expected answers are evaluator-only and unavailable here.",
    }
    if specialist_contract is not None:
        value["specialist_contract"] = dict(specialist_contract)
    if specialist_recommendation is not None:
        value["specialist_recommendation"] = dict(specialist_recommendation)
        value["objective"] = (
            "Independently review the specialist recommendation against the case and common "
            "rules. Return the final structured decision; do not defer merely because it came "
            "from a specialist."
        )
    return value


def run_arm(
    case: Mapping[str, Any],
    *,
    arm: str,
    provider: CommandProvider,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    calls: list[dict[str, Any]] = []
    if arm == "agent-scientist":
        request = analysis_payload(case, role="general-controller")
        response = provider.request(request)
        calls.append({"role": "general-controller", "response": response})
        final = response
    elif arm == "agent-scientist-plus-specialist":
        specialist_request = analysis_payload(
            case, role="spe-specialist", specialist_contract=contract
        )
        specialist = provider.request(specialist_request)
        calls.append({"role": "spe-specialist", "response": specialist})
        review_request = analysis_payload(
            case,
            role="general-controller-review",
            specialist_recommendation={
                key: value for key, value in specialist.items() if key != "agent_scientist_usage"
            },
        )
        final = provider.request(review_request)
        calls.append({"role": "general-controller-review", "response": final})
    else:
        raise ValueError(f"unknown arm: {arm}")
    return {
        "case_id": case["case_id"],
        "environment_id": case["environment_id"],
        "arm": arm,
        "wall_seconds": time.perf_counter() - started,
        "calls": calls,
        "response": {key: value for key, value in final.items() if key != "agent_scientist_usage"},
        "usage": combined_usage(calls),
    }


def combined_usage(calls: list[Mapping[str, Any]]) -> dict[str, float]:
    totals = {"api_calls": 0.0, "total_tokens": 0.0, "estimated_cost_usd": 0.0}
    for call in calls:
        response = call.get("response", {})
        usage = response.get("agent_scientist_usage", {}) if isinstance(response, Mapping) else {}
        source = usage.get("total_including_auxiliary", usage) if isinstance(usage, Mapping) else {}
        if not isinstance(source, Mapping):
            continue
        for key in totals:
            value = source.get(key, 0)
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                totals[key] += float(value)
    return totals


def evaluate(run: Mapping[str, Any], reference: Mapping[str, Any], tolerance: float) -> dict[str, Any]:
    response = run["response"]
    findings: list[str] = []
    for key in ("disposition", "quantity_scope"):
        if response.get(key) != reference.get(key):
            findings.append(f"{key}: expected {reference.get(key)!r}, got {response.get(key)!r}")
    for key in ("selected_records", "excluded_records", "warning_codes"):
        actual = response.get(key)
        expected = reference.get(key, [])
        if not isinstance(actual, list) or sorted(actual) != sorted(expected):
            findings.append(f"{key}: expected {sorted(expected)!r}, got {actual!r}")
    actual_values = response.get("values")
    if not isinstance(actual_values, Mapping):
        findings.append("values must be an object")
        actual_values = {}
    for key, expected in reference.get("values", {}).items():
        if key not in actual_values:
            findings.append(f"missing value: {key}")
            continue
        actual = actual_values[key]
        if isinstance(expected, (int, float)) and not isinstance(expected, bool):
            if not isinstance(actual, (int, float)) or not math.isfinite(float(actual)):
                findings.append(f"{key} is not a finite number")
            elif abs(float(actual) - float(expected)) > tolerance:
                findings.append(f"{key}: expected {expected:.12g}, got {actual:.12g}")
        elif actual != expected:
            findings.append(f"{key}: expected {expected!r}, got {actual!r}")
    encoded = json.dumps(response, sort_keys=True).lower()
    for term in reference.get("forbidden_terms", []):
        if term.lower() in encoded:
            findings.append(f"forbidden unsupported claim: {term}")
    return {"passed": not findings, "findings": findings}
