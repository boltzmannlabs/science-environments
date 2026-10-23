from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import BenchmarkBudget, BenchmarkCase, CaseExpectation, Split


class DatasetError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class BenchmarkDataset:
    benchmark_id: str
    schema_version: str
    project_root: Path
    manifest_path: Path
    manifest_sha256: str
    budget: BenchmarkBudget
    cases: tuple[BenchmarkCase, ...]
    permitted_methods: tuple[str, ...]
    permitted_basis_sets: tuple[str, ...]
    reference_store_path: Path
    reference_store_sha256: str

    def cases_for_split(self, split: Split | None) -> tuple[BenchmarkCase, ...]:
        if split is None:
            return self.cases
        return tuple(case for case in self.cases if case.split is split)


def _require(raw: dict[str, Any], key: str, expected: type) -> Any:
    value = raw.get(key)
    if not isinstance(value, expected):
        raise DatasetError(f"{key!r} must be {expected.__name__}")
    return value


def load_dataset(manifest_path: Path | str, project_root: Path | str) -> BenchmarkDataset:
    manifest_path = Path(manifest_path).resolve()
    project_root = Path(project_root).resolve()
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetError(f"cannot load benchmark manifest: {exc}") from exc
    if not isinstance(raw, dict):
        raise DatasetError("benchmark manifest must be an object")

    methods = tuple(_require(raw, "permitted_methods", list))
    bases = tuple(_require(raw, "permitted_basis_sets", list))
    if not methods or not all(isinstance(item, str) and item for item in methods):
        raise DatasetError("permitted_methods must contain strings")
    if not bases or not all(isinstance(item, str) and item for item in bases):
        raise DatasetError("permitted_basis_sets must contain strings")

    budget_raw = _require(raw, "budget", dict)
    budget = BenchmarkBudget(
        max_tool_calls=int(budget_raw["max_tool_calls"]),
        max_retries=int(budget_raw["max_retries"]),
        per_attempt_timeout_seconds=float(budget_raw["per_attempt_timeout_seconds"]),
        max_case_wall_seconds=float(budget_raw["max_case_wall_seconds"]),
    )

    reference_raw = _require(raw, "reference_store", dict)
    reference_path = (project_root / str(reference_raw["path"])).resolve()
    expected_reference_hash = str(reference_raw["sha256"])
    if not reference_path.is_file():
        raise DatasetError(f"reference store is missing: {reference_path}")
    actual_reference_hash = sha256_file(reference_path)
    if actual_reference_hash != expected_reference_hash:
        raise DatasetError(
            f"reference store hash mismatch: expected {expected_reference_hash}, got {actual_reference_hash}"
        )

    cases_raw = _require(raw, "cases", list)
    cases: list[BenchmarkCase] = []
    identifiers: set[str] = set()
    for item in cases_raw:
        if not isinstance(item, dict):
            raise DatasetError("each benchmark case must be an object")
        case_id = str(item.get("case_id", ""))
        if not case_id or case_id in identifiers:
            raise DatasetError(f"case IDs must be non-empty and unique: {case_id!r}")
        identifiers.add(case_id)
        try:
            split = Split(str(item["split"]))
            expectation = CaseExpectation(str(item["expectation"]))
        except (KeyError, ValueError) as exc:
            raise DatasetError(f"{case_id}: invalid split or expectation") from exc
        structure = (project_root / str(item["structure_file"])).resolve()
        expected_hash = str(item["structure_sha256"])
        # Deliberately missing files are permitted only for invalid-input cases.
        if structure.is_file():
            actual_hash = sha256_file(structure)
            if actual_hash != expected_hash:
                raise DatasetError(
                    f"{case_id}: structure hash mismatch: expected {expected_hash}, got {actual_hash}"
                )
        elif expectation is not CaseExpectation.INVALID:
            raise DatasetError(f"{case_id}: structure file is missing: {structure}")
        method = str(item["method"])
        basis = str(item["basis"])
        if (method not in methods or basis not in bases) and expectation is not CaseExpectation.INVALID:
            raise DatasetError(f"{case_id}: method or basis is outside the frozen protocol")
        setting_values_raw = item.get("permitted_setting_values", {})
        if not isinstance(setting_values_raw, dict) or not all(
            isinstance(values, list) and values for values in setting_values_raw.values()
        ):
            raise DatasetError(f"{case_id}: permitted_setting_values must contain non-empty arrays")
        cases.append(
            BenchmarkCase(
                case_id=case_id,
                split=split,
                expectation=expectation,
                structure_file=structure,
                structure_sha256=expected_hash,
                charge=int(item["charge"]),
                multiplicity=int(item["multiplicity"]),
                method=method,
                basis=basis,
                requested_properties=tuple(item.get("requested_properties", ["total_energy"])),
                initial_settings=dict(item.get("initial_settings", {})),
                permitted_setting_values={
                    str(key): tuple(values) for key, values in setting_values_raw.items()
                },
                reference_id=(str(item["reference_id"]) if item.get("reference_id") else None),
                notes=str(item.get("notes", "")),
                fault_rules=tuple(dict(rule) for rule in item.get("fault_rules", [])),
                specialist_context=dict(item.get("specialist_context", {})),
            )
        )

    if not cases:
        raise DatasetError("benchmark manifest has no cases")
    for split in Split:
        if not any(case.split is split for case in cases):
            raise DatasetError(f"benchmark has no {split.value} cases")
    required_expectations = {
        CaseExpectation.VALID,
        CaseExpectation.RECOVERABLE,
        CaseExpectation.INVALID,
    }
    if str(raw["schema_version"]).startswith("2"):
        required_expectations.add(CaseExpectation.EXPECTED_FAILURE)
    for expectation in required_expectations:
        if not any(case.expectation is expectation for case in cases):
            raise DatasetError(f"benchmark has no {expectation.value} cases")

    return BenchmarkDataset(
        benchmark_id=str(raw["benchmark_id"]),
        schema_version=str(raw["schema_version"]),
        project_root=project_root,
        manifest_path=manifest_path,
        manifest_sha256=sha256_file(manifest_path),
        budget=budget,
        cases=tuple(cases),
        permitted_methods=methods,
        permitted_basis_sets=bases,
        reference_store_path=reference_path,
        reference_store_sha256=actual_reference_hash,
    )
