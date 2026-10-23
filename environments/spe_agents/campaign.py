"""Manifest validation and evidence-aware execution for the initial SPE campaign."""

from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .quality import SPEArtifactAuditor
from .registry import ACTIVE_ENVIRONMENT_IDS, SPERegistry


DECLARED_METHODS = {
    "HF",
    "LDA",
    "PBE",
    "B3LYP",
    "PBE0",
    "TPSS",
    "M06-2X",
    "CAM-B3LYP",
    "wB97X-D",
    "wB97X-D3",
    "wB97M-V",
}
DECLARED_BASIS_SETS = {
    "STO-3G",
    "6-31G",
    "6-31G*",
    "6-311G**",
    "cc-pVDZ",
    "cc-pVTZ",
    "cc-pVQZ",
    "aug-cc-pVDZ",
    "aug-cc-pVTZ",
    "def2-SVP",
    "def2-TZVP",
    "def2-TZVPP",
    "def2-QZVP",
}

_ELEMENTS = (
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc "
    "Lv Ts Og"
).split()
ATOMIC_NUMBERS = {symbol: index for index, symbol in enumerate(_ELEMENTS, start=1)}


class CampaignConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class XYZStructure:
    path: Path
    comment: str
    elements: tuple[str, ...]
    coordinates: tuple[tuple[float, float, float], ...]


@dataclass(frozen=True)
class CampaignOutcome:
    test_id: str
    environment_id: str
    agent_name: str
    case_kind: str
    test_status: str
    job_status: str
    energy_difference_hartree: float | None
    scientific_validity: str
    error_handling: str
    provenance: dict[str, Any]
    runtime_seconds: float
    warnings: tuple[str, ...] = field(default_factory=tuple)
    validation_result: tuple[str, ...] = field(default_factory=tuple)
    audit_decision: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["warnings"] = list(self.warnings)
        result["validation_result"] = list(self.validation_result)
        return result


def parse_xyz(path: Path) -> XYZStructure:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CampaignConfigurationError(f"structure file unavailable: {path}") from exc
    if len(lines) < 2:
        raise CampaignConfigurationError(f"{path}: XYZ requires an atom count and comment line")
    try:
        count = int(lines[0].strip())
    except ValueError as exc:
        raise CampaignConfigurationError(f"{path}: invalid XYZ atom count") from exc
    if count < 1:
        raise CampaignConfigurationError(f"{path}: XYZ atom count must be positive")
    atom_lines = lines[2:]
    if len(atom_lines) != count:
        raise CampaignConfigurationError(
            f"{path}: declared {count} atoms but found {len(atom_lines)} coordinate rows"
        )
    elements: list[str] = []
    coordinates: list[tuple[float, float, float]] = []
    for line_number, line in enumerate(atom_lines, start=3):
        fields = line.split()
        if len(fields) != 4:
            raise CampaignConfigurationError(f"{path}:{line_number}: expected element and x y z")
        element = fields[0]
        if element not in ATOMIC_NUMBERS:
            raise CampaignConfigurationError(f"{path}:{line_number}: unknown element {element!r}")
        try:
            xyz = tuple(float(value) for value in fields[1:])
        except ValueError as exc:
            raise CampaignConfigurationError(f"{path}:{line_number}: invalid coordinate") from exc
        if len(xyz) != 3 or not all(math.isfinite(value) for value in xyz):
            raise CampaignConfigurationError(f"{path}:{line_number}: coordinates must be finite")
        elements.append(element)
        coordinates.append(xyz)  # type: ignore[arg-type]
    return XYZStructure(path, lines[1], tuple(elements), tuple(coordinates))


def validate_electron_parity(structure: XYZStructure, charge: int, multiplicity: int) -> None:
    electrons = sum(ATOMIC_NUMBERS[element] for element in structure.elements) - charge
    if electrons <= 0:
        raise CampaignConfigurationError("charge removes all electrons")
    if multiplicity < 1:
        raise CampaignConfigurationError("multiplicity must be positive")
    if electrons % 2 != (multiplicity - 1) % 2:
        raise CampaignConfigurationError(
            f"electron-count parity mismatch: {electrons} electrons and multiplicity {multiplicity}"
        )


class CampaignRunner:
    def __init__(self, project_root: Path | str, registry: SPERegistry | None = None):
        self.project_root = Path(project_root).resolve()
        self.registry = registry or SPERegistry(self.project_root / "environments")
        self.auditor = SPEArtifactAuditor()

    def load_manifest(self, path: Path | str) -> dict[str, Any]:
        manifest_path = Path(path)
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CampaignConfigurationError(f"cannot read campaign manifest: {exc}") from exc
        if not isinstance(raw, dict) or not isinstance(raw.get("cases"), list):
            raise CampaignConfigurationError("campaign manifest must contain a cases array")
        self.validate_manifest(raw)
        return raw

    def validate_manifest(self, manifest: Mapping[str, Any]) -> None:
        cases = manifest.get("cases")
        if not isinstance(cases, list):
            raise CampaignConfigurationError("cases must be an array")
        expected_count = manifest.get("expected_case_count", len(ACTIVE_ENVIRONMENT_IDS) * 3)
        if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 1:
            raise CampaignConfigurationError("expected_case_count must be a positive integer")
        if len(cases) != expected_count:
            raise CampaignConfigurationError(
                f"expected {expected_count} campaign cases, found {len(cases)}"
            )
        identifiers: set[str] = set()
        coverage: dict[str, set[str]] = {
            environment_id: set() for environment_id in ACTIVE_ENVIRONMENT_IDS
        }
        for case in cases:
            if not isinstance(case, dict):
                raise CampaignConfigurationError("each campaign case must be an object")
            test_id = case.get("test_id")
            environment_id = case.get("environment_id")
            kind = case.get("case_kind")
            if not isinstance(test_id, str) or not test_id:
                raise CampaignConfigurationError("every case requires a test_id")
            if test_id in identifiers:
                raise CampaignConfigurationError(f"duplicate test_id: {test_id}")
            identifiers.add(test_id)
            if environment_id not in coverage:
                raise CampaignConfigurationError(f"invalid environment_id in {test_id}")
            if kind not in {"valid", "invalid", "reference"}:
                raise CampaignConfigurationError(f"invalid case_kind in {test_id}")
            coverage[environment_id].add(kind)
            self.registry.get(environment_id)
        if manifest.get("require_three_case_coverage", True):
            incomplete = {
                key: value
                for key, value in coverage.items()
                if value != {"valid", "invalid", "reference"}
            }
            if incomplete:
                raise CampaignConfigurationError(f"campaign coverage is incomplete: {incomplete}")

    def run(self, manifest: Mapping[str, Any]) -> list[CampaignOutcome]:
        self.validate_manifest(manifest)
        return [self.run_case(case) for case in manifest["cases"]]

    def run_case(self, case: Mapping[str, Any]) -> CampaignOutcome:
        started = time.perf_counter()
        environment_id = str(case["environment_id"])
        agent = self.registry.get(environment_id)
        kind = str(case["case_kind"])
        mode = str(case.get("mode", "calculation"))
        findings: list[str] = []
        warnings: list[str] = []

        if mode == "audit":
            artifact_path = self.project_root / str(case["artifact_file"])
            try:
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                if not isinstance(artifact, dict):
                    raise ValueError("artifact must be an object")
                report = self.auditor.audit(artifact)
                expected = case.get("expected_audit_decision")
                passed = report.decision.value == expected
                findings.extend(f"{item.code}: {item.message}" for item in report.findings)
                return CampaignOutcome(
                    test_id=str(case["test_id"]),
                    environment_id=environment_id,
                    agent_name=agent.name,
                    case_kind=kind,
                    test_status="pass" if passed else "fail",
                    job_status="pass" if passed else "fail",
                    energy_difference_hartree=None,
                    scientific_validity="audited from preserved artifact evidence",
                    error_handling="audit decision matched expectation" if passed else "unexpected audit decision",
                    provenance={"artifact_file": str(artifact_path), "auditor": "SPEArtifactAuditor/v1"},
                    runtime_seconds=time.perf_counter() - started,
                    validation_result=tuple(findings),
                    audit_decision=report.decision.value,
                )
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                findings.append(str(exc))
                return self._failed_outcome(case, agent.name, started, findings)

        external_inputs = case.get("external_inputs", [])
        missing_external = [
            str(item.get("description", item))
            for item in external_inputs
            if isinstance(item, dict) and item.get("required") is True and not item.get("path")
        ]
        if missing_external:
            findings.extend(f"validated external prerequisite missing: {item}" for item in missing_external)

        calculations = case.get("calculations", [])
        if not isinstance(calculations, list):
            findings.append("calculations must be an array")
        else:
            for calculation in calculations:
                self._validate_calculation(calculation, findings)

        expect_rejection = case.get("expected_preflight") == "reject"
        if expect_rejection:
            caught = bool(findings)
            return CampaignOutcome(
                test_id=str(case["test_id"]),
                environment_id=environment_id,
                agent_name=agent.name,
                case_kind=kind,
                test_status="pass" if caught else "fail",
                job_status="pass" if caught else "fail",
                energy_difference_hartree=None,
                scientific_validity="invalid input rejected before submission" if caught else "invalid input was not rejected",
                error_handling="caught" if caught else "missed",
                provenance={"adapter_called": False},
                runtime_seconds=time.perf_counter() - started,
                validation_result=tuple(findings),
            )

        if findings:
            return CampaignOutcome(
                test_id=str(case["test_id"]),
                environment_id=environment_id,
                agent_name=agent.name,
                case_kind=kind,
                test_status="review",
                job_status="review",
                energy_difference_hartree=None,
                scientific_validity="not evaluated; required validated inputs are unavailable",
                error_handling="blocked safely before execution",
                provenance={"adapter_called": False},
                runtime_seconds=time.perf_counter() - started,
                validation_result=tuple(findings),
            )

        reference_file = case.get("reference_artifact")
        if reference_file and not (self.project_root / str(reference_file)).is_file():
            findings.append(f"independent reference artifact unavailable: {reference_file}")
            return CampaignOutcome(
                test_id=str(case["test_id"]),
                environment_id=environment_id,
                agent_name=agent.name,
                case_kind=kind,
                test_status="review",
                job_status="review",
                energy_difference_hartree=None,
                scientific_validity="not evaluated; independent reference unavailable",
                error_handling="missing reference reported",
                provenance={"adapter_called": False},
                runtime_seconds=time.perf_counter() - started,
                validation_result=tuple(findings),
            )

        warnings.append("boltzmann-spe-api has no verified live adapter; calculation not submitted")
        return CampaignOutcome(
            test_id=str(case["test_id"]),
            environment_id=environment_id,
            agent_name=agent.name,
            case_kind=kind,
            test_status="review",
            job_status="review",
            energy_difference_hartree=None,
            scientific_validity="preflight passed; execution and numerical validity not evaluated",
            error_handling="unverified adapter blocked safely",
            provenance={"adapter_called": False, "integration_status": agent.integration_status},
            runtime_seconds=time.perf_counter() - started,
            warnings=tuple(warnings),
            validation_result=("input preflight passed",),
        )

    def _validate_calculation(self, calculation: Any, findings: list[str]) -> None:
        if not isinstance(calculation, Mapping):
            findings.append("calculation entry must be an object")
            return
        required = ("file", "charge", "multiplicity", "method", "basis_set")
        missing = [field for field in required if field not in calculation]
        if missing:
            findings.append(f"calculation is missing fields: {', '.join(missing)}")
            return
        path = self.project_root / str(calculation["file"])
        try:
            structure = parse_xyz(path)
        except CampaignConfigurationError as exc:
            findings.append(str(exc))
            return
        charge = calculation["charge"]
        multiplicity = calculation["multiplicity"]
        if isinstance(charge, bool) or not isinstance(charge, int):
            findings.append(f"{path}: charge must be an integer")
            return
        if isinstance(multiplicity, bool) or not isinstance(multiplicity, int):
            findings.append(f"{path}: multiplicity must be an integer")
            return
        try:
            validate_electron_parity(structure, charge, multiplicity)
        except CampaignConfigurationError as exc:
            findings.append(f"{path}: {exc}")
        method = calculation["method"]
        basis = calculation["basis_set"]
        if method not in DECLARED_METHODS:
            findings.append(f"unsupported declared method: {method}")
        if basis not in DECLARED_BASIS_SETS:
            findings.append(f"unsupported declared basis set: {basis}")

    @staticmethod
    def _failed_outcome(
        case: Mapping[str, Any], agent_name: str, started: float, findings: list[str]
    ) -> CampaignOutcome:
        return CampaignOutcome(
            test_id=str(case["test_id"]),
            environment_id=str(case["environment_id"]),
            agent_name=agent_name,
            case_kind=str(case["case_kind"]),
            test_status="fail",
            job_status="fail",
            energy_difference_hartree=None,
            scientific_validity="not evaluated",
            error_handling="campaign harness error",
            provenance={"adapter_called": False},
            runtime_seconds=time.perf_counter() - started,
            validation_result=tuple(findings),
        )


def summarize(outcomes: list[CampaignOutcome]) -> dict[str, Any]:
    counts = {status: sum(item.test_status == status for item in outcomes) for status in ("pass", "fail", "review")}
    return {"total": len(outcomes), "counts": counts, "outcomes": [item.to_dict() for item in outcomes]}
