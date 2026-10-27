"""Behavior tests use clearly marked synthetic fixtures; they are not antibody evidence."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import validation


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="antibody-contract-test-")
        self.root = Path(self.temp.name)
        self.artifact_root = self.root / "protocol-evidence"
        self.artifact_root.mkdir()
        self._write(self.artifact_root / "qualification.json", "synthetic qualification fixture")
        self._write(self.artifact_root / "adapter.json", "synthetic adapter fixture")
        self._write(self.artifact_root / "weights.bin", "synthetic weights fixture")
        self._write(self.artifact_root / "dataset.json", "synthetic dataset fixture")
        self.protocol = self._protocol()
        self._save_protocol_and_request()

    def tearDown(self):
        self.temp.cleanup()

    def _write(self, path, contents):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path

    def _artifact(self, path, base=None):
        path = Path(path)
        base = Path(base) if base is not None else self.root
        return {"path": path.relative_to(base).as_posix(), "sha256": validation.sha256(path)}

    def _protocol(self):
        config = validation.yaml.safe_load((ROOT / "config/environment.yaml").read_text())
        groups = list(config["required_rule_groups"]) + ["dynamics"]
        metric_ids = {"identity": "paired_chain_integrity", "framework": "framework_identity_fraction",
                      "fold": "plddt", "developability": "cdr_surface_hydrophobicity", "interface": "iptm", "binding": "prodigy_binding_energy",
                      "stability": "stabddg_delta_delta_g", "aggregation": "aggregation_risk_score",
                      "solubility": "solubility_prediction", "expression": "expression_prediction",
                      "polyreactivity": "polyreactivity_prediction", "immunogenicity": "immunogenicity_prediction",
                      "dynamics": "interface_contact_persistence"}
        rules, ranking = [], []
        for group in groups:
            rule_id = f"{group}_score"
            rules.append({"rule_id": rule_id, "group": group, "required": True,
                          "metric_id": metric_ids[group], "units": "fixture_score", "scale": "synthetic 0-1",
                          "scope": "antigen_antibody" if group in {"interface", "binding", "dynamics"} else "antibody",
                          "method_id": "fixture_method", "operator": "ge", "threshold": 0.5})
            if group in {"interface", "fold"}:
                ranking.append(rule_id)
        return {"schema_version": "1.0", "protocol_id": "synthetic-test-protocol",
                "task_id": "denv_antibody_001", "status": "qualified",
                "evaluator_revision": "a" * 64, "knowledge_cutoff": "2024-09-01",
                "rules": rules,
                "methods": [{"method_id": "fixture_method", "name": "Synthetic Test Fixture",
                             "capability": "contract_validation", "revision": "b" * 40,
                             "released_on": "2024-01-01", "availability_evidence": self._artifact(
                                 self.artifact_root / "adapter.json"), "adapter_verified": True,
                             "model_weights": [self._artifact(self.artifact_root / "weights.bin")],
                             "dataset_snapshots": [self._artifact(self.artifact_root / "dataset.json")]}],
                "qualification_evidence": [self._artifact(self.artifact_root / "qualification.json")],
                "ranking": {"ordered_rule_ids": ranking, "tie_break": "candidate_id_ascending"}}

    def _tool_specific_protocol(self):
        protocol = copy.deepcopy(self.protocol)
        common = {"revision": "c" * 40, "released_on": "2024-01-01",
                  "availability_evidence": self._artifact(self.artifact_root / "adapter.json"),
                  "adapter_verified": True,
                  "model_weights": [self._artifact(self.artifact_root / "weights.bin")],
                  "dataset_snapshots": [self._artifact(self.artifact_root / "dataset.json")]}
        protocol["methods"].extend([
            {"method_id": "stability_binding_ddg", "name": "Stability-Binding DDG",
             "capability": "stability_assessment", **common},
            {"method_id": "prodigy", "name": "PRODIGY",
             "capability": "binding_energy_estimation", **common},
            {"method_id": "ipsae", "name": "ipSAE",
             "capability": "interface_confidence", **common},
        ])
        mapping = {"stability": ("stability_binding_ddg", "stabddg_delta_delta_g"),
                   "binding": ("prodigy", "prodigy_binding_energy"),
                   "interface": ("ipsae", "ipsae")}
        for rule in protocol["rules"]:
            if rule["group"] in mapping:
                rule["method_id"], rule["metric_id"] = mapping[rule["group"]]
        return protocol

    def _preflight_variant(self, variant):
        protocol = copy.deepcopy(self.protocol if variant == "general" else self._tool_specific_protocol())
        protocol_path = self.root / f"protocol-{variant}.json"
        self._write(protocol_path, json.dumps(protocol, indent=2))
        request = self._request()
        request["variant"] = variant
        request["protocol"] = self._artifact(protocol_path)
        return request, protocol, validation.preflight(request, self.root)

    def _request(self):
        return {"schema_version": "1.0", "task_id": "denv_antibody_001", "variant": "general",
                "target": {"organism": "DENV-2", "protein": "envelope", "region": "EDIII",
                           "strain_id": "synthetic-fixture", "construct": {"name": "synthetic EDIII",
                           "residue_range": [1, 3], "presentation_context": "isolated_EDIII"},
                           "sequence": self._artifact(self._write(self.root / "inputs/antigen.fasta", ">fixture\nACDE\n")),
                           "structure": self._artifact(self._write(self.root / "inputs/antigen.pdb", "synthetic fixture\n")),
                           "chain_ids": ["A"], "residue_map": self._artifact(self._write(self.root / "inputs/residue-map.json", "{}"))},
                "reference": {"id": "DV87.1", "format": "VH_VL",
                              "sequences": self._artifact(self._write(self.root / "inputs/reference.fasta", ">H\nCDEF\n>L\nGHIK\n")),
                              "heavy_chain_id": "H", "light_chain_id": "L", "numbering_scheme": "IMGT",
                              "region_annotation": self._artifact(self._write(self.root / "inputs/regions.json", "{}"))},
                "input_candidates": None,
                "protocol": None,
                "constraints": {"preserve_framework": True, "preserve_chain_pairing": True,
                                "lengths_from_reference": True, "allowed_design_region": "annotated_CDRs",
                                "numbering_scheme": "IMGT"},
                "execution": {"final_count": 1, "max_candidates": 2, "seed": 1,
                              "dynamics_required": True,
                              "budget": {"wall_time_minutes": 120, "cpu_core_hours": 2,
                                         "gpu_hours": 2, "remote_cost_units": 0}},
                "knowledge_cutoff": "2024-09-01"}

    def _save_protocol_and_request(self):
        self.protocol_path = self.root / "protocol.json"
        self._write(self.protocol_path, json.dumps(self.protocol, indent=2))
        self.request = self._request()
        self.request["protocol"] = self._artifact(self.protocol_path)
        self.request_path = self.root / "request.json"
        self._write(self.request_path, json.dumps(self.request, indent=2))

    def _record(self, candidate_id, role, sequences, value=0.8, forced_state=None):
        digest = validation.sequence_hash(sequences)
        evidence_file = self.root / "bundle/evidence/metrics.json"
        self._write(evidence_file, "synthetic fixture; not molecular evidence")
        evidence = self._artifact(evidence_file, self.root / "bundle")
        rules = []
        for rule in self.protocol["rules"]:
            measured = 1.0 if rule["group"] in {"identity", "framework"} else value
            state = forced_state or validation._expected_state(measured, rule)
            rules.append({"rule_id": rule["rule_id"], "value": measured,
                          "state": state, "method_id": rule["method_id"], "units": rule["units"],
                          "scale": rule["scale"], "scope": rule["scope"],
                          "sequence_sha256": digest, "evidence": [evidence], "reason": None})
        return {"candidate_id": candidate_id, "role": role,
                "parent_id": None if role == "reference" else "DV87.1",
                "sequences": sequences, "sequence_sha256": digest, "rules": rules}

    def _bundle(self, *, status="QUALIFIED", candidate_value=0.8, forced_state=None):
        bundle = self.root / "bundle"
        bundle.mkdir(exist_ok=True)
        reference = self._record("DV87.1", "reference", {"heavy": "CDEF", "light": "GHIK"})
        candidate = self._record("candidate-1", "candidate", {"heavy": "ACDE", "light": "FGHI"},
                                 candidate_value, forced_state)
        shortlist = ["candidate-1"] if candidate_value >= 0.5 and forced_state is None else []
        metrics = {"schema_version": "1.0", "task_id": "denv_antibody_001", "variant": "general",
                   "run_id": "synthetic-run", "run_status": status, "requested_count": 1,
                   "stop_reason": "Synthetic validator fixture only.", "missing_requirements": [],
                   "records": [reference, candidate], "shortlist": shortlist,
                   "provenance": {"request_sha256": validation.sha256(self.request_path),
                                  "protocol_sha256": validation.sha256(self.protocol_path),
                                  "scientific_execution": True, "synthetic_fixture": True,
                                  "knowledge_cutoff": "2024-09-01"},
                   "resources": {"wall_time_minutes": 1, "cpu_core_hours": 0.5,
                                 "gpu_hours": 0.5, "remote_cost_units": 0}}
        self._write(bundle / "metrics.json", json.dumps(metrics, indent=2))
        fasta = ">candidate-1|H\nACDE\n>candidate-1|L\nFGHI\n" if shortlist else ""
        self._write(bundle / "designed_sequences.fasta", fasta)
        with (bundle / "shortlist.csv").open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["rank", "candidate_id", "sequence_sha256"])
            if shortlist:
                writer.writerow([1, "candidate-1", candidate["sequence_sha256"]])
        self._write(bundle / "report.md", "Synthetic contract test only; not scientific evidence.\n")
        return bundle

    def test_example_request_fails_closed_for_missing_biological_inputs(self):
        example = validation.read_json(ROOT / "tasks/request.example.json")
        result = validation.preflight(example, ROOT / "tasks")
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

    def test_method_neutral_task_does_not_name_documented_software(self):
        text = (ROOT / "tasks/denv_antibody_001.md").read_text().casefold()
        for name in ("stability-binding ddg", "stability-binding-ddg", "prodigy", "ipsae",
                     "stabddg", "boltz", "boltz2"):
            self.assertNotIn(name, text)


if __name__ == "__main__":
    unittest.main()
