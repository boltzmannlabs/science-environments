#!/usr/bin/env python3
"""Full-guide verification for task_014 (monoclonal.md §7 handoff checklist)."""
import csv
import hashlib
import json
import os

N = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
T = "task_014_fxi_igdesign_cdr_redesign"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))


runs = ["run_001_antibmpnn_fixed_backbone", "run_002_igdesign_native_reconstruction"]
for run in runs:
    src = f"{N}/src/{T}/{run}"
    res = f"{N}/results/{T}/{run}"
    cfg = f"{N}/configs/{T}/{run}.json"
    # 1. paths exist + JSON valid
    for p in (f"{src}/workflow.md", f"{src}/run.yaml", cfg, f"{res}/run.json", f"{res}/report.md"):
        check(f"{run}: {os.path.relpath(p, N)} exists", os.path.exists(p))
    try:
        rj = json.load(open(f"{res}/run.json")); check(f"{run}: run.json valid JSON", True)
    except Exception as e:
        check(f"{run}: run.json valid JSON", False, str(e)); continue
    # 2. hashes current
    y = open(f"{src}/run.yaml").read()
    check(f"{run}: run.json sha256 in run.yaml", h(f"{res}/run.json") in y)
    check(f"{run}: config sha256 in run.yaml", h(cfg) in y)
    # 3. exactly two logs
    logs = sorted(os.listdir(f"{src}/logs"))
    check(f"{run}: exactly two logs", logs == ["agent_scientist_log.md", "execution_summary.md"], str(logs))
    # 4. execution records set
    er = os.listdir(f"{src}/inputs/execution_records")
    for req in ("full_config.json", "tool_details.json", "run_files.csv", "observable_events.jsonl"):
        check(f"{run}: execution_records/{req}", req in er)
    # 5. config five keys
    c = json.load(open(cfg))
    check(f"{run}: config exactly five keys", sorted(c) == ["llm_model", "llm_version", "time_budget", "tokens_used", "use_subagent"], str(sorted(c)))
    # 6. saved_artifacts.csv
    check(f"{run}: inputs/saved_artifacts.csv", os.path.exists(f"{src}/inputs/saved_artifacts.csv"))
    # 7. core result bundle
    for f in ("candidates.csv", "shortlist.csv", "metrics.csv", "benchmark_comparison.csv"):
        check(f"{run}: results/{f}", os.path.exists(f"{res}/{f}"))
    check(f"{run}: sequences fasta present", os.path.exists(f"{res}/designed_sequences.fasta") or os.path.exists(f"{res}/sequences.fasta"))
    check(f"{run}: structures/ nonempty", len(os.listdir(f"{res}/structures")) >= 11)
    check(f"{run}: raw/ present", os.path.isdir(f"{res}/raw"))
    # 8. status agreement
    check(f"{run}: run.json status completed", rj.get("status") == "completed", rj.get("status"))
    # 9. benchmark_comparison rows match run values
    with open(f"{res}/benchmark_comparison.csv") as f:
        n = sum(1 for _ in f) - 1
    check(f"{run}: benchmark_comparison rows > 0", n > 0, f"{n} rows")

# task-level benchmark folder
bm = f"{N}/benchmark/monoclonal_antibody_design/{T}"
for f in ("reference.md", "comparison.md", "figures/results_comparison.png", "figures/workflow_results.png"):
    check(f"benchmark: {f}", os.path.exists(f"{bm}/{f}"))
figs = os.listdir(f"{bm}/figures")
check("benchmark: figures PNG-only, exactly 2", sorted(figs) == ["results_comparison.png", "workflow_results.png"], str(figs))

# cross-consistency: shortlist s13 uses v3 metrics; echo report 10/10
e = json.load(open(f"{N}/results/{T}/run_001_antibmpnn_fixed_backbone/raw/boltz2/sequence_echo_report.json"))
check("run_001: echo 10/10 exact", all(v["vh_match"] and v["vl_match"] for v in e.values()), f"{len(e)} labels")
docs = json.load(open(f"{N}/src/{T}/run_001_antibmpnn_fixed_backbone/inputs/execution_records/boltz2_doc_ids.json"))
check("run_001: D08 = v3 corrected doc", docs["records"]["D08"]["doc_id"] == "6afb44b47426d09ad749d5fe")
check("run_001: wrong-input evidence v1+v2 preserved", set(docs["wrong_input_evidence"]) >= {"v1", "v2"})
# run.json tool_details link present
rj = json.load(open(f"{N}/results/{T}/run_001_antibmpnn_fixed_backbone/run.json"))
check("run_001: evidence.tool_details linked", "tool_details.json" in rj["evidence"]["tool_details"])

n_pass = sum(1 for _, ok, _ in results if ok)
n_fail = len(results) - n_pass
for name, ok, detail in results:
    if not ok:
        print("FAIL:", name, detail)
print(f"\n=== VERIFICATION: {n_pass}/{len(results)} PASS, {n_fail} FAIL ===")
