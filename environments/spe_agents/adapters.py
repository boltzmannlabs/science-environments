"""Versioned execution boundary for SPE engine integrations.

The objects in this module describe the information an engine adapter must expose;
they do not make any engine operational.  ``MockSPEAdapter`` exists only for
contract and orchestration tests and returns results explicitly scripted by a test.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Protocol, runtime_checkable


ADAPTER_PROTOCOL_VERSION = "1.0"
_VERSION_PATTERN = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)$")


def _normalized_json(value: Any, label: str) -> Any:
    """Validate JSON data, reject non-finite numbers, and detach caller-owned data."""

    try:
        encoded = json.dumps(value, sort_keys=True, allow_nan=False)
        return json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must contain only finite JSON values") from exc


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


class AdapterError(RuntimeError):
    """Base class for adapter-boundary errors."""


class AdapterCompatibilityError(AdapterError):
    """Raised when an adapter implements an incompatible protocol version."""


class UnsupportedCapabilityError(AdapterError):
    """Raised before submission when requested science is unsupported."""


class UnknownJobError(AdapterError):
    """Raised for a job identifier that the adapter does not own."""


class AdapterStateError(AdapterError):
    """Raised when an operation is invalid for the current job state."""


class FailureClass(str, Enum):
    INVALID_INPUT = "invalid_input"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    TOOL_UNAVAILABLE = "tool_unavailable"
    CONFIGURATION_ERROR = "configuration_error"
    EXECUTION_ERROR = "execution_error"
    NON_CONVERGENCE = "non_convergence"
    OUTPUT_PARSE_ERROR = "output_parse_error"
    SCIENTIFIC_VALIDATION_FAILURE = "scientific_validation_failure"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Atom:
    element: str
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Z][a-z]?", self.element):
            raise ValueError(f"invalid element symbol: {self.element!r}")
        if not all(math.isfinite(value) for value in (self.x, self.y, self.z)):
            raise ValueError("atom coordinates must be finite")


@dataclass(frozen=True)
class SPERequest:
    """Normalized, fixed-geometry request passed to an adapter."""

    task_id: str
    atoms: tuple[Atom, ...]
    coordinate_unit: str
    charge: int
    multiplicity: int
    method: str
    basis: str
    requested_properties: tuple[str, ...] = ("total_energy",)
    settings: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task_id must not be empty")
        if not self.atoms:
            raise ValueError("at least one atom is required")
        if self.coordinate_unit not in {"angstrom", "bohr"}:
            raise ValueError("coordinate_unit must be 'angstrom' or 'bohr'")
        if isinstance(self.charge, bool) or not isinstance(self.charge, int):
            raise ValueError("charge must be an integer")
        if isinstance(self.multiplicity, bool) or not isinstance(self.multiplicity, int) or self.multiplicity < 1:
            raise ValueError("multiplicity must be a positive integer")
        if not self.method.strip() or not self.basis.strip():
            raise ValueError("method and basis must not be empty")
        if not self.requested_properties or not all(
            isinstance(item, str) and item.strip() for item in self.requested_properties
        ):
            raise ValueError("requested_properties must contain non-empty strings")
        normalized_settings = _normalized_json(dict(self.settings), "settings")
        object.__setattr__(self, "settings", _freeze_json(normalized_settings))

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "atoms": [
                {"element": atom.element, "x": atom.x, "y": atom.y, "z": atom.z}
                for atom in self.atoms
            ],
            "basis": self.basis,
            "charge": self.charge,
            "coordinate_unit": self.coordinate_unit,
            "method": self.method,
            "multiplicity": self.multiplicity,
            "requested_properties": list(self.requested_properties),
            "settings": _thaw_json(self.settings),
            "task_id": self.task_id,
        }

    def fingerprint(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AdapterCapabilities:
    adapter_name: str
    adapter_version: str
    engine_name: str
    engine_version: str
    supported_elements: frozenset[str]
    supported_methods: frozenset[str]
    supported_basis_sets: frozenset[str]
    supported_properties: frozenset[str]
    supports_open_shell: bool
    max_atoms: int
    supports_cancellation: bool = True

    def __post_init__(self) -> None:
        for label, value in (
            ("adapter_name", self.adapter_name),
            ("adapter_version", self.adapter_version),
            ("engine_name", self.engine_name),
            ("engine_version", self.engine_version),
        ):
            if not value.strip():
                raise ValueError(f"{label} must not be empty")
        if not self.supported_elements or not self.supported_methods or not self.supported_basis_sets:
            raise ValueError("element, method, and basis capabilities must not be empty")
        if not self.supported_properties:
            raise ValueError("supported_properties must not be empty")
        if isinstance(self.max_atoms, bool) or not isinstance(self.max_atoms, int) or self.max_atoms < 1:
            raise ValueError("max_atoms must be a positive integer")

    def validate(self, request: SPERequest) -> None:
        missing_elements = sorted({atom.element for atom in request.atoms} - self.supported_elements)
        unsupported_properties = sorted(set(request.requested_properties) - self.supported_properties)
        problems: list[str] = []
        if missing_elements:
            problems.append(f"unsupported elements: {', '.join(missing_elements)}")
        if request.method not in self.supported_methods:
            problems.append(f"unsupported method: {request.method}")
        if request.basis not in self.supported_basis_sets:
            problems.append(f"unsupported basis set: {request.basis}")
        if unsupported_properties:
            problems.append(f"unsupported properties: {', '.join(unsupported_properties)}")
        if request.multiplicity != 1 and not self.supports_open_shell:
            problems.append("open-shell calculations are unsupported")
        if len(request.atoms) > self.max_atoms:
            problems.append(f"atom count {len(request.atoms)} exceeds limit {self.max_atoms}")
        if problems:
            raise UnsupportedCapabilityError("; ".join(problems))


@dataclass(frozen=True)
class Artifact:
    name: str
    uri: str
    sha256: str
    media_type: str = "application/octet-stream"

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.uri.strip() or not self.media_type.strip():
            raise ValueError("artifact name, URI, and media type must not be empty")
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ValueError("artifact sha256 must be 64 lowercase hexadecimal characters")


@dataclass(frozen=True)
class AdapterResult:
    task_id: str
    request_fingerprint: str
    engine_name: str
    engine_version: str
    converged: bool
    outputs: Mapping[str, Any]
    artifacts: tuple[Artifact, ...]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.engine_name.strip() or not self.engine_version.strip():
            raise ValueError("result identifiers and engine provenance must not be empty")
        if not re.fullmatch(r"[0-9a-f]{64}", self.request_fingerprint):
            raise ValueError("request_fingerprint must be a SHA-256 digest")
        normalized_outputs = _normalized_json(dict(self.outputs), "result outputs")
        object.__setattr__(self, "outputs", _freeze_json(normalized_outputs))


@dataclass(frozen=True)
class AdapterFailure:
    failure_class: FailureClass
    message: str
    retryable: bool

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("failure message must not be empty")


class AdapterExecutionError(AdapterError):
    def __init__(self, failure: AdapterFailure):
        super().__init__(f"{failure.failure_class.value}: {failure.message}")
        self.failure = failure


@runtime_checkable
class SPEAdapter(Protocol):
    """Protocol implemented by each concrete SPE engine integration."""

    @property
    def protocol_version(self) -> str: ...

    def capabilities(self) -> AdapterCapabilities: ...

    def submit(self, request: SPERequest) -> str: ...

    def status(self, job_id: str) -> JobState: ...

    def cancel(self, job_id: str) -> None: ...

    def result(self, job_id: str) -> AdapterResult: ...


def require_compatible_adapter(adapter: SPEAdapter) -> None:
    """Reject adapters with a different protocol major version."""

    expected = _VERSION_PATTERN.fullmatch(ADAPTER_PROTOCOL_VERSION)
    actual = _VERSION_PATTERN.fullmatch(adapter.protocol_version)
    if expected is None or actual is None:
        raise AdapterCompatibilityError(
            f"invalid adapter protocol version {adapter.protocol_version!r}; expected MAJOR.MINOR"
        )
    if actual.group("major") != expected.group("major"):
        raise AdapterCompatibilityError(
            f"adapter protocol {adapter.protocol_version} is incompatible with "
            f"runtime protocol {ADAPTER_PROTOCOL_VERSION}"
        )


@dataclass
class _MockJob:
    request: SPERequest
    result: AdapterResult | None
    failure: AdapterFailure | None
    state: JobState = JobState.QUEUED


class MockSPEAdapter:
    """Deterministic contract-test adapter; never invents calculation outputs."""

    protocol_version = ADAPTER_PROTOCOL_VERSION

    def __init__(self, capabilities: AdapterCapabilities):
        self._capabilities = capabilities
        self._scripts: dict[str, AdapterResult | AdapterFailure] = {}
        self._jobs: dict[str, _MockJob] = {}
        self.submitted_requests: list[SPERequest] = []

    def capabilities(self) -> AdapterCapabilities:
        return self._capabilities

    def script_result(self, task_id: str, result: AdapterResult) -> None:
        if result.task_id != task_id:
            raise ValueError("scripted result task_id does not match script key")
        self._scripts[task_id] = result

    def script_failure(self, task_id: str, failure: AdapterFailure) -> None:
        self._scripts[task_id] = failure

    def submit(self, request: SPERequest) -> str:
        require_compatible_adapter(self)
        self._capabilities.validate(request)
        if request.task_id not in self._scripts:
            raise AdapterStateError(
                f"no mock outcome scripted for task {request.task_id!r}; refusing to fabricate one"
            )
        scripted = self._scripts[request.task_id]
        if isinstance(scripted, AdapterResult):
            if scripted.request_fingerprint != request.fingerprint():
                raise AdapterStateError("scripted result fingerprint does not match request")
            result, failure = scripted, None
        else:
            result, failure = None, scripted
        job_id = f"mock-{len(self._jobs) + 1:04d}"
        self._jobs[job_id] = _MockJob(request=request, result=result, failure=failure)
        self.submitted_requests.append(request)
        return job_id

    def status(self, job_id: str) -> JobState:
        job = self._job(job_id)
        if job.state == JobState.QUEUED:
            job.state = JobState.RUNNING
        elif job.state == JobState.RUNNING:
            job.state = JobState.COMPLETED if job.result is not None else JobState.FAILED
        return job.state

    def cancel(self, job_id: str) -> None:
        job = self._job(job_id)
        if not self._capabilities.supports_cancellation:
            raise UnsupportedCapabilityError("adapter does not support cancellation")
        if job.state in {JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED}:
            raise AdapterStateError(f"cannot cancel job in {job.state.value} state")
        job.state = JobState.CANCELLED

    def result(self, job_id: str) -> AdapterResult:
        job = self._job(job_id)
        if job.state == JobState.FAILED:
            if job.failure is None:  # defensive invariant
                raise AdapterStateError("failed mock job has no failure record")
            raise AdapterExecutionError(job.failure)
        if job.state != JobState.COMPLETED or job.result is None:
            raise AdapterStateError(f"result unavailable while job is {job.state.value}")
        return job.result

    def _job(self, job_id: str) -> _MockJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise UnknownJobError(f"unknown job: {job_id}") from exc
