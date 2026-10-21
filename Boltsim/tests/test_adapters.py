from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents import (  # noqa: E402
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
from spe_agents.adapters import (  # noqa: E402
    AdapterCompatibilityError,
    AdapterExecutionError,
    AdapterStateError,
    UnsupportedCapabilityError,
)


def capabilities(**changes: object) -> AdapterCapabilities:
    base = AdapterCapabilities(
        adapter_name="mock-spe",
        adapter_version="0.1.0",
        engine_name="mock-qm",
        engine_version="test-only",
        supported_elements=frozenset({"H", "C", "N", "O"}),
        supported_methods=frozenset({"HF", "B3LYP"}),
        supported_basis_sets=frozenset({"STO-3G", "def2-SVP"}),
        supported_properties=frozenset({"total_energy"}),
        supports_open_shell=False,
        max_atoms=20,
    )
    return replace(base, **changes)


def water(task_id: str = "water-001", **changes: object) -> SPERequest:
    values: dict[str, object] = {
        "task_id": task_id,
        "atoms": (
            Atom("O", 0.0, 0.0, 0.0),
            Atom("H", 0.7586, 0.0, 0.5043),
            Atom("H", -0.7586, 0.0, 0.5043),
        ),
        "coordinate_unit": "angstrom",
        "charge": 0,
        "multiplicity": 1,
        "method": "HF",
        "basis": "STO-3G",
    }
    values.update(changes)
    return SPERequest(**values)  # type: ignore[arg-type]


def successful_result(request: SPERequest) -> AdapterResult:
    return AdapterResult(
        task_id=request.task_id,
        request_fingerprint=request.fingerprint(),
        engine_name="mock-qm",
        engine_version="test-only",
        converged=True,
        outputs={"total_energy": {"value": -74.96, "unit": "hartree"}},
        artifacts=(
            Artifact(
                name="engine-output",
                uri="memory://water.out",
                sha256="a" * 64,
                media_type="text/plain",
            ),
        ),
    )


class AdapterContractTests(unittest.TestCase):
    def test_mock_implements_versioned_protocol_and_discovers_capabilities(self) -> None:
        adapter = MockSPEAdapter(capabilities())
        self.assertIsInstance(adapter, SPEAdapter)
        self.assertEqual(adapter.protocol_version, ADAPTER_PROTOCOL_VERSION)
        require_compatible_adapter(adapter)
        self.assertEqual(adapter.capabilities().engine_name, "mock-qm")
        self.assertIn("B3LYP", adapter.capabilities().supported_methods)

    def test_supported_job_lifecycle_returns_only_scripted_result(self) -> None:
        request = water()
        expected = successful_result(request)
        adapter = MockSPEAdapter(capabilities())
        adapter.script_result(request.task_id, expected)

        job_id = adapter.submit(request)
        self.assertEqual(adapter.status(job_id), JobState.RUNNING)
        with self.assertRaises(AdapterStateError):
            adapter.result(job_id)
        self.assertEqual(adapter.status(job_id), JobState.COMPLETED)
        actual = adapter.result(job_id)

        self.assertIs(actual, expected)
        self.assertEqual(actual.request_fingerprint, request.fingerprint())
        self.assertEqual(actual.outputs["total_energy"]["unit"], "hartree")
        self.assertEqual(actual.artifacts[0].sha256, "a" * 64)

    def test_unsupported_settings_are_rejected_before_submission(self) -> None:
        request = water(method="CCSD(T)")
        adapter = MockSPEAdapter(capabilities())
        adapter.script_result(request.task_id, successful_result(request))

        with self.assertRaisesRegex(UnsupportedCapabilityError, "unsupported method"):
            adapter.submit(request)
        self.assertEqual(adapter.submitted_requests, [])

    def test_open_shell_is_rejected_when_not_advertised(self) -> None:
        request = water(multiplicity=3)
        adapter = MockSPEAdapter(capabilities())
        adapter.script_failure(
            request.task_id,
            AdapterFailure(FailureClass.NON_CONVERGENCE, "not reached", retryable=True),
        )
        with self.assertRaisesRegex(UnsupportedCapabilityError, "open-shell"):
            adapter.submit(request)

    def test_unscripted_mock_request_refuses_to_fabricate_result(self) -> None:
        adapter = MockSPEAdapter(capabilities())
        with self.assertRaisesRegex(AdapterStateError, "refusing to fabricate"):
            adapter.submit(water())

    def test_failure_is_structured_and_preserved(self) -> None:
        request = water()
        failure = AdapterFailure(
            FailureClass.NON_CONVERGENCE,
            "SCF iteration limit reached",
            retryable=True,
        )
        adapter = MockSPEAdapter(capabilities())
        adapter.script_failure(request.task_id, failure)
        job_id = adapter.submit(request)
        adapter.status(job_id)
        self.assertEqual(adapter.status(job_id), JobState.FAILED)
        with self.assertRaises(AdapterExecutionError) as raised:
            adapter.result(job_id)
        self.assertIs(raised.exception.failure, failure)

    def test_cancellation_is_terminal(self) -> None:
        request = water()
        adapter = MockSPEAdapter(capabilities())
        adapter.script_result(request.task_id, successful_result(request))
        job_id = adapter.submit(request)
        adapter.cancel(job_id)
        self.assertEqual(adapter.status(job_id), JobState.CANCELLED)
        with self.assertRaises(AdapterStateError):
            adapter.result(job_id)

    def test_request_fingerprint_is_stable_and_settings_sensitive(self) -> None:
        first = water(settings={"scf_max_cycles": 50})
        equivalent = water(settings={"scf_max_cycles": 50})
        changed = water(settings={"scf_max_cycles": 100})
        self.assertEqual(first.fingerprint(), equivalent.fingerprint())
        self.assertNotEqual(first.fingerprint(), changed.fingerprint())

    def test_incompatible_protocol_major_is_rejected(self) -> None:
        adapter = MockSPEAdapter(capabilities())
        adapter.protocol_version = "2.0"
        with self.assertRaises(AdapterCompatibilityError):
            require_compatible_adapter(adapter)


if __name__ == "__main__":
    unittest.main()
