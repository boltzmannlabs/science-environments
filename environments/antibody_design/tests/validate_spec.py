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

from jsonschema import Draft202012Validator
from schema_registry import schema_path, schema_validator, schema_registry, config_path
from task_contracts import task_profile, validate_task_contract
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "results/specification-validation.json"
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


def validate_paper_benchmark_tasks(config):
    tasks = config.get("paper_benchmark_tasks", {})
    benchmarks = config.get("paper_benchmark_references", {})
    paths = set(tasks.values())
    check(len(paths) == len(tasks) and len(set(benchmarks.values())) == len(benchmarks) and
          set(tasks) == set(benchmarks) and not (set(tasks) & set(config["task_profiles"])),
          "Paper tasks and benchmarks have unique paired mappings separate from executable profiles")
    required_headings = {"Description", "Target", "Design Constraints", "Evaluation Metrics",
                         "Expected Output", "Important Instructions"}
    for task_id, relative in tasks.items():
        path = ROOT / relative
        valid_path = relative == f"tasks/monoclonal_antibody_design/{task_id}.md"
        text = path.read_text() if valid_path and path.is_file() else ""
        benchmark_relative = benchmarks[task_id]
        benchmark_path = ROOT / benchmark_relative
        valid_benchmark_path = benchmark_relative == f"benchmark/monoclonal_antibody_design/{task_id}.md"
        benchmark_text = (benchmark_path.read_text()
                          if valid_benchmark_path and benchmark_path.is_file() else "")
        headings = set(re.findall(r"^## (.+)$", text, re.M))
        check(text.startswith(f"# Task: {task_id}\n") and required_headings <= headings and
              "Benchmark" not in headings and "Computational Tool Capabilities" not in headings and
              f"(../../{benchmark_relative})" in text and
              benchmark_text.startswith("# Benchmark: ") and
              f"**Task ID:** `{task_id}`" in benchmark_text and
              "## Published Results" in benchmark_text and "https://doi.org/" in benchmark_text and
              f"(../../{relative})" in benchmark_text,
              f"Task and benchmark have separate content, matching names and reciprocal links: {task_id}")
    return paths


def main():
    required = [
        "README.md", "ENVIRONMENT_SPEC.md", "tests/monoclonal_antibody_with_reference/validation.py",
        "config/environment.yaml", "config/README.md", "config/requirements.txt",
        "config/monoclonal_reference/request.schema.json",
        "config/monoclonal_reference/denv.request.schema.json", "config/shared/protocol.schema.json",
        "config/monoclonal_reference/denv.result.schema.json", "config/shared/metric-catalog.json", "tests/fixtures/retired_tasks/denv_antibody_001.md",
        "tests/fixtures/retired_tasks/denv_antibody_001_tools.md", "config/monoclonal_reference/denv.request.example.json",
        "tests/fixtures/retired_tasks/mab_reference_guided_design.md", "config/monoclonal_reference/request.example.json",
        "tests/fixtures/retired_tasks/mab_target_only_design.md",
        "tasks/bispecific_design/bispecific_antibody_design.md",
        "tasks/bispecific_assessment/bispecific_cellular_mechanism_assessment.md",
        "tasks/bispecific_assessment/bispecific_cns_delivery_assessment.md",
        "tasks/bispecific_assessment/bispecific_cns_readout_comparison.md",
        "tasks/bispecific_assessment/bispecific_cns_shuttle_integrated_gate.md",

        "config/monoclonal_reference/result.schema.json", "config/shared/mab-assay-record.schema.json",
        "tests/monoclonal_antibody_with_reference/test_reference_guided.py", "tests/monoclonal_antibody_with_reference/contract_fixtures.py", "tests/monoclonal_antibody_with_reference/COVERAGE.md",
        "tests/monoclonal_antibody_with_reference/ACCEPTANCE.md", "tests/monoclonal_antibody_with_reference/MONOCLONAL_ANTIBODY_TEST_CASES.md",
        "tests/monoclonal_antibody_with_reference/test_task_variants.py", "tests/monoclonal_antibody_with_reference/test_denv_reference.py",
        "tests/monoclonal_antibody_with_reference/test_mab_testing_criteria.py", "tests/validate_spec.py",
        "tests/monoclonal_antibody_with_reference/__init__.py",
        "tests/monoclonal_antibody_with_reference/README.md",
        "tests/monoclonal_antibody_with_reference/make_needs_input_example.py",
        "results/README.md", "results/needs-input.example.json",
        "../../research/antibody_design/research-notes.md",
        "../../research/antibody_design/references.md",
        "../../research/antibody_design/DENV2_Computational_Antibody_Benchmark.md",
    ]
    check(all((ROOT / relative).is_file() for relative in required), "Required environment and research files exist")

    required.extend(path.relative_to(ROOT).as_posix() for path in (ROOT / "config").rglob("*") if path.is_file())
    required.extend(path.relative_to(ROOT).as_posix() for path in (ROOT / "tests").rglob("*.py"))
    required = sorted(set(required))
    registry = schema_registry()
    def verify_refs(node, resolver):
        if isinstance(node, dict):
            if "$ref" in node:
                resolver.lookup(node["$ref"])
            for child in node.values():
                verify_refs(child, resolver)
        elif isinstance(node, list):
            for child in node:
                verify_refs(child, resolver)
    for path in sorted((ROOT / "config").rglob("*.schema.json")):
        schema = validation_json(path)
        Draft202012Validator.check_schema(schema)
        verify_refs(schema, registry.resolver(base_uri=schema["$id"]))
        check(True, f"Schema and local references resolve: {path.relative_to(ROOT)}")
    schema_data = {}
    for name in ("request", "protocol", "metrics", "generic-antibody-request",
                 "generic-antibody-metrics", "mab-assay-record"):
        schema = validation_json(schema_path(name))
        Draft202012Validator.check_schema(schema)
        schema_data[name] = schema
        check(True, f"{name} schema is valid JSON Schema")

    config = yaml.safe_load((ROOT / "config/environment.yaml").read_text())
    # Verify every task profile independently of legacy reference-bundle settings.
    check(len(config["task_profiles"]) == 9, "All nine task profiles are registered")
    for task in config["task_profiles"]:
        profile = task_profile(task)
        check(profile["scientific_execution_included"] is False and
              profile["scientific_thresholds_supplied"] is False,
              f"Profile does not claim scientific execution or supplied thresholds: {task}")
        if profile.get("prompt_status") == "retired":
            fixture = Path(profile["fixture_file"])
            check("task_file" not in profile and fixture.parent == Path("tests/fixtures/retired_tasks") and
                  (ROOT / fixture).is_file(), f"Retired prompt is retained only as a test fixture: {task}")
        else:
            check(profile["task_file"].startswith("tasks/") and (ROOT / profile["task_file"]).is_file(),
                  f"Profile task file exists: {task}")
            family = Path(config["task_profiles"][task]).parent.name
            check(Path(profile["task_file"]).parent == Path("tasks") / family,
                  f"Task folder matches configuration family: {task}")
        for kind in ("request", "result"):
            check(config_path(profile[f"{kind}_schema"]).is_file(), f"Profile {kind} schema exists: {task}")
        example_path = ROOT / profile.get("request_example", "config/monoclonal_reference/denv.request.example.json")
        profile_example = validation_json(example_path)
        if "variant" in profile:
            profile_example["variant"] = profile["variant"]
        check(validate_task_contract(profile_example, task)["status"] == "CONTRACT_VALID",
              f"Incomplete example satisfies declared contract only: {task}")
    for relative in config["contracts"].values():
        check(relative.startswith("config/") and (ROOT / relative).is_file(),
              f"Configured contract exists under config: {relative}")
    for relative in [*config["task_templates"].values(), *config["task_variants"].values()]:
        check(relative.startswith("tasks/") and Path(relative).suffix == ".md" and (ROOT / relative).is_file(),
              f"Configured Markdown task exists under tasks: {relative}")
    for relative in config["request_examples"].values():
        check(config_path(relative).suffix == ".json",
              f"Configured JSON request example exists under config: {relative}")
    validation_config = config["validation"]
    check(validation_config["entrypoint"] == "tests/monoclonal_antibody_with_reference/validation.py" and
          validation_config["package_check"] == "tests/validate_spec.py" and
          validation_config["test_directory"] == "tests",
          "All configured validation and scenario testing lives under tests")
    check((ROOT / validation_config["requirements"]).is_file() and
          validation_config["requirements"] == "config/requirements.txt" and
          ROOT / validation_config["report"] == REPORT,
          "Validation dependencies and report use config and results respectively")
    check(all(path.relative_to(ROOT).parts[0] == "tests" for path in ROOT.rglob("*.py")),
          "All Python testing and validation code is confined to tests")
    directories = {path.name for path in ROOT.iterdir() if path.is_dir()
                   and not path.name.startswith(".") and path.name != "__pycache__"}
    required_directories = {"config", "tasks", "tests", "results"}
    check(required_directories <= directories <= required_directories | {"src", "scripts", "skills", "benchmark"},
          "Environment contains required directories and supported source, script, skill and benchmark directories")
    check({path.relative_to(ROOT / "tests").parts[0] for path in (ROOT / "tests").rglob("test_*.py")} ==
          {"monoclonal_antibody_with_reference", "test_configurations.py"},
          "Scenario tests remain monoclonal; shared configuration checks live directly under tests")
    catalog = validation_json(ROOT / "config/shared/metric-catalog.json")
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
    expected_templates = {"bispecific_design", "bispecific_cellular_mechanism_assessment",
                          "bispecific_cns_delivery_assessment", "bispecific_cns_readout_comparison",
                          "bispecific_cns_shuttle_integrated_gate"}
    check(set(config["task_templates"]) == expected_templates,
          "Profile-backed task catalog contains only the five bispecific tasks")
    check(all(config["task_status"][name] == "retained_contract_only" for name in
              ("reference_guided_monoclonal", "target_only_monoclonal", "denv_profile")) and
          not config["task_variants"] and
          all(config["task_status"][name] == "contract_schema_implemented"
              for name in expected_templates),
          "Retired monoclonal prompts are excluded from the active task catalog")
    check(set(config["scope"]["active_design_modes"]) == validation.REFERENCE_GUIDED_MODES,
          "Executable objectives still require a supplied monoclonal reference")
    expected_task_paths = set(config["task_templates"].values()) | set(config["task_variants"].values())
    registered_tasks = {profile["task_file"] for task in config["task_profiles"]
                        if "task_file" in (profile := task_profile(task))}
    task_files = [path for path in (ROOT / "tasks").rglob("*") if path.is_file()]
    paper_task_paths = validate_paper_benchmark_tasks(config)
    fixed_tasks = config.get("fixed_framework_tasks", {})
    fixed_task_paths = set(fixed_tasks.values())
    check(len(fixed_task_paths) == len(fixed_tasks) and
          not (set(fixed_tasks) & (set(config["task_profiles"]) |
                                   set(config.get("paper_benchmark_tasks", {})))) and
          not (fixed_task_paths & (expected_task_paths | paper_task_paths)),
          "Fixed-framework prompts have unique IDs and paths separate from profiles and benchmarks")
    for task_id, relative in fixed_tasks.items():
        path = ROOT / relative
        valid_path = Path(relative).parent.as_posix() == "tasks/monoclonal_antibody_design"
        text = path.read_text() if valid_path and path.is_file() else ""
        headings = set(re.findall(r"^## (.+)$", text, re.M))
        check(text.startswith(f"# Task: {task_id}\n") and
              {"Description", "Target", "Design Constraints", "Computational Tool Capabilities",
               "Evaluation Metrics", "Expected Output", "Important Instructions"} <= headings,
              f"Fixed-framework task has its declared identity and required sections: {task_id}")
    check({path.relative_to(ROOT).as_posix() for path in task_files} ==
          expected_task_paths | paper_task_paths | fixed_task_paths and
          expected_task_paths == registered_tasks and
          all(path.suffix == ".md" for path in task_files),
          "Task folders match registered profiles, paper benchmarks and fixed-framework prompts")
    for relative in sorted(expected_task_paths):
        task_text = (ROOT / relative).read_text()
        headings = set(re.findall(r"^## (.+)$", task_text, re.M))
        check({"Description", "Target", "Evaluation Metrics", "Expected Output", "Important Instructions"} <= headings,
              f"Task has consistent reader-facing sections: {relative}")
        capability_heading = "Data Analysis Tool Capabilities" if "assessment/" in config["task_profiles"].get(
            Path(relative).stem, "") else "Computational Tool Capabilities"
        check(capability_heading in headings, f"Task has appropriate tool capabilities: {relative}")
        check(task_text.index("## " + capability_heading) < task_text.index("## Evaluation Metrics"),
              f"Task presents workflow before evaluation: {relative}")
        check(not re.search(r"Stability-Binding|PRODIGY|ipSAE|StabDDG|Boltz2?|AlphaFold|"
                            r"RFdiffusion|ProteinMPNN|ESMFold", task_text, re.I),
              f"Task describes capabilities without software names: {relative}")
        check(not re.search(r"Machine-readable contract|Implementation status|Environment status|"
                            r"Task family:|Competency:|Grader type:|Scientific Intuition", task_text, re.I),
              f"Task omits implementation boilerplate: {relative}")
        check(not re.search(r"budget|wall[- ]time|time limit|compute limit|resource limit|"
                            r"\bCPU\b|\bGPU\b|\d+[- ]minute", task_text, re.I),
              f"Task omits runtime and compute-budget criteria: {relative}")
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

    example = validation.read_json(ROOT / "config/monoclonal_reference/denv.request.example.json")
    validation.validate_request(example)
    check(example["knowledge_cutoff"] == "2024-09-01", "Example preserves the requested knowledge cutoff")
    check(example["target"]["sequence"] is None and example["reference"]["sequences"] is None,
          "Example does not invent antigen or antibody sequences")
    check(validation.preflight(example, ROOT / "config/monoclonal_reference")["status"] == "NEEDS_INPUT",
          "Incomplete example fails closed during preflight")
    preflight_result = validation.preflight(example, ROOT / "config/monoclonal_reference")
    needs_input = validation.read_json(ROOT / "results/needs-input.example.json")
    schema_validator("metrics").validate(needs_input)
    check(needs_input["provenance"]["request_sha256"] == hashlib.sha256((ROOT / "config/monoclonal_reference/denv.request.example.json").read_bytes()).hexdigest(),
          "Example preflight result binds to its exact request")
    check(needs_input["missing_requirements"] == preflight_result["missing_requirements"],
          "Example preflight result lists the actual missing biological inputs")

    task_paths = [ROOT / "tests/fixtures/retired_tasks/denv_antibody_001.md", ROOT / "tests/fixtures/retired_tasks/denv_antibody_001_tools.md"]
    generic, specific = (path.read_text() for path in task_paths)
    expected_headings = ["Description", "Target", "Design Constraints", "Computational Tool Capabilities",
                         "Evaluation Metrics", "Expected Output", "Constraints", "Important Instructions"]
    check(re.findall(r"^## (.+)$", generic, re.M) == expected_headings,
          "General task follows the benchmark task structure")
    normalized = []
    for text in (generic, specific):
        text = re.sub(r"\*\*Task variant:\*\* `[^`]+`", "**Task variant:** `shared`", text)
        normalized.append(re.sub(r"## Computational Tool Capabilities\n.*?(?=## Evaluation Metrics\n)",
                                 "", text, flags=re.S))
    check(normalized[0] == normalized[1], "Both task variants have identical scientific requirements and outputs")
    check("verified energy-change sign convention" in specific and "interface confidence inputs" in specific,
          "Tools variant specifies evidence requirements without software names")
    documented_names = {item["name"].casefold() for item in config["documented_methods"]}
    check(documented_names == {"stability-binding ddg", "prodigy", "ipsae"}
          and "boltz" not in "".join(documented_names) and "stabddg" not in "".join(documented_names),
          "Configuration documents only the current registered method names")
    check("docking" in config["unbound_capabilities"] and "molecular_dynamics" in config["unbound_capabilities"],
          "Undocumented implementation choices remain explicitly unbound")

    generic_request = validation_json(ROOT / "config/monoclonal_reference/request.example.json")
    validation.validate_generic_request(generic_request)
    check(validation.preflight(generic_request, ROOT / "config/monoclonal_reference")["status"] == "NEEDS_INPUT",
          "Reusable reference-guided example reports missing input artifacts")
    generic_validator = schema_validator("generic-antibody-request")
    missing_reference = json.loads(json.dumps(generic_request))
    missing_reference["antibody"]["reference"] = None
    check(bool(list(generic_validator.iter_errors(missing_reference))),
          "Active schema rejects a request without a reference")
    target_only = json.loads(json.dumps(generic_request))
    target_only["design_mode"] = "de_novo"
    check(bool(list(generic_validator.iter_errors(target_only))),
          "Active schema rejects target-only design")
    check(set(schema_data["generic-antibody-request"]["properties"]["design_mode"]["enum"]) ==
          set(schema_data["generic-antibody-metrics"]["properties"]["design_mode"]["enum"]) ==
          validation.REFERENCE_GUIDED_MODES,
          "Request and result schemas agree on reference-required objectives")
    template = ROOT / task_profile("mab_reference_guided_design")["fixture_file"]
    check(bool(re.search(r"^## Expected output$", template.read_text(), re.I | re.M)),
          "Reference-guided task defines the output contract")
    check(not re.search(r"\b(StabDDG|Boltz2?|PRODIGY|ipSAE)\b", template.read_text(), re.I),
          "Reusable reference-guided task remains tool-neutral")

    documents = list(ROOT.rglob("*.md")) + list((ROOT.parent.parent / "research/antibody_design").rglob("*.md"))
    check(local_links(documents) > 0, "Documentation links stay inside present local package files")

    test_env = dict(os.environ)
    test_env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", validation_config["test_directory"],
                             "-t", "tests", "-p", "test_*.py"],
                            cwd=ROOT, text=True, capture_output=True, env=test_env)
    check(result.returncode == 0, "Synthetic contract behavior tests pass: " + result.stderr[-500:])

    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "environment_id": config["environment_id"], "maturity": config["maturity"],
              "validation_scope": "local specification and synthetic contract checks; no scientific execution",
              "status": "PASS", "checks_passed": len(CHECKS), "checks": CHECKS,
              "dependencies": {"python": sys.version.split()[0],
                               "jsonschema": importlib.metadata.version("jsonschema"),
                               "PyYAML": importlib.metadata.version("PyYAML"),
                               "referencing": importlib.metadata.version("referencing")},
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
    sys.path.insert(0, str(ROOT / "tests"))
    from monoclonal_antibody_with_reference import validation
    main()
