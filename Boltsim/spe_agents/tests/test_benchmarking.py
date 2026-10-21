from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents.benchmarking.dataset import DatasetError, load_dataset  # noqa: E402
from spe_agents.benchmarking.accuracy import (  # noqa: E402
    AccuracyTrackError,
    validate_accuracy_track,
)
from spe_agents.benchmarking.evaluator import BenchmarkEvaluator, ReferenceStore  # noqa: E402
from spe_agents.benchmarking.models import Approach, CaseExpectation, RunStatus, Split  # noqa: E402
from spe_agents.benchmarking.policies import (  # noqa: E402
    AgentScientistPolicy,
    FixedWorkflowPolicy,
    SpecialistAssistedPolicy,
)
from spe_agents.benchmarking.runner import BenchmarkRunner  # noqa: E402


MANIFEST = ROOT / "benchmark/spe_v1/dataset_manifest.json"
V2_MANIFEST = ROOT / "benchmark/spe_v2/dataset_manifest.json"


class FakeBackend:
    def __init__(self, energy: float = -76.39913535162846):
        self.energy = energy
        self.requests = []

    def execute(self, request, *, timeout_seconds):
        self.requests.append(request)
        if request.settings["max_cycles"] == 1:
            return {
                "status": "failed",
                "wall_seconds": 0.01,
                "failure_class": "non_convergence",
                "failure_message": "SCF iteration limit reached",
                "retryable": True,
            }
        return {
            "status": "completed",
            "wall_seconds": 0.02,
            "engine_seconds": 0.01,
            "job_id": f"fake-{len(self.requests)}",
            "energy_hartree": self.energy,
            "converged": True,
            "artifacts": [],
        }


class StaticProvider:
    def __init__(self, response):
        self.response = response
        self.payloads = []

    def request(self, payload):
        self.payloads.append(payload)
        return dict(self.response)


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(MANIFEST, ROOT)
        cls.references = ReferenceStore(cls.dataset.reference_store_path)

    def case(self, case_id):
        return next(item for item in self.dataset.cases if item.case_id == case_id)

    def test_dataset_is_frozen_and_has_development_heldout_and_failure_cases(self):
        self.assertEqual(len(self.dataset.cases), 12)
        self.assertTrue(self.dataset.manifest_sha256)
        self.assertTrue(self.dataset.reference_store_sha256)
        self.assertEqual({item.split for item in self.dataset.cases}, set(Split))
        self.assertEqual(
            {item.expectation for item in self.dataset.cases},
            {CaseExpectation.VALID, CaseExpectation.RECOVERABLE, CaseExpectation.INVALID},
        )

    def test_v1_frozen_integrity_manifest_matches_preserved_baseline(self):
        freeze = json.loads(
            (ROOT / "benchmark/spe_v1/FROZEN_INTEGRITY.json").read_text(encoding="utf-8")
        )
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_reference_answers_are_absent_from_policy_payload(self):
        payload = self.case("dev-water-clean").public_payload()
        self.assertNotIn("reference_id", payload)
        self.assertNotIn("energy_hartree", payload)
        self.assertNotIn("tolerance_hartree", payload)

    def test_structure_hash_mutation_is_rejected(self):
        original = MANIFEST.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "manifest.json"
            path.write_text(original.replace("cfcb068b", "ffffffff", 1), encoding="utf-8")
            with self.assertRaisesRegex(DatasetError, "structure hash mismatch"):
                load_dataset(path, ROOT)

    def test_fixed_workflow_recovers_nonconvergence_with_one_changed_retry(self):
        backend = FakeBackend()
        runner = BenchmarkRunner(backend, self.dataset.budget)
        run = runner.run_case(self.case("dev-water-low-scf-budget"), FixedWorkflowPolicy())
        self.assertEqual(run.status, RunStatus.COMPLETED)
        self.assertTrue(run.recovered)
        self.assertEqual(run.tool_call_count, 2)
        self.assertEqual(backend.requests[0].settings["max_cycles"], 1)
        self.assertEqual(backend.requests[1].settings["max_cycles"], 200)

    def test_invalid_input_is_rejected_without_backend_call(self):
        backend = FakeBackend()
        run = BenchmarkRunner(backend, self.dataset.budget).run_case(
            self.case("dev-water-invalid-spin"), FixedWorkflowPolicy()
        )
        self.assertEqual(run.status, RunStatus.REJECTED)
        self.assertEqual(run.tool_call_count, 0)
        self.assertFalse(backend.requests)

    def test_agent_cannot_repeat_identical_failed_action(self):
        provider = StaticProvider(
            {
                "action": "retry",
                "settings": {"max_cycles": 1, "conv_tol": 1e-9, "use_gpu": True},
                "reason": "repeat",
                "evidence": ["non-convergence"],
            }
        )
        run = BenchmarkRunner(FakeBackend(), self.dataset.budget).run_case(
            self.case("dev-water-low-scf-budget"), AgentScientistPolicy(provider)
        )
        self.assertEqual(run.status, RunStatus.PROTOCOL_VIOLATION)
        self.assertIn("repeated identical settings", run.protocol_violations[0])

    def test_specialist_path_delegates_then_requires_controller_review(self):
        provider = StaticProvider(
            {
                "action": "retry",
                "settings": {"max_cycles": 200, "conv_tol": 1e-9, "use_gpu": True},
                "reason": "increase bounded SCF cycles",
                "evidence": ["SCF iteration limit"],
            }
        )
        run = BenchmarkRunner(FakeBackend(), self.dataset.budget).run_case(
            self.case("dev-water-low-scf-budget"), SpecialistAssistedPolicy(provider)
        )
        self.assertEqual(run.status, RunStatus.COMPLETED)
        self.assertEqual(len(provider.payloads), 2)
        self.assertEqual(provider.payloads[0]["role"], "spe-specialist")
        self.assertEqual(provider.payloads[1]["role"], "general-controller-review")
        self.assertIn("specialist_recommendation", provider.payloads[1])

    def test_evaluator_aggregates_agent_usage_without_counting_backend_calls(self):
        provider = StaticProvider(
            {
                "action": "retry",
                "settings": {"max_cycles": 50, "conv_tol": 1e-9, "use_gpu": True},
                "reason": "bounded SCF recovery",
                "evidence": ["non-convergence after one cycle"],
                "agent_scientist_usage": {
                    "total_including_auxiliary": {
                        "api_calls": 2,
                        "total_tokens": 1234,
                        "estimated_cost_usd": 0.125,
                    }
                },
            }
        )
        run = BenchmarkRunner(FakeBackend(), self.dataset.budget).run_case(
            self.case("dev-water-low-scf-budget"), AgentScientistPolicy(provider)
        )
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [run], {run.case_id: "water-b3lyp-631gd-recoverable"}
        )
        metrics = bundle.metrics[Approach.AGENT.value]
        self.assertEqual(metrics["tool_call_count"], 2)
        self.assertEqual(metrics["decision_call_count"], 1)
        self.assertEqual(metrics["agent_api_call_count"], 2)
        self.assertEqual(metrics["agent_total_tokens"], 1234)
        self.assertEqual(metrics["agent_reported_estimated_cost_usd"], 0.125)

    def test_evaluator_uses_hidden_reference_and_rejects_wrong_energy(self):
        runner = BenchmarkRunner(FakeBackend(energy=-70.0), self.dataset.budget)
        run = runner.run_case(self.case("dev-water-clean"), FixedWorkflowPolicy())
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [run], {run.case_id: "water-b3lyp-631gd"}
        )
        self.assertFalse(bundle.cases[0].passed)
        self.assertGreater(bundle.cases[0].reference_error_hartree, 1.0)
        self.assertEqual(bundle.metrics[Approach.FIXED.value]["valid_completion_rate"], 1.0)

    def test_invalid_case_scores_as_correct_only_with_zero_tool_calls(self):
        run = BenchmarkRunner(FakeBackend(), self.dataset.budget).run_case(
            self.case("dev-missing-structure"), FixedWorkflowPolicy()
        )
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [run], {run.case_id: "invalid-input"}
        )
        self.assertTrue(bundle.cases[0].passed)
        self.assertEqual(bundle.metrics[Approach.FIXED.value]["input_validation_accuracy"], 1.0)


class BenchmarkV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(V2_MANIFEST, ROOT)
        cls.references = ReferenceStore(cls.dataset.reference_store_path)

    def case(self, case_id):
        return next(item for item in self.dataset.cases if item.case_id == case_id)

    def runner(self, backend):
        return BenchmarkRunner(
            backend,
            self.dataset.budget,
            supported_methods=self.dataset.permitted_methods,
            supported_basis_sets=self.dataset.permitted_basis_sets,
        )

    def test_v2_fault_schedule_and_reference_answer_are_hidden(self):
        payload = self.case("v2-heldout-gpu-execution-failure").public_payload()
        self.assertNotIn("fault_rules", payload)
        self.assertNotIn("reference_id", payload)
        self.assertNotIn("specialist_context", payload)
        specialist_payload = self.case(
            "v2-heldout-gpu-execution-failure"
        ).public_payload(include_specialist_context=True)
        self.assertEqual(specialist_payload["specialist_context"]["environment_id"], "20")

    def test_v2_unsupported_method_is_rejected_before_backend(self):
        backend = FakeBackend()
        run = self.runner(backend).run_case(
            self.case("v2-heldout-unsupported-method"), FixedWorkflowPolicy()
        )
        self.assertEqual(run.status, RunStatus.REJECTED)
        self.assertEqual(run.tool_call_count, 0)
        self.assertIn("unsupported method", run.preflight_findings[0])
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [run], {run.case_id: "v2-unsupported-method"}
        )
        self.assertTrue(bundle.cases[0].passed)

    def test_v2_fixed_timeout_rule_switches_to_cpu_and_recovers(self):
        backend = FakeBackend(-76.39913535146792)
        run = self.runner(backend).run_case(
            self.case("v2-heldout-interrupted-gpu"), FixedWorkflowPolicy()
        )
        self.assertEqual(run.status, RunStatus.COMPLETED)
        self.assertTrue(run.attempts[0].synthetic_fault)
        self.assertFalse(run.attempts[1].settings["use_gpu"])
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [run], {run.case_id: "v2-water-cpu-interruption-recovery"}
        )
        self.assertTrue(bundle.cases[0].passed)

    def test_v2_adaptive_gpu_failure_recovers_but_fixed_policy_stops(self):
        case = self.case("v2-heldout-gpu-execution-failure")
        fixed = self.runner(FakeBackend(-40.51762601931546)).run_case(
            case, FixedWorkflowPolicy()
        )
        provider = StaticProvider(
            {
                "action": "retry",
                "settings": {"max_cycles": 200, "conv_tol": 1e-9, "use_gpu": False},
                "reason": "use the available CPU backend after GPU allocation failure",
                "evidence": ["failure occurred before SCF initialization"],
            }
        )
        adaptive = self.runner(FakeBackend(-40.51762601931546)).run_case(
            case, AgentScientistPolicy(provider)
        )
        self.assertEqual(fixed.status, RunStatus.FAILED)
        self.assertEqual(adaptive.status, RunStatus.COMPLETED)
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [fixed, adaptive], {case.case_id: "v2-methane-cpu-gpu-recovery"}
        )
        self.assertFalse(bundle.cases[0].passed)
        self.assertTrue(bundle.cases[1].passed)

    def test_v2_nonretryable_parse_error_is_scored_as_safe_failure(self):
        provider = StaticProvider(
            {
                "action": "stop",
                "settings": {},
                "reason": "output has no verifiable energy and is non-retryable",
                "evidence": ["output_parse_error"],
            }
        )
        case = self.case("v2-heldout-output-parse-failure")
        run = self.runner(FakeBackend()).run_case(case, AgentScientistPolicy(provider))
        bundle = BenchmarkEvaluator(self.references).evaluate(
            [run], {case.case_id: "v2-output-parse-safe-failure"}
        )
        self.assertEqual(run.status, RunStatus.FAILED)
        self.assertTrue(bundle.cases[0].passed)
        self.assertEqual(
            bundle.metrics[Approach.AGENT.value]["safe_failure_handling_rate"], 1.0
        )

    def test_independent_accuracy_track_is_separate_and_hash_verified(self):
        manifest = ROOT / "benchmark/spe_v2/accuracy_track.json"
        record = validate_accuracy_track(manifest, ROOT)
        self.assertFalse(record["included_in_primary_reliability_gate"])
        self.assertEqual(record["status"], "review")
        self.assertFalse(record["comparison"]["energy_agreement_pass"])

    def test_v2_protocol_freeze_matches_scored_inputs_and_policies(self):
        freeze = json.loads(
            (ROOT / "benchmark/spe_v2/PROTOCOL_FREEZE.json").read_text(encoding="utf-8")
        )
        for relative, expected in freeze["sha256"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_accuracy_track_rejects_changed_threshold_outcome(self):
        source = json.loads(
            (ROOT / "benchmark/spe_v2/accuracy_track.json").read_text(encoding="utf-8")
        )
        source["status"] = "pass"
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "accuracy.json"
            manifest.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(AccuracyTrackError, "status conflicts"):
                validate_accuracy_track(manifest, ROOT)


if __name__ == "__main__":
    unittest.main()
