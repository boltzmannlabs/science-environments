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

    pub_body = sec.get("Publication", "")
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

    expected_outputs = re.findall(r"^\|\s*`([^`]+)`\s*\|", sec.get("Expected Output", ""), re.M)

    evaluation_metrics = []
    for line in sec.get("Evaluation Metrics", "").splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [c.strip() for c in line[1:-1].split("|")]
        if len(cells) < 2 or cells[0] in ("Metric", "File", "Tool", ""):
            continue
        if set(cells[0]) <= set("-: "):
            continue
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
        "text": text,
    }


def check_structure(parsed):
    """Return list of structural error strings (empty = valid)."""
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
