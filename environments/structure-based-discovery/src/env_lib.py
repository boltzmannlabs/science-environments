"""Shared library for task-doc parsing, environment validation, config generation
and run grading. Dependency-free (stdlib only). The task documents in tasks/ are
the single source of truth; config/ and benchmark/ are generated from them by
scripts/gen_config.py."""

import csv
import json
import os
import re

SECTIONS = [
    "Description",
    "Target",
    "Design Constraints",
    "Computational Tool Capabilities",
    "Evaluation Metrics",
    "Expected Output",
    "Constraints",
    "Important Instructions",
    "Publication",
]

WORKFLOW_SECTIONS = SECTIONS[:-1]

PLATFORM_DOCKING_ARG = "exhaustivness"  # real Boltzmann API spelling (sic) — do not "fix"


def env_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tasks_dir():
    return os.path.join(env_dir(), "tasks")


def task_files():
    return sorted(
        f for f in os.listdir(tasks_dir())
        if f.startswith("task_") and f.endswith(".md")
    )


def split_sections(text):
    """Return ordered list of (section_name, body)."""
    parts = re.split(r"^## +", text, flags=re.M)
    out = []
    for part in parts[1:]:
        name = part.splitlines()[0].strip()
        body = part[len(name):]
        out.append((name, body))
    return out


def parse_task(path):
    text = open(path, encoding="utf-8").read()
    sections = split_sections(text)
    sec = dict(sections)
    order = [name for name, _ in sections]
    title = text.splitlines()[0].lstrip("# ").strip()

    def field(section, label):
        body = sec.get(section, "")
        m = re.search(r"\*\*" + re.escape(label) + r":?\*\* ?(.*)", body)
        return m.group(1).strip() if m else None

    task_format = "paper_anchored" if "Publication" in sec else "capability_workflow"
    evaluator_file = None
    evaluator_text = ""
    evaluator_format = None
    grading_mode = None
    pub_body = sec.get("Publication", "")
    if task_format == "capability_workflow":
        evaluator_file = os.path.join("benchmark", os.path.basename(path))
        evaluator_path = os.path.join(os.path.dirname(os.path.dirname(path)), evaluator_file)
        if os.path.isfile(evaluator_path):
            with open(evaluator_path, encoding="utf-8") as fh:
                evaluator_text = fh.read()
            pub_body = dict(split_sections(evaluator_text)).get("Publication", "")
            format_m = re.search(r"^\*\*Task Format:\*\*\s*(\S+)", evaluator_text, re.M)
            mode_m = re.search(r"^\*\*Grading Mode:\*\*\s*(\S+)", evaluator_text, re.M)
            evaluator_format = format_m.group(1) if format_m else None
            grading_mode = mode_m.group(1) if mode_m else None
    doi_m = re.search(r"\((https?://doi\.org/[^\s)]+)\)", pub_body)
    pmc_m = re.search(r"\((https?://pmc\.ncbi\.nlm\.nih\.gov/articles/(PMC\d+)/?)\)", pub_body)

    target_body = sec.get("Target", "")
    pdbs = []
    for label in ("PDB", "PDBs"):
        m = re.search(r"\*\*" + label + r":?\*\* ?(.*)", target_body)
        if m:
            pdbs = re.findall(r"\b([1-9][A-Z0-9]{3})\b", m.group(1))
            break
    if not pdbs:
        # some docs name the structure only in the workflow/tool table;
        # require a letter in position 2 to reject years/counts like 2025/4809
        pdbs = re.findall(r"\b([1-9][A-Z][A-Z0-9]{2})\b", text)

    pass_bar = None
    for line in sec.get("Expected Output", "").splitlines():
        if line.strip().startswith("**Pass bar:**"):
            pass_bar = line.strip()[len("**Pass bar:**"):].strip()
            break
        if task_format == "capability_workflow" and line.strip().startswith("**Completion Rule:**"):
            pass_bar = line.strip()[len("**Completion Rule:**"):].strip()
            break

    expected_outputs = re.findall(r"^\|\s*`([^`]+)`\s*\|", sec.get("Expected Output", ""), re.M)

    evaluation_metrics = []
    for line in sec.get("Evaluation Metrics", "").splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line[1:-1].split("|")]
        if len(cells) < 2 or cells[0] in ("Metric", "Criterion", "File", "Tool", ""):
            continue
        if set(cells[0]) <= set("-: "):
            continue
        if task_format == "capability_workflow":
            evaluation_metrics.append({
                "metric": cells[0],
                "measurements_and_evidence": cells[1],
                "evaluation_rule": cells[2] if len(cells) > 2 else "",
            })
        else:
            evaluation_metrics.append({"metric": cells[0], "published_value": cells[1]})

    return {
        "file": os.path.basename(path),
        "id": re.match(r"(task_\d+)", os.path.basename(path)).group(1),
        "title": title,
        "section_order": order,
        "target": field("Target", "Name"),
        "disease": field("Target", "Disease"),
        "data": field("Target", "Data"),
        "pdbs": sorted(set(pdbs)),
        "doi": doi_m.group(1) if doi_m else None,
        "pmc": pmc_m.group(2) if pmc_m else None,
        "pass_bar": pass_bar,
        "expected_outputs": expected_outputs,
        "evaluation_metrics": evaluation_metrics,
        "task_format": task_format,
        "evaluator_file": evaluator_file,
        "evaluator_format": evaluator_format,
        "grading_mode": grading_mode,
        "text": text,
    }


def check_workflow_structure(parsed):
    """Validate an agent-facing workflow without exposing evaluator provenance."""
    errors = []
    prefix = parsed["file"] + ": "
    if parsed["section_order"] != WORKFLOW_SECTIONS:
        errors.append(prefix + "capability workflow sections are missing or out of order")
    if parsed["evaluator_format"] != "capability_workflow":
        errors.append(prefix + "missing capability-workflow evaluator specification")
    if parsed["grading_mode"] != "manual_review_required":
        errors.append(prefix + "workflow grading must require scientific review")
    if not parsed["doi"] or not parsed["pmc"]:
        errors.append(prefix + "evaluator specification missing source identifiers")
    if not parsed["pass_bar"]:
        errors.append(prefix + "missing Completion Rule")
    if not parsed["pdbs"]:
        errors.append(prefix + "Target section names no PDB ID")
    if not parsed["expected_outputs"]:
        errors.append(prefix + "missing required output files")
    if not parsed["evaluation_metrics"] or any(
        not row["evaluation_rule"] for row in parsed["evaluation_metrics"]
    ):
        errors.append(prefix + "metrics must include measurements and evaluation rules")
    for needle in ("Execution Budget:", "Reference Policy:", "Capability", "Expected Evidence"):
        if needle not in parsed["text"]:
            errors.append(prefix + "missing " + needle)
    forbidden = (
        r"doi\.org/|PMC\d+|\bUSRCAT\b|\bSwissADME\b|\bProTox\b|"
        r"\bVina\b|\bMGLTools\b|\bAvogadro\b|\bPyMOL\b|\bOpen\s*Babel\b|"
        r"\bGROMACS\b|\bOpenMM\b|\bVMD\b|\bATB\b|\bXmgrace\b|"
        r"Similarity_Screening|Property_Prediction|MDS_openMM|MDS_Gromacs|Diffdock|"
        r"Vina_basic_docking|exhaustivness"
    )
    if re.search(forbidden, parsed["text"], re.I):
        errors.append(prefix + "agent task exposes publication identity or prescribed tools")
    for token in ("TODO", "TBD", "XXX"):
        if token in parsed["text"]:
            errors.append(prefix + "placeholder '" + token + "' present")
    return errors


def check_structure(parsed):
    """Return list of structural error strings (empty = valid)."""
    if parsed["task_format"] == "capability_workflow":
        return check_workflow_structure(parsed)
    errors = []
    order = parsed["section_order"]
    if order != SECTIONS:
        expected = list(SECTIONS)
        for s in order:
            if s not in SECTIONS:
                errors.append(f"{parsed['file']}: unexpected section '{s}'")
        for s in expected:
            if s not in order:
                errors.append(f"{parsed['file']}: missing section '{s}'")
        if sorted(order) == sorted(SECTIONS):
            errors.append(f"{parsed['file']}: sections out of order")
    pb = parsed["pass_bar"]
    if not pb:
        errors.append(f"{parsed['file']}: no '**Pass bar:**' line in Expected Output")
    elif not re.search(r"\d", pb):
        errors.append(f"{parsed['file']}: pass bar not quantitative")
    constraints = parsed["text"]
    for needle, what in [
        ("Time Limit:", "time limit"),
        ("240 minutes", "240-minute limit"),
        ("Reference Policy", "reference policy"),
    ]:
        if needle not in constraints:
            errors.append(f"{parsed['file']}: Constraints missing {what}")
    if "Do NOT search" not in constraints:
        errors.append(f"{parsed['file']}: Important Instructions missing no-lookup boilerplate")
    if not parsed["doi"]:
        errors.append(f"{parsed['file']}: Publication missing DOI link")
    if not parsed["pmc"]:
        errors.append(f"{parsed['file']}: Publication missing PMC link")
    if not parsed["pdbs"]:
        errors.append(f"{parsed['file']}: Target section names no PDB ID")
    if PLATFORM_DOCKING_ARG not in constraints:
        errors.append(f"{parsed['file']}: platform docking arg 'exhaustivness' (sic) missing")
    for token in ("TODO", "TBD", "XXX"):
        if token in parsed["text"]:
            errors.append(f"{parsed['file']}: placeholder '{token}' present")
    return errors


def load_environment_json():
    path = os.path.join(env_dir(), "config", "environment.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_benchmark():
    path = os.path.join(env_dir(), "benchmark", "benchmark.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_papers_csv():
    path = os.path.join(env_dir(), "benchmark", "papers.csv")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def pass_bar_docking_threshold(pass_bar):
    """Best-effort machine parsing of the docking anchor (kcal/mol) from a pass bar."""
    if not pass_bar:
        return None
    m = re.search(r"(−?-?\d+(?:\.\d+)?)\s*kcal/mol", pass_bar)
    if not m:
        return None
    return float(m.group(1).replace("−", "-"))


def grade_run(task_id, run_dir, verbose=True):
    """Grade a results/<task_id>/<run>/ directory: expected files present,
    metrics.json parsed, docking score compared to the pass-bar anchor."""
    env = load_environment_json()
    task = next((t for t in env["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise SystemExit(f"unknown task id {task_id}")
    if task.get("grading_mode") == "manual_review_required":
        raise SystemExit(
            f"{task_id}: scientific review required; the legacy single-score grader "
            "cannot certify this capability workflow"
        )
    lines, failures = [], 0
    for fname in task["expected_outputs"]:
        exists = os.path.isfile(os.path.join(run_dir, fname))
        if not exists:
            failures += 1
        lines.append(f"  [{'PASS' if exists else 'FAIL'}] output file {fname}")
    metrics_path = os.path.join(run_dir, "metrics.json")
    score = None
    if os.path.isfile(metrics_path):
        with open(metrics_path, encoding="utf-8") as fh:
            metrics = json.load(fh)
        for key in ("best_docking_score", "best_score", "docking_score", "score", "best_hit_score"):
            if isinstance(metrics.get(key), (int, float)):
                score = float(metrics[key])
                break
    threshold = pass_bar_docking_threshold(task["pass_bar"])
    if score is not None and threshold is not None:
        ok = score <= threshold
        if not ok:
            failures += 1
        lines.append(f"  [{'PASS' if ok else 'FAIL'}] docking {score} <= anchor {threshold} kcal/mol")
    elif score is None:
        lines.append("  [WARN] metrics.json missing or has no numeric docking score (manual review)")
    if verbose:
        print(f"Grading {task_id} against run {run_dir}")
        print("\n".join(lines))
        print(f"RESULT: {'PASS' if failures == 0 else 'FAIL'} ({failures} hard failures)")
    return failures == 0
