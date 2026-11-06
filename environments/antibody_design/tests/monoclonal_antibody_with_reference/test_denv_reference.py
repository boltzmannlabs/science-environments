"""Behavior tests use clearly marked synthetic fixtures; they are not antibody evidence."""
from __future__ import annotations

import copy
import json
import unittest

from .contract_fixtures import ContractFixture, ROOT, validation


class ContractTests(ContractFixture, unittest.TestCase):
    def test_example_request_fails_closed_for_missing_biological_inputs(self):
        example = validation.read_json(ROOT / "config/monoclonal_reference/denv.request.example.json")
        result = validation.preflight(example, ROOT / "config/monoclonal_reference")
        self.assertEqual(result["status"], "NEEDS_INPUT")
        self.assertIn("target.construct", result["missing_requirements"])
        self.assertIn("reference.heavy_chain_id", result["missing_requirements"])

    def test_contract_ready_is_not_scientific_validation(self):
        result = validation.preflight(self.request, self.root)
        self.assertEqual(result["status"], "CONTRACT_READY")
        self.assertIn("remain unverified", result["scope"])

    def test_general_and_tool_specific_variants_share_scientific_preflight_contract(self):
        general_request, general_protocol, general_result = self._preflight_variant("general")
        tool_request, tool_protocol, tool_result = self._preflight_variant("tool_specific")
        self.assertEqual(general_result["status"], "CONTRACT_READY")
        self.assertEqual(tool_result["status"], "CONTRACT_READY")
        for field in ("target", "reference", "constraints", "execution", "knowledge_cutoff"):
            self.assertEqual(general_request[field], tool_request[field])
        general_groups = {rule["group"] for rule in general_protocol["rules"] if rule["required"]}
        tool_groups = {rule["group"] for rule in tool_protocol["rules"] if rule["required"]}
        self.assertEqual(general_groups, tool_groups)
        self.assertEqual(general_protocol["ranking"], tool_protocol["ranking"])

    def test_both_variants_fail_closed_on_the_same_missing_antigen_input(self):
        for variant in ("general", "tool_specific"):
            request, _, _ = self._preflight_variant(variant)
            request["target"]["sequence"] = None
            result = validation.preflight(request, self.root)
            self.assertEqual(result["status"], "NEEDS_INPUT")
            self.assertIn("target.sequence", result["missing_requirements"])

    def test_tool_specific_protocol_rejects_legacy_stabddg_name(self):
        request, protocol, _ = self._preflight_variant("tool_specific")
        method = next(item for item in protocol["methods"] if item["method_id"] == "stability_binding_ddg")
        method["name"] = "StabDDG"
        protocol_path = self.root / "legacy-name-protocol.json"
        self._write(protocol_path, json.dumps(protocol, indent=2))
        request["protocol"] = self._artifact(protocol_path)
        result = validation.preflight(request, self.root)
        self.assertEqual(result["status"], "PROTOCOL_REQUIRED")
        self.assertIn("Missing documented method: stability_assessment", result["missing_requirements"][0])

    def test_protocol_released_after_cutoff_is_rejected(self):
        self.protocol["methods"][0]["released_on"] = "2024-09-02"
        self._save_protocol_and_request()
        result = validation.preflight(self.request, self.root)
        self.assertEqual(result["status"], "PROTOCOL_REQUIRED")
        self.assertIn("newer than", result["missing_requirements"][0])

    def test_antigen_binding_rule_cannot_use_antibody_internal_scope(self):
        rule = next(r for r in self.protocol["rules"] if r["group"] == "interface")
        rule["scope"] = "antibody"
        self._save_protocol_and_request()
        with self.assertRaisesRegex(ValueError, "antigen-antibody scope"):
            validation.validate_protocol(self.protocol, self.request, self.root)

    def test_paired_bundle_contracts_agree(self):
        bundle = self._bundle()
        metrics = validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)
        self.assertEqual(metrics["run_status"], "QUALIFIED")
        self.assertEqual(metrics["shortlist"], ["candidate-1"])

    def test_synthetic_fixture_is_not_accepted_as_scientific_result(self):
        with self.assertRaisesRegex(ValueError, "Synthetic fixture"):
            validation.validate_bundle(self._bundle(), self.request_path, self.root)

    def test_pass_with_missing_numeric_value_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        metric = metrics["records"][1]["rules"][0]
        metric["value"], metric["state"] = None, "PASS"
        metric["reason"] = "missing value"
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "Incorrect rule decision"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_candidate_evidence_stale_after_sequence_change_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        metrics["records"][1]["sequences"]["heavy"] = "ACDF"
        metrics["records"][1]["sequence_sha256"] = validation.sequence_hash(metrics["records"][1]["sequences"])
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "Stale evidence"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_fasta_must_match_paired_shortlist(self):
        bundle = self._bundle()
        self._write(bundle / "designed_sequences.fasta", ">candidate-1|H\nACDE\n")
        with self.assertRaisesRegex(ValueError, "FASTA and shortlist disagree"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_declared_evidence_hash_is_checked(self):
        bundle = self._bundle()
        evidence = bundle / "evidence/metrics.json"
        evidence.write_text("changed after scoring")
        with self.assertRaisesRegex(ValueError, "Artifact hash mismatch"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_duplicate_paired_sequence_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        candidate = metrics["records"][1]
        candidate["sequences"] = copy.deepcopy(metrics["records"][0]["sequences"])
        candidate["sequence_sha256"] = validation.sequence_hash(candidate["sequences"])
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "Duplicate paired sequences"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_candidate_with_wrong_reference_lineage_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        metrics["records"][1]["parent_id"] = "unverified-parent"
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "reference lineage"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_resolved_metric_without_native_evidence_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        metrics["records"][1]["rules"][0]["evidence"] = []
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "Resolved metrics require artifacts"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_resource_budget_overrun_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        metrics["resources"]["wall_time_minutes"] = 121
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "Resource budget exceeded"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_binding_pass_cannot_compensate_for_developability_failure(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        candidate = metrics["records"][1]
        developability = next(rule for rule in candidate["rules"] if rule["rule_id"] == "developability_score")
        binding = next(rule for rule in candidate["rules"] if rule["rule_id"] == "binding_score")
        self.assertEqual(binding["state"], "PASS")
        developability["value"], developability["state"] = 0.1, "FAIL"
        metrics["run_status"] = "NO_QUALIFYING_DESIGNS"
        metrics["shortlist"] = []
        self._write(metrics_path, json.dumps(metrics))
        self._write(bundle / "designed_sequences.fasta", "")
        self._write(bundle / "shortlist.csv", "rank,candidate_id,sequence_sha256\n")
        result = validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)
        self.assertEqual(result["run_status"], "NO_QUALIFYING_DESIGNS")
        self.assertEqual(result["shortlist"], [])

    def test_unresolved_required_evidence_produces_incomplete_not_negative(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        candidate = metrics["records"][1]
        interface = next(rule for rule in candidate["rules"] if rule["rule_id"] == "interface_score")
        interface["value"], interface["state"] = None, "UNRESOLVED"
        interface["reason"] = "Synthetic missing interface evidence."
        interface["evidence"] = []
        metrics["run_status"] = "INCOMPLETE"
        metrics["shortlist"] = []
        self._write(metrics_path, json.dumps(metrics))
        self._write(bundle / "designed_sequences.fasta", "")
        self._write(bundle / "shortlist.csv", "rank,candidate_id,sequence_sha256\n")
        result = validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)
        self.assertEqual(result["run_status"], "INCOMPLETE")
        self.assertEqual(result["shortlist"], [])

    def test_candidate_count_above_budget_is_rejected(self):
        bundle = self._bundle()
        metrics_path = bundle / "metrics.json"
        metrics = json.loads(metrics_path.read_text())
        metrics["records"].append(self._record("candidate-2", "candidate",
                                               {"heavy": "LMNP", "light": "QRST"}))
        metrics["records"].append(self._record("candidate-3", "candidate",
                                               {"heavy": "VWYA", "light": "CDEF"}))
        self._write(metrics_path, json.dumps(metrics))
        with self.assertRaisesRegex(ValueError, "Candidate budget exceeded"):
            validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def test_zero_qualification_is_only_a_completed_negative_with_failures(self):
        bundle = self._bundle(status="NO_QUALIFYING_DESIGNS", candidate_value=0.1)
        result = validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)
        self.assertEqual(result["shortlist"], [])


if __name__ == "__main__":
    unittest.main()
