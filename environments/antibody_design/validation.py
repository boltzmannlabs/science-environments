#!/usr/bin/env python3
"""Validate benchmark contracts and local evidence integrity; no scientific execution."""
from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker, ValidationError
import yaml

ROOT = Path(__file__).resolve().parent
PREFLIGHT_STATUSES = {"NEEDS_INPUT", "PROTOCOL_REQUIRED", "BLOCKED"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    def invalid_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    return json.loads(Path(path).read_text(), object_pairs_hook=_unique_keys,
                      parse_constant=invalid_constant)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sequence_hash(sequences):
    """Canonical paired-chain content; no structural or biological interpretation."""
    return hashlib.sha256((sequences["heavy"] + "\n" + sequences["light"] + "\n").encode()).hexdigest()


def _read_protein_sequence_artifact(artifact, root):
    """Read one protein sequence from plain text or a single-record FASTA file."""
    path = artifact_path(artifact, root)
    entries, current = [], None
    for raw_line in path.read_text().splitlines():
        line = "".join(raw_line.split()).upper()
        if not line:
            continue
        if line.startswith(">"):
            require(current is None or current, "Empty FASTA sequence record")
            current = ""
            entries.append(current)
        else:
            if current is None:
                current = ""
                entries.append(current)
            entries[-1] += line
    require(len(entries) == 1, f"Expected one protein sequence in {artifact['path']}")
    sequence = entries[0]
    require(re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", sequence) is not None,
            f"Invalid protein sequence artifact: {artifact['path']}")
    return sequence


def _finite(value):
    if isinstance(value, float):
        require(math.isfinite(value), "Non-finite numeric value")
    elif isinstance(value, dict):
        for item in value.values():
            _finite(item)
    elif isinstance(value, list):
        for item in value:
            _finite(item)


def validate_schema(value, name):
    _finite(value)
    schema = read_json(ROOT / "config" / f"{name}.schema.json")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def _artifact_entries(value):
    if isinstance(value, dict):
        if {"path", "sha256"} <= set(value):
            yield value
            return
        for child in value.values():
            yield from _artifact_entries(child)
    elif isinstance(value, list):
        for child in value:
            yield from _artifact_entries(child)


def artifact_path(artifact, root):
    root = Path(root).resolve()
    relative = Path(artifact["path"])
    require(not relative.is_absolute() and ".." not in relative.parts,
            "Artifact paths must stay beneath their declared root")
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "Artifact symlink escapes the declared root")
    require(path.is_file(), f"Missing artifact: {artifact['path']}")
    require(sha256(path) == artifact["sha256"], f"Artifact hash mismatch: {artifact['path']}")
    return path


REFERENCE_GUIDED_MODES = {
    "reference_guided", "affinity_maturation", "humanization",
    "developability_optimization", "specificity_optimization", "mechanism_optimization",
}


def validate_generic_request(request):
    validate_schema(request, "generic-antibody-request")
    mode = request["design_mode"]
    antibody = request["antibody"]
    reference = antibody["reference"]
    require((reference is not None) == (mode in REFERENCE_GUIDED_MODES),
            "Reference-guided design modes require a reference; de_novo must not supply one")
    require(request["evaluation"]["requested_count"] <= request["constraints"]["max_candidates"],
            "Requested count exceeds the candidate budget")
    if antibody["format"] == "full_length_IgG":
        require(bool(antibody["desired_isotype"]), "Full-length IgG requires a declared isotype")
        require(antibody["fc_policy"] != "not_applicable", "Full-length IgG requires an explicit Fc policy")
        require(antibody["sequence_scope"] in {"variable_domains", "full_length_chains"},
                "Full-length IgG requests must use variable-domain or full-length-chain sequence scope")
    else:
        require(antibody["fc_policy"] in {"not_applicable", "to_be_decided"},
                "Fc engineering is only valid when the declared antibody format contains an Fc")
        require(antibody["sequence_scope"] in {"variable_domains", "Fab_chains"},
                "Fab formats must use variable-domain or Fab-chain sequence scope")

    target = request["target"]
    construct_ids = [item["construct_id"] for item in target["constructs"]]
    require(len(construct_ids) == len(set(construct_ids)), "Duplicate target construct IDs")
    for construct in target["constructs"]:
        context = construct["presentation_context"]
        require(context != "unknown" or bool(construct.get("context_details")),
                "Unknown target presentation context requires an explanatory note")

    epitope = target["epitope_policy"]
    if epitope["mode"] == "defined_residues":
        require(bool(epitope["residues"]), "Defined-residue epitope policy requires residues")
    if epitope["mode"] == "defined_region":
        require(bool(epitope.get("region")), "Defined-region epitope policy requires a region")

    if reference is not None:
        heavy_id, light_id = reference.get("heavy_chain_id"), reference.get("light_chain_id")
        require(not heavy_id or not light_id or heavy_id != light_id,
                "Reference heavy and light chain IDs must differ")
        declared_numbering = request["constraints"].get("numbering_scheme")
        require(not declared_numbering or declared_numbering == reference["numbering_scheme"],
                "Reference and edit-mask numbering schemes must match")

    objective = request["objective"]
    if objective["mechanism"] != "binding_only":
        require(bool(objective.get("functional_assays")),
                "A functional mechanism requires at least one declared functional endpoint")
        require("function" in request["evaluation"]["required_evidence_domains"],
                "A functional mechanism requires function evidence")
    if mode == "specificity_optimization":
        panel = objective.get("cross_reactivity_panel")
        require(panel is not None, "Specificity optimization requires a frozen cross-reactivity panel")
        require("specificity" in request["evaluation"]["required_evidence_domains"],
                "Specificity optimization requires specificity evidence")
    if mode == "mechanism_optimization":
        require(objective["mechanism"] != "binding_only",
                "Mechanism optimization requires a functional mechanism")
        require(bool(objective.get("functional_assays")),
                "Mechanism optimization requires a declared functional endpoint")
        require("function" in request["evaluation"]["required_evidence_domains"],
                "Mechanism optimization requires function evidence")
    if mode == "de_novo":
        require(target.get("variant_panel") is not None or objective.get("cross_reactivity_panel") is not None,
                "Target-only discovery requires a declared specificity panel")

    required_by_mode = {
        "de_novo": {"identity", "structure", "interface", "binding", "specificity", "developability"},
        "reference_guided": {"identity", "framework", "structure", "interface", "binding", "developability"},
        "affinity_maturation": {"identity", "framework", "structure", "interface", "binding", "developability"},
        "humanization": {"identity", "framework", "structure", "binding", "developability", "immunogenicity"},
        "developability_optimization": {"identity", "framework", "binding", "developability"},
        "specificity_optimization": {"identity", "framework", "binding", "specificity", "developability"},
        "mechanism_optimization": {"identity", "framework", "binding", "function", "developability"},
    }
    declared = set(request["evaluation"]["required_evidence_domains"])
    require(required_by_mode[mode] <= declared,
            f"Request omits evidence domains for {mode}: {sorted(required_by_mode[mode] - declared)}")


def validate_generic_protocol(protocol, request, root):
    validate_schema(protocol, "protocol")
    require(protocol["status"] == "qualified", "A qualified protocol is required")
    require(protocol["task_id"] == request["task_id"], "Protocol task ID does not match the request")
    require(protocol["knowledge_cutoff"] == request["knowledge_cutoff"],
            "Protocol knowledge cutoff changed")

    config = yaml.safe_load((ROOT / "config/environment.yaml").read_text())
    group_map = config["generic_evidence_domain_groups"]
    required_groups = set()
    for domain in request["evaluation"]["required_evidence_domains"]:
        require(domain in group_map, f"No protocol rule-group mapping for evidence domain: {domain}")
        required_groups.update(group_map[domain])

    rules = {rule["rule_id"]: rule for rule in protocol["rules"]}
    require(len(rules) == len(protocol["rules"]), "Duplicate rule IDs")
    declared_groups = {rule["group"] for rule in rules.values() if rule["required"]}
    require(required_groups <= declared_groups,
            f"Protocol omits required evidence groups: {sorted(required_groups - declared_groups)}")

    catalog = read_json(ROOT / "config/metric-catalog.json")
    metric_catalog = {item["metric_id"]: item for item in catalog["metrics"]}
    methods = {method["method_id"]: method for method in protocol["methods"]}
    require(len(methods) == len(protocol["methods"]), "Duplicate method IDs")
    for rule in rules.values():
        require(rule["method_id"] in methods, "Rule references an unknown method")
        require(rule["metric_id"] in metric_catalog, "Protocol references an unknown antibody metric")
        if rule["group"] in {"interface", "binding", "function", "specificity"}:
            require(rule["scope"] == "antigen_antibody",
                    "Target recognition/function rules require antigen-antibody scope")
        metric = metric_catalog[rule["metric_id"]]
        require(metric["group"] == rule["group"] and metric["scope"] == rule["scope"],
                "Protocol metric group or scope contradicts the antibody metric catalog")
    require(protocol["qualification_evidence"], "Protocol has no qualification evidence")
    for artifact in protocol["qualification_evidence"]:
        artifact_path(artifact, root)
    for method in methods.values():
        require(method["adapter_verified"], "Protocol contains an unverified adapter")
        require(re.fullmatch(r"(?:[a-f0-9]{40}|sha256:[a-f0-9]{64})", method["revision"]),
                "Method revision must be a full commit or container digest")
        if request["knowledge_cutoff"]:
            require(date.fromisoformat(method["released_on"]) <= date.fromisoformat(request["knowledge_cutoff"]),
                    "Method release is newer than the knowledge cutoff")
        for artifact in [method["availability_evidence"], *method["model_weights"], *method["dataset_snapshots"]]:
            artifact_path(artifact, root)
    for rule_id in protocol["ranking"]["ordered_rule_ids"]:
        require(rule_id in rules and rules[rule_id]["required"] and rules[rule_id]["operator"] != "eq",
                "Ranking must refer to required ordered numeric rules")


def validate_request(request):
    if "design_mode" in request:
        validate_generic_request(request)
        return
    validate_schema(request, "request")
    execution = request["execution"]
    require(execution["final_count"] <= execution["max_candidates"],
            "Final count exceeds candidate budget")
    reference = request["reference"]
    heavy, light = reference["heavy_chain_id"], reference["light_chain_id"]
    if heavy is not None and light is not None:
        require(heavy != light, "Heavy and light chains must be distinct")
    require(not set(request["target"]["chain_ids"]) & {heavy, light},
            "Antigen and antibody chain assignments overlap")
    target_range = request["target"]["construct"]
    if target_range is not None:
        require(target_range["residue_range"][0] <= target_range["residue_range"][1],
                "Target construct residue range is reversed")


def validate_protocol(protocol, request, root):
    validate_schema(protocol, "protocol")
    require(protocol["status"] == "qualified", "A qualified protocol is required")
    require(protocol["task_id"] == request["task_id"], "Protocol task ID does not match the request")
    require(protocol["knowledge_cutoff"] == request["knowledge_cutoff"], "Knowledge cutoff changed")
    config = yaml.safe_load((ROOT / "config/environment.yaml").read_text())
    catalog = read_json(ROOT / "config/metric-catalog.json")
    metric_catalog = {item["metric_id"]: item for item in catalog["metrics"]}
    required_groups = set(config["required_rule_groups"])
    if request["execution"]["dynamics_required"]:
        required_groups.add("dynamics")
    rules = {rule["rule_id"]: rule for rule in protocol["rules"]}
    require(len(rules) == len(protocol["rules"]), "Duplicate rule IDs")
    require(required_groups <= {r["group"] for r in rules.values() if r["required"]},
            "Protocol omits a mandatory evidence group")
    methods = {method["method_id"]: method for method in protocol["methods"]}
    require(len(methods) == len(protocol["methods"]), "Duplicate method IDs")
    for rule in rules.values():
        require(rule["method_id"] in methods, "Rule references an unknown method")
        require(rule["metric_id"] in metric_catalog, "Protocol references an unknown antibody metric")
        if rule["group"] in {"interface", "binding"}:
            require(rule["scope"] == "antigen_antibody", "Target binding requires antigen-antibody scope")
        metric = metric_catalog[rule["metric_id"]]
        require(metric["group"] == rule["group"] and metric["scope"] == rule["scope"],
                "Protocol metric group or scope contradicts the antibody metric catalog")
    require(protocol["qualification_evidence"], "Protocol has no qualification evidence")
    for artifact in protocol["qualification_evidence"]:
        artifact_path(artifact, root)
    for method in methods.values():
        require(method["adapter_verified"], "Protocol contains an unverified adapter")
        require(re.fullmatch(r"(?:[a-f0-9]{40}|sha256:[a-f0-9]{64})", method["revision"]),
                "Method revision must be a full commit or container digest")
        if request["knowledge_cutoff"]:
            require(date.fromisoformat(method["released_on"]) <= date.fromisoformat(request["knowledge_cutoff"]),
                    "Method release is newer than the knowledge cutoff")
        for artifact in [method["availability_evidence"], *method["model_weights"], *method["dataset_snapshots"]]:
            artifact_path(artifact, root)
    if request["variant"] == "tool_specific":
        named = {(m["name"].casefold(), m["capability"]) for m in methods.values()}
        choices = [({"stability-binding ddg", "stability binding ddg"},
                    "stability_assessment", {"stabddg_delta_delta_g"}),
                   ({"prodigy"}, "binding_energy_estimation", {"prodigy_binding_energy"}),
                   ({"ipsae"}, "interface_confidence", {"ipsae"})]
        for names, capability, expected_metrics in choices:
            matched = {key for key, method in methods.items()
                       if method["name"].casefold() in names and method["capability"] == capability}
            require(matched, f"Missing documented method: {capability}")
            used_rule_metrics = {rule["metric_id"] for rule in rules.values() if rule["method_id"] in matched}
            require(expected_metrics <= used_rule_metrics,
                    f"Documented method lacks its required metric mapping: {capability}")
    for rule_id in protocol["ranking"]["ordered_rule_ids"]:
        require(rule_id in rules and rules[rule_id]["required"] and rules[rule_id]["operator"] != "eq",
                "Ranking must refer to required ordered numeric rules")


def preflight_generic(request, root):
    validate_generic_request(request)
    root = Path(root)
    protocol_ref = request["evaluation"]["protocol"]
    protocol_key = (protocol_ref["path"], protocol_ref["sha256"]) if protocol_ref else None
    missing_inputs = []
    validated_artifacts = set()
    for artifact in _artifact_entries(request):
        if protocol_key == (artifact["path"], artifact["sha256"]):
            continue
        try:
            artifact_path(artifact, root)
            validated_artifacts.add((artifact["path"], artifact["sha256"]))
        except (ValueError, KeyError, TypeError, OSError) as exc:
            missing_inputs.append(f"{artifact['path']}: {exc}")
    sequence_artifacts = [request["target"]["sequence"]]
    sequence_artifacts.extend(item["sequence"] for item in request["target"]["constructs"])
    if request["antibody"]["reference"] is not None:
        reference = request["antibody"]["reference"]
        sequence_artifacts.extend([reference["heavy_sequence"], reference["light_sequence"]])
    for artifact in sequence_artifacts:
        if (artifact["path"], artifact["sha256"]) not in validated_artifacts:
            continue
        try:
            _read_protein_sequence_artifact(artifact, root)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            missing_inputs.append(f"{artifact['path']}: {exc}")
    if missing_inputs:
        return {"status": "NEEDS_INPUT", "missing_requirements": missing_inputs}
    if protocol_ref is None:
        return {"status": "PROTOCOL_REQUIRED", "missing_requirements": ["evaluation.protocol"]}
    try:
        protocol_path = artifact_path(protocol_ref, root)
        protocol = read_json(protocol_path)
        validate_generic_protocol(protocol, request, root)
    except (ValueError, KeyError, TypeError, OSError, ValidationError, json.JSONDecodeError) as exc:
        return {"status": "PROTOCOL_REQUIRED", "missing_requirements": [str(exc)]}
    return {"status": "CONTRACT_READY", "missing_requirements": [],
            "scope": "Target-agnostic mAb contract checks only; scientific execution and biological identity remain unverified."}


def preflight(request, root):
    if "design_mode" in request:
        return preflight_generic(request, root)
    validate_request(request)
    missing = []
    required_fields = {"target": ["strain_id", "construct", "sequence", "structure", "chain_ids", "residue_map"],
                       "reference": ["format", "sequences", "heavy_chain_id", "light_chain_id",
                                     "numbering_scheme", "region_annotation"]}
    artifact_fields = {"target": {"sequence", "structure", "residue_map"},
                       "reference": {"sequences", "region_annotation"}}
    for section, fields in required_fields.items():
        for field in fields:
            value = request[section][field]
            if not value:
                missing.append(f"{section}.{field}")
            elif field in artifact_fields[section]:
                try:
                    artifact_path(value, root)
                except (ValueError, KeyError, TypeError) as exc:
                    missing.append(f"{section}.{field}: {exc}")
    if request["input_candidates"]:
        try:
            artifact_path(request["input_candidates"], root)
        except ValueError as exc:
            missing.append(f"input_candidates: {exc}")
    if request["protocol"] is None:
        missing.append("protocol")
    if missing:
        return {"status": "NEEDS_INPUT", "missing_requirements": missing}
    if request["protocol"] is None:
        return {"status": "PROTOCOL_REQUIRED", "missing_requirements": ["protocol"]}
    try:
        protocol = read_json(artifact_path(request["protocol"], root))
        validate_protocol(protocol, request, root)
    except (ValueError, ValidationError, OSError, json.JSONDecodeError) as exc:
        return {"status": "PROTOCOL_REQUIRED", "missing_requirements": [str(exc)]}
    return {"status": "CONTRACT_READY", "missing_requirements": [],
            "scope": "Contract checks only; biological identity and scientific execution remain unverified."}


def _expected_state(value, rule):
    if value is None:
        return "UNRESOLVED"
    threshold = rule["threshold"]
    passed = {"ge": value >= threshold, "le": value <= threshold, "eq": value == threshold}[rule["operator"]]
    return "PASS" if passed else "FAIL"


def _validate_records(metrics, protocol, bundle, *, reference_id="DV87.1", reference_required=True):
    rules = {r["rule_id"]: r for r in protocol["rules"]}
    records, pairs = {}, set()
    for record in metrics["records"]:
        candidate_id = record["candidate_id"]
        require(candidate_id not in records, "Duplicate candidate ID")
        records[candidate_id] = record
        digest = sequence_hash(record["sequences"])
        require(digest == record["sequence_sha256"], "Paired sequence hash mismatch")
        require(digest not in pairs, "Duplicate paired sequences")
        pairs.add(digest)
        values = {v["rule_id"]: v for v in record["rules"]}
        require(len(values) == len(record["rules"]) and set(values) == set(rules), "Rule coverage mismatch")
        for key, value in values.items():
            rule = rules[key]
            require(value["sequence_sha256"] == digest, "Stale evidence belongs to another sequence")
            for field in ("units", "scale", "scope", "method_id"):
                require(value[field] == rule[field], f"Metric {field} mismatch")
            require(value["state"] == _expected_state(value["value"], rule), "Incorrect rule decision")
            if value["value"] is None:
                require(value["reason"], "Unresolved evidence needs a reason")
            else:
                require(value["evidence"], "Resolved metrics require artifacts")
            for artifact in value["evidence"]:
                artifact_path(artifact, bundle)
    references = [r for r in records.values() if r["role"] == "reference"]
    candidates = [r for r in records.values() if r["role"] == "candidate"]
    if reference_required:
        require(len(references) == 1 and references[0]["candidate_id"] == reference_id,
                "Exactly one declared reference record is required")
        require(references[0]["parent_id"] is None, "Reference cannot have a candidate parent")
        require(all(r["parent_id"] == reference_id for r in candidates),
                "Candidate reference lineage is invalid")
    else:
        require(not references, "A de novo task cannot introduce an undeclared reference record")
        candidate_ids = {r["candidate_id"] for r in candidates}
        require(all(r["parent_id"] is None or
                    (r["parent_id"] in candidate_ids and r["parent_id"] != r["candidate_id"])
                    for r in candidates),
                "De novo candidate lineage references an unknown candidate")
        parents = {r["candidate_id"]: r["parent_id"] for r in candidates}
        for candidate_id in parents:
            lineage, current = set(), candidate_id
            while current is not None:
                require(current not in lineage, "De novo candidate lineage contains a cycle")
                lineage.add(current)
                current = parents.get(current)
    required_ids = {key for key, rule in rules.items() if rule["required"]}
    eligible = [r for r in candidates if all(v["state"] == "PASS" for v in r["rules"] if v["rule_id"] in required_ids)]
    if eligible and reference_required:
        require(all(v["state"] != "UNRESOLVED" for v in references[0]["rules"] if v["rule_id"] in required_ids),
                "Reference evidence is incomplete")
    def order(record):
        values = {v["rule_id"]: v["value"] for v in record["rules"]}
        return tuple((-values[key] if rules[key]["operator"] == "ge" else values[key])
                     for key in protocol["ranking"]["ordered_rule_ids"]) + (record["candidate_id"],)
    return records, candidates, sorted(eligible, key=order), required_ids


def _read_fasta(path):
    records, key = {}, None
    for line in path.read_text().splitlines():
        if not line:
            continue
        if line.startswith(">"):
            key = line[1:]
            require(key not in records, "Duplicate FASTA header")
            records[key] = ""
        else:
            require(key is not None and re.fullmatch("[ACDEFGHIKLMNPQRSTVWY]+", line), "Invalid FASTA content")
            records[key] += line
    return records


def validate_bundle(bundle, request_path, input_root=None, *, allow_synthetic=False):
    bundle, request_path = Path(bundle), Path(request_path)
    input_root = Path(input_root) if input_root is not None else request_path.parent
    request = read_json(request_path)
    if "design_mode" in request:
        return validate_generic_bundle(bundle, request_path, input_root, allow_synthetic=allow_synthetic,
                                       request=request)
    metrics = read_json(bundle / "metrics.json")
    validate_request(request)
    validate_schema(metrics, "metrics")
    require(not metrics["provenance"]["synthetic_fixture"] or allow_synthetic, "Synthetic fixture is not a scientific result")
    for key in ("task_id", "variant"):
        require(metrics[key] == request[key], f"Result {key} mismatch")
    require(metrics["requested_count"] == request["execution"]["final_count"], "Requested count changed")
    require(metrics["provenance"]["request_sha256"] == sha256(request_path), "Request hash mismatch")
    require(metrics["provenance"]["knowledge_cutoff"] == request["knowledge_cutoff"], "Result cutoff changed")
    for key, value in metrics["resources"].items():
        require(value <= request["execution"]["budget"][key], f"Resource budget exceeded: {key}")
    status = metrics["run_status"]
    if status in PREFLIGHT_STATUSES:
        require(not metrics["records"] and not metrics["shortlist"], "Preflight failure cannot claim candidate results")
        require(metrics["missing_requirements"], "Preflight failure needs missing requirements")
        require(not metrics["provenance"]["scientific_execution"], "Preflight failure cannot claim scientific execution")
        if status in {"NEEDS_INPUT", "PROTOCOL_REQUIRED"}:
            require(preflight(request, input_root)["status"] == status, "Preflight result contradicts request")
        return metrics
    require(preflight(request, input_root)["status"] == "CONTRACT_READY", "Run inputs/protocol are not contract-ready")
    protocol_path = artifact_path(request["protocol"], input_root)
    protocol = read_json(protocol_path)
    require(metrics["provenance"]["protocol_sha256"] == sha256(protocol_path), "Protocol hash mismatch")
    require(metrics["provenance"]["scientific_execution"], "Scientific result must declare execution")
    require(not metrics["missing_requirements"], "Run results cannot hide missing preflight requirements")
    records, candidates, eligible, required_ids = _validate_records(metrics, protocol, bundle)
    require(len(candidates) <= request["execution"]["max_candidates"], "Candidate budget exceeded")
    expected = [r["candidate_id"] for r in eligible[:metrics["requested_count"]]]
    require(metrics["shortlist"] == expected, "Shortlist contradicts eligibility or frozen ranking")
    count = len(expected)
    if status not in {"CANCELLED", "INCOMPLETE"}:
        expected_status = "QUALIFIED" if count == metrics["requested_count"] else "PARTIAL" if count else "NO_QUALIFYING_DESIGNS"
        require(status == expected_status, "Run status contradicts qualifying count")
    if status == "NO_QUALIFYING_DESIGNS":
        require(candidates and all(any(v["state"] == "FAIL" for v in r["rules"] if v["rule_id"] in required_ids)
                                   for r in candidates), "Unresolved/empty work is not a completed negative result")
    if status == "INCOMPLETE":
        require(count == 0, "An incomplete zero-qualification status cannot contain a shortlist")
    fasta = {f"{key}|{chain}": records[key]["sequences"][field] for key in expected
             for chain, field in (("H", "heavy"), ("L", "light"))}
    require(_read_fasta(bundle / "designed_sequences.fasta") == fasta, "FASTA and shortlist disagree")
    with (bundle / "shortlist.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == ["rank", "candidate_id", "sequence_sha256"], "CSV header mismatch")
        rows = list(reader)
    expected_rows = [{"rank": str(i), "candidate_id": key, "sequence_sha256": records[key]["sequence_sha256"]}
                     for i, key in enumerate(expected, 1)]
    require(rows == expected_rows, "CSV and shortlist disagree")
    require((bundle / "report.md").read_text().strip(), "Human-readable report is empty")
    return metrics


def validate_assay_record(record_path, root):
    record_path = Path(record_path)
    record = read_json(record_path)
    validate_schema(record, "mab-assay-record")
    _finite(record)
    for artifact in _artifact_entries(record):
        artifact_path(artifact, root)
    state = record["result_state"]
    if state == "interval":
        require(record["lower_bound"] <= record["upper_bound"],
                "Assay interval lower bound exceeds upper bound")
    elif state == "below_limit":
        require(record["upper_bound"] is not None, "Below-limit result requires an upper bound")
    elif state == "above_limit":
        require(record["lower_bound"] is not None, "Above-limit result requires a lower bound")
    elif state in {"not_measured", "uninterpretable"}:
        require(bool(record.get("reason")), "Unmeasured or uninterpretable assay record requires a reason")
    uncertainty = record.get("uncertainty")
    if uncertainty is not None:
        if uncertainty["kind"] in {"confidence_interval", "credible_interval", "range"}:
            require(uncertainty["lower_bound"] is not None and uncertainty["upper_bound"] is not None,
                    "Interval uncertainty requires lower and upper bounds")
            require(uncertainty["lower_bound"] <= uncertainty["upper_bound"],
                    "Uncertainty lower bound exceeds upper bound")
        elif uncertainty["kind"] in {"standard_deviation", "standard_error"}:
            require(uncertainty["value"] is not None and uncertainty["value"] >= 0,
                    "Standard deviation/error must be a nonnegative value")
    control_ids = [item["control_id"] for item in record["controls"]]
    require(len(control_ids) == len(set(control_ids)), "Duplicate assay control IDs")
    return record


def validate_generic_bundle(bundle, request_path, input_root=None, *, allow_synthetic=False, request=None):
    bundle, request_path = Path(bundle), Path(request_path)
    input_root = Path(input_root) if input_root is not None else request_path.parent
    request = request if request is not None else read_json(request_path)
    metrics = read_json(bundle / "metrics.json")
    validate_generic_request(request)
    validate_schema(metrics, "generic-antibody-metrics")
    require(not metrics["provenance"]["synthetic_fixture"] or allow_synthetic,
            "Synthetic fixture is not a scientific result")
    require(metrics["task_id"] == request["task_id"], "Result task ID mismatch")
    require(metrics["design_mode"] == request["design_mode"], "Result design mode mismatch")
    require(metrics["sequence_scope"] == request["antibody"]["sequence_scope"],
            "Result sequence scope differs from the frozen request")
    require(metrics["requested_count"] == request["evaluation"]["requested_count"],
            "Requested count changed")
    require(metrics["provenance"]["request_sha256"] == sha256(request_path), "Request hash mismatch")
    require(metrics["provenance"]["knowledge_cutoff"] == request["knowledge_cutoff"],
            "Result cutoff changed")
    if metrics["provenance"]["scientific_execution"]:
        agent_run = metrics["provenance"].get("agent_run")
        require(agent_run is not None, "Computational runs must record model, harness, tools, and workspace provenance")
        require(agent_run["random_seed"] == request["evaluation"]["seed"],
                "Agent run seed differs from the frozen request")
        require(agent_run["workspace_isolated"], "Benchmark runs require an isolated workspace")

    budget = request["budget"]
    resource_limits = {
        "wall_time_minutes": budget["wall_time_minutes"],
        "cpu_core_hours": budget["cpu_hours"],
        "gpu_hours": budget["gpu_hours"],
    }
    for key, limit in resource_limits.items():
        require(metrics["resources"][key] <= limit, f"Resource budget exceeded: {key}")
    cost_limit = budget.get("remote_cost_limit")
    if cost_limit is not None:
        require(metrics["resources"]["remote_cost_units"] <= cost_limit,
                "Remote cost budget exceeded")

    status = metrics["run_status"]
    preflight_result = preflight_generic(request, input_root)
    if status in PREFLIGHT_STATUSES:
        require(not metrics["records"] and not metrics["shortlist"] and not metrics["assay_records"],
                "Preflight failure cannot claim candidate or assay results")
        require(metrics["missing_requirements"], "Preflight failure needs missing requirements")
        require(not metrics["provenance"]["scientific_execution"],
                "Preflight failure cannot claim scientific execution")
        if status in {"NEEDS_INPUT", "PROTOCOL_REQUIRED"}:
            require(preflight_result["status"] == status,
                    "Preflight result contradicts the request")
        return metrics

    require(preflight_result["status"] == "CONTRACT_READY",
            "Run inputs/protocol are not contract-ready")
    protocol_path = artifact_path(request["evaluation"]["protocol"], input_root)
    protocol = read_json(protocol_path)
    validate_generic_protocol(protocol, request, input_root)
    require(metrics["provenance"]["protocol_sha256"] == sha256(protocol_path),
            "Protocol hash mismatch")
    require(metrics["provenance"]["scientific_execution"],
            "Scientific result must declare computational execution")
    require(not metrics["missing_requirements"],
            "Run results cannot hide missing preflight requirements")

    reference = request["antibody"]["reference"]
    reference_id = reference["antibody_id"] if reference else None
    records, candidates, eligible, required_ids = _validate_records(
        metrics, protocol, bundle, reference_id=reference_id,
        reference_required=reference is not None)
    if reference is not None:
        reference_record = records[reference_id]
        require(reference_record["sequences"]["heavy"] ==
                _read_protein_sequence_artifact(reference["heavy_sequence"], input_root),
                "Reference heavy-chain sequence differs from the supplied reference artifact")
        require(reference_record["sequences"]["light"] ==
                _read_protein_sequence_artifact(reference["light_sequence"], input_root),
                "Reference light-chain sequence differs from the supplied reference artifact")
    require(len(candidates) <= request["constraints"]["max_candidates"],
            "Candidate budget exceeded")
    expected = [r["candidate_id"] for r in eligible[:metrics["requested_count"]]]
    require(metrics["shortlist"] == expected,
            "Shortlist contradicts eligibility or frozen ranking")

    target_constructs = {item["construct_id"]: item for item in request["target"]["constructs"]}
    assay_ids, assay_pairs = set(), set()
    for assay_ref in metrics["assay_records"]:
        require(assay_ref["record_id"] not in assay_ids, "Duplicate assay record ID")
        assay_ids.add(assay_ref["record_id"])
        require(assay_ref["candidate_id"] in records,
                "Assay record references an unknown candidate or reference")
        path = artifact_path(assay_ref, bundle)
        assay = validate_assay_record(path, bundle)
        require(sha256(path) == assay_ref["sha256"], "Assay record hash mismatch")
        require(assay["record_id"] == assay_ref["record_id"], "Assay record ID mismatch")
        require(assay["candidate_id"] == assay_ref["candidate_id"], "Assay candidate ID mismatch")
        require(assay["candidate_sequence_sha256"] == records[assay["candidate_id"]]["sequence_sha256"],
                "Assay evidence belongs to a different antibody sequence")
        require(assay["target_construct_id"] in target_constructs,
                "Assay evidence references an undeclared target construct")
        require(assay["target_sequence_sha256"] == target_constructs[assay["target_construct_id"]]["sequence"]["sha256"],
                "Assay evidence target construct hash mismatch")
        pair = (assay["candidate_id"], assay["endpoint"], assay["target_construct_id"])
        require(pair not in assay_pairs, "Duplicate assay endpoint for candidate and construct")
        assay_pairs.add(pair)

    count = len(expected)
    if status not in {"CANCELLED", "INCOMPLETE"}:
        expected_status = ("QUALIFIED" if count == metrics["requested_count"] else
                           "PARTIAL" if count else "NO_QUALIFYING_DESIGNS")
        require(status == expected_status, "Run status contradicts qualifying count")
    if status == "NO_QUALIFYING_DESIGNS":
        require(candidates and all(any(v["state"] == "FAIL" for v in r["rules"]
                                       if v["rule_id"] in required_ids) for r in candidates),
                "Unresolved/empty work is not a completed negative result")
    if status == "INCOMPLETE":
        require(count == 0, "An incomplete zero-qualification status cannot contain a shortlist")

    fasta = {f"{key}|{chain}": records[key]["sequences"][field] for key in expected
             for chain, field in (("H", "heavy"), ("L", "light"))}
    require(_read_fasta(bundle / "designed_sequences.fasta") == fasta,
            "FASTA and shortlist disagree")
    with (bundle / "shortlist.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == ["rank", "candidate_id", "sequence_sha256"],
                "CSV header mismatch")
        rows = list(reader)
    expected_rows = [{"rank": str(i), "candidate_id": key,
                      "sequence_sha256": records[key]["sequence_sha256"]}
                     for i, key in enumerate(expected, 1)]
    require(rows == expected_rows, "CSV and shortlist disagree")
    require((bundle / "report.md").read_text().strip(), "Human-readable report is empty")
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pre = sub.add_parser("preflight")
    pre.add_argument("request", type=Path)
    pre.add_argument("--input-root", type=Path)
    out = sub.add_parser("bundle")
    out.add_argument("directory", type=Path)
    out.add_argument("--request", type=Path, required=True)
    out.add_argument("--input-root", type=Path)
    assay = sub.add_parser("assay-record")
    assay.add_argument("record", type=Path)
    assay.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "preflight":
            result = preflight(read_json(args.request), args.input_root or args.request.parent)
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "CONTRACT_READY" else 2
        if args.command == "assay-record":
            result = validate_assay_record(args.record, args.root or args.record.parent)
            print(json.dumps({"status": "VALID", "record_id": result["record_id"],
                              "result_state": result["result_state"]}))
            return 0
        result = validate_bundle(args.directory, args.request, args.input_root)
        print(json.dumps({"status": "VALID", "run_status": result["run_status"],
                          "scope": "Contract and artifact integrity only"}))
        return 0
    except Exception as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
