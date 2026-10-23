"""Shared runtime for the standalone Boltzmann Labs SPE agent suite."""

from .adapters import (
    ADAPTER_PROTOCOL_VERSION,
    AdapterCapabilities,
    AdapterFailure,
    AdapterResult,
    Artifact,
    Atom,
    FailureClass,
    JobState,
    MockSPEAdapter,
    SPEAdapter,
    SPERequest,
    require_compatible_adapter,
)
from .evaluation import EvaluationDecision, EvaluationReport, IndependentEvaluator
from .models import SPEEnvironment, SPEConfigurationError
from .local_module_adapter import LocalBoltzmannSPEAdapter
from .prompts import build_system_prompt
from .quality import AuditDecision, AuditReport, SPEArtifactAuditor
from .registry import SPERegistry

__all__ = [
    "ADAPTER_PROTOCOL_VERSION",
    "AdapterCapabilities",
    "AdapterFailure",
    "AdapterResult",
    "Artifact",
    "Atom",
    "AuditDecision",
    "AuditReport",
    "EvaluationDecision",
    "EvaluationReport",
    "FailureClass",
    "IndependentEvaluator",
    "JobState",
    "LocalBoltzmannSPEAdapter",
    "MockSPEAdapter",
    "SPEAdapter",
    "SPEArtifactAuditor",
    "SPEConfigurationError",
    "SPEEnvironment",
    "SPERequest",
    "SPERegistry",
    "build_system_prompt",
    "require_compatible_adapter",
]
