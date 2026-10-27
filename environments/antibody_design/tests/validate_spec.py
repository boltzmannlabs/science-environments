#!/usr/bin/env python3
"""Run local specification checks and synthetic behavior tests; no scientific execution."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from jsonschema import Draft202012Validator, FormatChecker
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "tests/specification-validation.json"
CHECKS = []


def check(condition, label):
    if not condition:
        raise AssertionError(label)
    CHECKS.append({"check": label, "status": "PASS"})


def local_links(documents):
    count = 0
    for document in documents:
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text()):
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = (document.parent / link.split("#", 1)[0]).resolve()
            check(target.is_file(), f"Local link resolves: {document.relative_to(ROOT.parent.parent)} -> {link}")
            count += 1
    return count


def main():
    required = [
        "README.md", "ENVIRONMENT_SPEC.md", "validation.py",
        "config/environment.yaml", "config/generic-antibody-request.schema.json",
        "config/request.schema.json", "config/protocol.schema.json",
        "config/metrics.schema.json", "config/metric-catalog.json", "tasks/denv_antibody_001.md",
        "tasks/denv_antibody_001_tools.md", "tasks/request.example.json",
        "tasks/mab_reference_guided_design.md", "tasks/mab_target_only_design.md",
        "tasks/bispecific_antibody_design.md", "tasks/bispecific_cellular_mechanism_assessment.md",
        "tasks/bispecific_cns_delivery_assessment.md", "tasks/bispecific_cns_shuttle_integrated_gate.md",
        "tasks/bispecific_cns_readout_comparison.md",
        "tests/ACCEPTANCE.md", "tests/MONOCLONAL_ANTIBODY_TEST_CASES.md",
        "tests/test_task_variants.py", "tests/test_validation.py",
        "tests/test_mab_testing_criteria.py", "tests/validate_spec.py",
        "results/README.md", "results/needs-input.example.json",
        "../../research/antibody_design/research-notes.md",
        "../../research/antibody_design/references.md",
        "../../research/antibody_design/DENV2_Computational_Antibody_Benchmark.md",
    ]
    check(all((ROOT / relative).is_file() for relative in required), "Required environment and research files exist")

    schema_data = {}
    for name in ("request", "protocol", "metrics", "generic-antibody-request"):
        schema = validation_json(ROOT / "config" / f"{name}.schema.json")
        Draft202012Validator.check_schema(schema)
        schema_data[name] = schema
        check(True, f"{name} schema is valid JSON Schema")

    config = yaml.safe_load((ROOT / "config/environment.yaml").read_text())
    catalog = validation_json(ROOT / "config/metric-catalog.json")
    metric_ids = {metric["metric_id"] for metric in catalog["metrics"]}
    check(len(metric_ids) == len(catalog["metrics"]), "Antibody metric catalog IDs are unique")
    check({"plddt", "iptm", "ipsae", "stabddg_delta_delta_g"} <= metric_ids,
          "Metric catalog covers paired antibody structure, interface, and stability evidence")
    endpoint_ids = {item["endpoint"] for item in catalog["noninterchangeable_endpoints"]}
    check({"equilibrium_dissociation_constant", "ELISA_binding_EC50",
           "viral_neutralization_potency", "antibody_dependent_enhancement_risk"} <= endpoint_ids,
          "Affinity, binding, neutralization, and enhancement endpoints are distinct")
    check(config["maturity"] == "Specification", "Maturity does not claim scientific validation")
    check(config["scientific_execution_included"] is False and config["contract_validation_included"] is True,
          "Configuration distinguishes implemented contract checks from scientific execution")
    check(set(config["task_templates"]) == {"reference_guided_monoclonal", "target_only_monoclonal",
                                             "bispecific_design", "bispecific_cellular_mechanism_assessment",
                                             "bispecific_cns_delivery_assessment", "bispecific_cns_shuttle_integrated_gate",
                                             "bispecific_cns_readout_comparison"},
          "Configuration registers the reusable monoclonal and bispecific task templates")
    stages = config["stages"]
    expected = ["prepare", "reference", "candidates", "structure", "interface",
                "specificity_function", "developability", "dynamics", "evaluate", "export"]
    check([stage["id"] for stage in stages] == expected, "Antibody assessment stages are ordered")
    seen, outputs = set(), set()
    for stage in stages:
        check(set(stage["depends_on"]) <= seen, f"Stage dependencies precede {stage['id']}")
        check(stage["output"] not in outputs, f"Stage output is unique: {stage['id']}")
        seen.add(stage["id"])
        outputs.add(stage["output"])
    check("identity" in config["required_rule_groups"] and "framework" in config["required_rule_groups"],
          "Antibody identity and framework rules are explicit")
    check(config["qualification"]["required_rule_combiner"] == "all" and
          config["qualification"]["evidence_bound_to_sequence_hash"],
          "Qualification requires all rules and sequence-bound evidence")

    example = validation.read_json(ROOT / "tasks/request.example.json")
    validation.validate_request(example)
    check(example["knowledge_cutoff"] == "2024-09-01", "Example preserves the requested knowledge cutoff")
    check(example["target"]["sequence"] is None and example["reference"]["sequences"] is None,
          "Example does not invent antigen or antibody sequences")
    check(validation.preflight(example, ROOT / "tasks")["status"] == "NEEDS_INPUT",
          "Incomplete example fails closed during preflight")
    preflight_result = validation.preflight(example, ROOT / "tasks")
    needs_input = validation.read_json(ROOT / "results/needs-input.example.json")
    Draft202012Validator(schema_data["metrics"]).validate(needs_input)
    check(needs_input["provenance"]["request_sha256"] == hashlib.sha256((ROOT / "tasks/request.example.json").read_bytes()).hexdigest(),
          "Example preflight result binds to its exact request")
    check(needs_input["missing_requirements"] == preflight_result["missing_requirements"],
          "Example preflight result lists the actual missing biological inputs")

    task_paths = [ROOT / "tasks/denv_antibody_001.md", ROOT / "tasks/denv_antibody_001_tools.md"]
    generic, specific = (path.read_text() for path in task_paths)
    expected_headings = ["Description", "Target", "Design Constraints", "Required Execution Steps",
                         "Evaluation Metrics", "Expected Output", "Constraints", "Important Instructions"]
    check(re.findall(r"^## (.+)$", generic, re.M) == expected_headings,
          "General task follows the benchmark task structure")
    check("## Available Computational Methods" in specific, "Tool-specific task declares named methods")
    normalized = re.sub(r"\*\*Task variant:\*\* `[^`]+`", "**Task variant:** `shared`", specific)
    normalized = re.sub(r"## Available Computational Methods\n.*?(?=## Required Execution Steps\n)", "", normalized, flags=re.S)
    normalized_generic = re.sub(r"\*\*Task variant:\*\* `[^`]+`", "**Task variant:** `shared`", generic)
    check(normalized == normalized_generic, "Both task variants have identical scientific requirements and outputs")
    for name in ("Stability-Binding DDG", "PRODIGY", "ipSAE"):
        check(name.casefold() in specific.casefold(), f"Dengue-documented method appears: {name}")
        check(name.casefold() not in generic.casefold(), f"General task remains tool neutral: {name}")
    check("StabDDG" not in specific and "Boltz2" not in specific,
          "Tool-specific task uses the registered Stability-Binding DDG name")
    documented_names = {item["name"].casefold() for item in config["documented_methods"]}
    check(documented_names == {"stability-binding ddg", "prodigy", "ipsae"}
          and "boltz" not in "".join(documented_names) and "stabddg" not in "".join(documented_names),
          "Configuration documents only the current registered method names")
    check("docking" in config["unbound_capabilities"] and "molecular_dynamics" in config["unbound_capabilities"],
          "Undocumented implementation choices remain explicitly unbound")

    generic_schema = schema_data["generic-antibody-request"]
    generic_validator = Draft202012Validator(generic_schema, format_checker=FormatChecker())
    generic_artifact = {"path": "inputs/example.dat", "sha256": "a" * 64,
                        "media_type": "application/octet-stream", "source": "declared example"}
    generic_request = {
        "schema_version": "1.0", "task_id": "mab_target_only_001", "design_mode": "de_novo",
        "target": {"target_id": "target-x", "name": "Target X", "organism": "organism-x",
                   "accession": None, "sequence": generic_artifact,
                   "constructs": [{"construct_id": "construct-x", "sequence": generic_artifact,
                                   "presentation_context": "unknown", "chain_ids": [],
                                   "residue_mapping": None, "post_translational_modifications": []}],
                   "epitope_policy": {"mode": "open_search", "residues": [], "evidence": None}},
        "antibody": {"format": "full_length_IgG", "sequence_scope": "variable_domains",
                     "reference": None, "desired_isotype": "IgG1",
                     "light_chain_type": "kappa", "fc_policy": "to_be_decided"},
        "objective": {"mechanism": "binding_only", "desired_effect": "target binding",
                      "specificity_scope": "declared target panel"},
        "constraints": {"preserve_heavy_light_pairing": True, "framework_policy": "preserve",
                        "numbering_scheme": "IMGT", "editable_regions": [], "max_mutations_per_chain": None,
                        "max_candidates": 10},
        "evaluation": {"protocol": generic_artifact, "requested_count": 1, "seed": 1,
                       "required_evidence_domains": ["identity", "structure", "interface", "specificity"]},
        "budget": {"wall_time_minutes": 120, "cpu_hours": 4, "gpu_hours": 4},
        "knowledge_cutoff": "2024-09-01"
    }
    check(not list(generic_validator.iter_errors(generic_request)),
          "Generic schema accepts a target-only design request without a reference antibody")
    reference_guided = json.loads(json.dumps(generic_request))
    reference_guided["design_mode"] = "reference_guided"
    check(bool(list(generic_validator.iter_errors(reference_guided))),
                "Reference-guided mode rejects a request without a supplied reference antibody")

    template_docs = [ROOT / relative for relative in (
        "tasks/mab_reference_guided_design.md", "tasks/mab_target_only_design.md",
        "tasks/bispecific_antibody_design.md", "tasks/bispecific_cellular_mechanism_assessment.md",
        "tasks/bispecific_cns_delivery_assessment.md", "tasks/bispecific_cns_shuttle_integrated_gate.md",
        "tasks/bispecific_cns_readout_comparison.md")]
    check(all(re.search(r"^## Expected (?:output|response format)$", path.read_text(), re.I | re.M)
              for path in template_docs),
          "Every reusable design or assessment task defines an expected output contract")
    check(all(not re.search(r"\b(StabDDG|Boltz2?|PRODIGY|ipSAE)\b", path.read_text(), re.I)
              for path in template_docs),
          "Reusable monoclonal and bispecific tasks remain tool-neutral")

    documents = list(ROOT.rglob("*.md")) + list((ROOT.parent.parent / "research/antibody_design").rglob("*.md"))
    check(local_links(documents) > 0, "Documentation links stay inside present local package files")

    test_env = dict(os.environ)
    test_env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
                            cwd=ROOT, text=True, capture_output=True, env=test_env)
    check(result.returncode == 0, "Synthetic contract behavior tests pass: " + result.stderr[-500:])

    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "environment_id": config["environment_id"], "maturity": config["maturity"],
              "validation_scope": "local specification and synthetic contract checks; no scientific execution",
              "status": "PASS", "checks_passed": len(CHECKS), "checks": CHECKS,
              "dependencies": {"python": sys.version.split()[0],
                               "jsonschema": importlib.metadata.version("jsonschema"),
                               "PyYAML": importlib.metadata.version("PyYAML")},
              "file_sha256": {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
                              for relative in required if (ROOT / relative).is_file()},
              "behavior_tests": {"return_code": result.returncode,
                                 "stdout": result.stdout.strip(), "stderr": result.stderr.strip()},
              "not_performed": ["biological identity validation", "scientific adapter execution",
                                "antibody generation or optimization", "structure/interface prediction",
                                "affinity or developability calculation", "molecular dynamics",
                                "experimental binding, neutralization, or safety tests"]}
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(CHECKS)} specification checks; {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'behavior tests passed'}")
    print("No scientific calculations were performed.")
    print(f"Report: {REPORT}")


def validation_json(path):
    return json.loads(path.read_text())


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    import validation
    main()
