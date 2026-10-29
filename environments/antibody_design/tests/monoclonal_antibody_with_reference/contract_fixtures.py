"""Behavior tests use clearly marked synthetic fixtures; they are not antibody evidence."""
from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from . import validation


class ContractFixture:
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
