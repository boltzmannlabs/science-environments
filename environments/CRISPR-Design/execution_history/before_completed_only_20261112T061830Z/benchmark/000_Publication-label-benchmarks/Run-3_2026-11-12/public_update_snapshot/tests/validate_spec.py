#!/usr/bin/env python3
"""Specification-package validation for the CRISPR-Design environment.

Stdlib only. 10 checks covering files/naming, task house structure, schema
well-formedness, example-brief schema conformance, YAML invariants, threshold
provenance, cross-references, benchmark-doc iteration structure, honesty markers
(no claimed executed results), and the runtime liveness probe's consistency.
Writes validation.json. Passing is package validation, not scientific validation.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.dirname(HERE)
results = {"checks": [], "passed": 0, "failed": 0}

APPLICATIONS = [
    "knockout_gene_disruption", "therapeutic_in_vivo_editing",
    "variant_correction_precision_repair", "base_editing", "prime_editing",
    "crispr_regulation", "epigenome_editing", "rna_targeting_cas13",
    "diagnostics_pathogen", "library_screen_design", "plant_genome_editing",
    "microbial_crispr_design",
]
ACTIVE = [a for a in APPLICATIONS if a not in ("diagnostics_pathogen", "plant_genome_editing")]
TASK_FILES = [f"{i:03d}_{name}.md" for i, name in enumerate([
    "crispr_design_general", "crispr_knockout", "crispr_therapeutic-in-vivo",
    "crispr_variant-correction", "crispr_base-editing", "crispr_prime-editing",
    "crispr_regulation", "crispr_epigenome-editing", "crispr_rna-targeting-cas13",
    "crispr_diagnostics", "crispr_library-screen-design", "crispr_plant-editing",
    "crispr_microbial"], start=1)]
EXAMPLE_FILES = ["001_design.request.example.json", "002_knockout.request.example.json",
                 "003_therapeutic-in-vivo.request.example.json", "004_variant-correction.request.example.json",
                 "005_base-editing.request.example.json", "006_prime-editing.request.example.json",
                 "007_crispr-regulation.request.example.json", "008_epigenome-editing.request.example.json",
                 "009_cas13.request.example.json", "010_diagnostics.request.example.json",
                 "011_library.request.example.json", "012_plant.request.example.json",
                 "013_microbial.request.example.json"]


def check(name, fn):
    try:
        detail = fn()
        results["checks"].append({"check": name, "status": "PASS", "detail": detail})
        results["passed"] += 1
        print(f"  PASS  {name}: {detail}")
    except Exception as e:
        results["checks"].append({"check": name, "status": "FAIL", "detail": str(e)[:300]})
        results["failed"] += 1
        print(f"  FAIL  {name}: {str(e)[:300]}")


def read(p):
    with open(os.path.join(ENV, p), encoding="utf-8") as f:
        return f.read()


def jread(p):
    return json.loads(read(p))


# ==================== 1. files ====================
def check_files():
    need = ["README.md", "ENVIRONMENT_SPEC.md", "STATUS.md", "MODELS_AND_TOOLS.md",
            "config/environment.yaml", "config/requirement_brief.schema.json",
            "config/candidate.schema.json", "config/thresholds.v0.1.draft.json",
            "runtime/CONTRACTS.md", "runtime/probe_backends.py",
            "tasks/README.md", "tests/ACCEPTANCE.md",
            "benchmark/README.md", "benchmark/BENCHMARK_RUNS.md", "results/README.md"]
    missing = [p for p in need if not os.path.isfile(os.path.join(ENV, p))]
    if missing:
        raise AssertionError(f"missing core files: {missing}")
    for group, names in (("tasks", TASK_FILES), ("config", EXAMPLE_FILES)):
        missing = [n for n in names if not os.path.isfile(os.path.join(ENV, group, n))]
        if missing:
            raise AssertionError(f"missing {group} files: {missing}")
    extra_tasks = [f for f in os.listdir(os.path.join(ENV, "tasks"))
                   if f.endswith(".md") and f not in TASK_FILES and f != "README.md"]
    if extra_tasks:
        raise AssertionError(f"unexpected task files: {extra_tasks}")
    return f"{len(need)} core + {len(TASK_FILES)} tasks + {len(EXAMPLE_FILES)} examples; naming aligned"


# ==================== 2. tasks ====================
def check_tasks():
    house = ["## Description", "## Target", "## Design Constraints",
             "## Required Execution Steps", "## Expected Output", "## Constraints",
             "## Important Instructions"]
    index = read("tasks/README.md")
    for tf in TASK_FILES:
        body = read(os.path.join("tasks", tf))
        for h in house:
            if h not in body:
                raise AssertionError(f"{tf} missing section {h}")
        if "| Step |" not in body and "| --- |" not in body:
            raise AssertionError(f"{tf} missing steps table")
        num = tf.split("_")[0]
        if num not in index:
            raise AssertionError(f"{tf} not indexed in tasks/README.md")
        # each application task references its example brief
        if tf != TASK_FILES[0]:
            ex = [e for e in EXAMPLE_FILES if e.startswith(num)]
            if not ex or ex[0] not in body:
                raise AssertionError(f"{tf} does not reference its example brief {ex}")
        if "NOT_EXECUTED" not in body and tf != TASK_FILES[0]:
            raise AssertionError(f"{tf} missing NOT_EXECUTED benchmark-status statement")
    return f"{len(TASK_FILES)} task docs: house sections, steps tables, index entries, example refs, status lines"


# ==================== 3. schemas ====================
def check_schemas():
    rb = jread("config/requirement_brief.schema.json")
    cand = jread("config/candidate.schema.json")
    apps = rb["properties"]["application"]["enum"]
    if apps != APPLICATIONS:
        raise AssertionError(f"application enum mismatch: {apps}")
    weights = rb["properties"]["priorities"]["properties"]["weights"]
    for dim in ["on_target", "specificity", "outcome_quality", "context"]:
        w = weights["properties"][dim]
        if w.get("minimum") != 0 or w.get("maximum") != 1:
            raise AssertionError(f"weight {dim} not bounded [0,1]")
    if cand["properties"]["spacer_sequence"].get("pattern") is None:
        raise AssertionError("candidate schema missing spacer pattern")
    return f"{len(apps)} applications; 4 bounded weight dims; spacer pattern present"


# ==================== 4. examples (mini schema validation) ====================
def _validate(instance, schema, path=""):
    errs = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object"]
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in instance:
                errs.append(f"{path}.{req}: required missing")
        if schema.get("additionalProperties") is False:
            for k in instance:
                if k not in props:
                    errs.append(f"{path}.{k}: additional property not allowed")
        for k, v in instance.items():
            if k in props:
                errs += _validate(v, props[k], f"{path}.{k}")
    elif t == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array"]
        for i, v in enumerate(instance):
            if "items" in schema:
                errs += _validate(v, schema["items"], f"{path}[{i}]")
    elif t == "string":
        if not isinstance(instance, str):
            errs.append(f"{path}: expected string")
        elif "minLength" in schema and len(instance) < schema["minLength"]:
            errs.append(f"{path}: shorter than minLength")
        elif "pattern" in schema and not re.search(schema["pattern"], instance):
            errs.append(f"{path}: pattern mismatch")
    elif t == "number":
        if isinstance(instance, bool) or not isinstance(instance, (int, float)):
            errs.append(f"{path}: expected number")
        else:
            if "minimum" in schema and instance < schema["minimum"]:
                errs.append(f"{path}: below minimum")
            if "maximum" in schema and instance > schema["maximum"]:
                errs.append(f"{path}: above maximum")
    elif t == "integer":
        if isinstance(instance, bool) or not isinstance(instance, int):
            errs.append(f"{path}: expected integer")
        elif "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{path}: below minimum")
    elif t == "boolean":
        if not isinstance(instance, bool):
            errs.append(f"{path}: expected boolean")
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{path}: {instance!r} not in enum")
    return errs


def check_examples():
    schema = jread("config/requirement_brief.schema.json")
    all_errs = []
    for ex in EXAMPLE_FILES:
        brief = jread(os.path.join("config", ex))
        errs = _validate(brief, schema, ex)
        all_errs += errs
    if all_errs:
        raise AssertionError("; ".join(all_errs[:6]))
    apps_seen = {jread(os.path.join("config", e))["application"] for e in EXAMPLE_FILES}
    if apps_seen != set(APPLICATIONS):
        raise AssertionError(f"examples cover {len(apps_seen)}/12 applications")
    return f"13 briefs conform to schema; all 12 applications covered"


# ==================== 5. yaml invariants ====================
def check_yaml():
    y = read("config/environment.yaml")
    for token in ["environment_id: crispr-design", "maturity: Partial-runtime, executed-computational-benchmarks",
                  "gate_thresholds_draft: config/thresholds.v0.1.draft.json",
                  "computational_benchmarks_included: true"]:
        if token not in y:
            raise AssertionError(f"environment.yaml missing token: {token}")
    for app in ACTIVE:
        if f"- {app}" not in y:
            raise AssertionError(f"active application missing from yaml: {app}")
    if "review_only_applications: [diagnostics_pathogen]" not in y:
        raise AssertionError("diagnostics not review-only in yaml")
    if "inactive_applications: [plant_genome_editing]" not in y:
        raise AssertionError("plant not inactive in yaml")
    for mode in ["design:", "evaluate:", "exploratory:", "benchmark:", "audit:"]:
        if mode not in y:
            raise AssertionError(f"mode missing: {mode}")
    return f"{len(ACTIVE)} active + 1 review-only + 1 inactive; 5 modes; draft-gates path"


# ==================== 6. thresholds ====================
def check_thresholds():
    th = jread("config/thresholds.v0.1.draft.json")
    if not th["version"].startswith("0.1-draft"):
        raise AssertionError("threshold version not draft")
    allowed = set(th["provenance_classes"])
    gates = th["gates"]
    if len(gates) < 10:
        raise AssertionError(f"only {len(gates)} draft gates")
    for name, g in gates.items():
        if g.get("provenance") not in allowed:
            raise AssertionError(f"gate {name} provenance not in declared set")
        if "source" not in g:
            raise AssertionError(f"gate {name} missing source")
    if not th.get("no_freeze_without"):
        raise AssertionError("no_freeze_without calibration list missing")
    return f"{len(gates)} draft gates, provenance-tagged; freeze blocked until calibration"


# ==================== 7. cross-references ====================
def check_cross_references():
    docs = ["README.md", "ENVIRONMENT_SPEC.md", "STATUS.md", "MODELS_AND_TOOLS.md",
            "runtime/CONTRACTS.md", "tests/ACCEPTANCE.md", "benchmark/README.md",
            "benchmark/BENCHMARK_RUNS.md", "results/README.md", "tasks/README.md"] + \
           [os.path.join("tasks", t) for t in TASK_FILES]
    link_re = re.compile(r"\]\(([^)#]+?)(?:#[^)]*)?\)")
    broken = []
    for doc in docs:
        base = os.path.dirname(os.path.join(ENV, doc))
        for m in link_re.finditer(read(doc)):
            target = m.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = os.path.normpath(os.path.join(base, target))
            if not os.path.exists(resolved):
                broken.append(f"{doc} -> {target}")
    if broken:
        raise AssertionError(f"broken links: {broken[:6]}")
    return f"all relative links in {len(docs)} docs resolve"


# ==================== 8. benchmark docs ====================
def check_benchmark_docs():
    readme = read("benchmark/README.md")
    runs = read("benchmark/BENCHMARK_RUNS.md")
    for token in ["Published anchor ledger", "Current execution",
                  "001_Xiang2021-clean-evaluation"]:
        if token not in readme:
            raise AssertionError(f"benchmark README missing token: {token}")
    if "| Area |" not in readme:
        raise AssertionError("benchmark README missing anchor table")
    sections = re.findall(r"^## \d", runs, flags=re.M)
    if len(sections) < 5:
        raise AssertionError(f"BENCHMARK_RUNS has {len(sections)} benchmark sections (<5)")
    not_exec = runs.count("NOT_EXECUTED")
    if not_exec < 6:
        raise AssertionError(f"only {not_exec} NOT_EXECUTED markers")
    if "No-tuning attestation" not in runs:
        raise AssertionError("attestation section missing")
    return f"{len(sections)} pre-registered benchmarks; {not_exec} NOT_EXECUTED slots; attestation present"


# ==================== 9. honesty markers ====================
def check_honesty():
    status = read("STATUS.md")
    spec = read("ENVIRONMENT_SPEC.md")
    readme = read("README.md")
    if "no wet-lab validation" not in status.lower():
        raise AssertionError("STATUS does not state the no-wet-lab-validation boundary")
    for token in ["NOT_IMPLEMENTED", "NEEDS_EXPERIMENTAL_VALIDATION"]:
        if token not in spec:
            raise AssertionError(f"spec missing honesty token {token}")
    if "Partial computational workflows and executed model benchmarks" not in readme:
        raise AssertionError("README missing maturity statement")
    results_dir = os.path.join(ENV, "results")
    run_dirs = [d for d in os.listdir(results_dir)
                if os.path.isdir(os.path.join(results_dir, d))]
    for d in run_dirs:
        if not re.match(r"^\d{3}_", d):
            raise AssertionError(f"results/ run dir not number-first: {d}")
        runs = os.listdir(os.path.join(results_dir, d))
        for rd in runs:
            if not rd.startswith("Run"):
                raise AssertionError(f"run dir not Run-prefixed: {d}/{rd}")
            brief = os.path.join(results_dir, d, rd, "00_inputs", "requirement_brief.json")
            if not os.path.isfile(brief):
                raise AssertionError(f"run without hashed brief: {d}/{rd}")
    return f"status/spec/readme honesty tokens present; {len(run_dirs)} application dir(s) with properly structured runs"


# ==================== 10. runtime probe ====================
def check_runtime_probe():
    src = os.path.join(ENV, "runtime", "probe_backends.py")
    spec_ = importlib.util.spec_from_file_location("probe_backends", src)
    mod = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(mod)
    if len(mod.BACKENDS) < 8:
        raise AssertionError("backend map too small")
    if len(mod.STAGES) < 6:
        raise AssertionError("stage map too small")
    for stage, deps in mod.STAGES.items():
        for d in deps:
            if d not in mod.BACKENDS:
                raise AssertionError(f"stage {stage} references unknown backend {d}")
    out = subprocess.run([sys.executable, src, "--json"], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise AssertionError(f"probe failed: {out.stderr[:200]}")
    report = json.loads(out.stdout)
    if set(report) != {"probe_version", "backends", "stages", "expected_absent"}:
        raise AssertionError("probe report shape unexpected")
    return f"probe runs; {len(mod.BACKENDS)} backends, {len(mod.STAGES)} stages; findings={report['stages']}"


if __name__ == "__main__":
    print(f"Validating CRISPR-Design specification package at {ENV}")
    for name, fn in [
        ("files", check_files), ("tasks", check_tasks), ("schemas", check_schemas),
        ("examples", check_examples), ("yaml_invariants", check_yaml),
        ("thresholds", check_thresholds), ("cross_references", check_cross_references),
        ("benchmark_docs", check_benchmark_docs), ("honesty_markers", check_honesty),
        ("runtime_probe", check_runtime_probe),
    ]:
        check(name, fn)
    with open(os.path.join(HERE, "validation.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n{results['passed']} passed, {results['failed']} failed -> tests/validation.json")
    sys.exit(1 if results["failed"] else 0)
