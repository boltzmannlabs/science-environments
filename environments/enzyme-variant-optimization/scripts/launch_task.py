"""Prepare a native SCI task prompt; start only with explicit --start."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--settings", type=Path, required=True,
                        help="Explicit frozen launch settings; compact historical configs are not launch profiles.")
    parser.add_argument("--approach", choices=("agent_alone", "agent_with_specialist"), required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--profile", required=True, help="Dedicated SCI profile with reviewed specialist packages.")
    parser.add_argument("--sci-python", type=Path, required=True, help="Python from the reviewed SCI runtime.")
    parser.add_argument("--sci-source", type=Path, required=True, help="Reviewed SCI checkout containing cli.py.")
    parser.add_argument("--contract-root", type=Path, action="append", default=[], help="Approved read-only catalog/contract directory; repeat for additional connectors.")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", args.profile):
        parser.error("Use a valid dedicated SCI profile name.")
    if args.start and not sys.stdin.isatty():
        parser.error("Start the printed command in an interactive terminal so SCI handles /goal natively.")
    if not re.fullmatch(r"task_\d{3}_[a-z0-9_]+", args.task):
        parser.error("Use a numbered task ID.")
    env = Path(__file__).resolve().parents[1]
    if not (env / "tasks" / (args.task + ".md")).is_file():
        parser.error("The numbered task does not exist in this environment.")
    if not args.sci_python.is_file() or not (args.sci_source / "cli.py").is_file():
        parser.error("Select an existing SCI interpreter and source checkout.")
    config = args.settings.resolve()
    if not config.is_file():
        parser.error("The supplied frozen settings file does not exist.")
    settings = json.loads(config.read_text())
    model = settings.get("llm", {}).get("model")
    if not model:
        parser.error("The configuration has no selected model; choose and freeze settings first.")
    contract_roots = args.contract_root or [args.sci_source / "plugins/boltzmann/skills/boltzmann-tools/references"]
    if args.approach == "agent_with_specialist" and any(not p.is_dir() for p in contract_roots):
        parser.error("Supply existing approved catalog directories with --contract-root.")
    workspace = args.run_dir.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    query = workspace / "START_SCI_TASK.txt"
    prepared = workspace / "PREPARED_LAUNCH.json"
    intent = workspace / "LAUNCH_INTENT.json"
    if intent.exists() or any(workspace.glob("jobs*.json")) or (workspace / "RUN_PLAN.json").exists():
        parser.error("Existing run workspace: use its native SCI resume ID; do not relaunch.")
    body = (f"/goal Execute {env / 'tasks' / (args.task + '.md')} with {config}.\n"
                     f"Read {env / 'ENVIRONMENT_SPEC.md'} and {env / 'MODELS_AND_TOOLS.md'}. Work only in {workspace}.\n"
                     "Consult current native tool contracts, freeze actual effective settings and inputs, "
                     "execute the full task-specific scope and preserve all outputs/failures/accounting. "
                     "Exclude MLDE. Do not duplicate pending or acceptance-unknown jobs. "
                     "Agent-alone uses no specialists. "
                     "Keep paper winner/reference files and other-arm outputs outside design inputs. "
                     "Do not claim improvement or completion without actual evidence.\n")
    if args.approach == "agent_with_specialist":
        body += ("Use the enzyme-coordinator skill and saved enzyme-method, enzyme-recovery and enzyme-evaluator specialists. "
                 "Use intermediate delivery for actionable reviews and save their actual receipts. "
                 "Discover authorized tools from the current catalog and contracts. "
                 "Finish all mandatory stages and independent evidence review, including honest negative outcomes.\n")
    if args.approach == "agent_with_specialist":
        body += "Approved read-only catalog and contract directories: " + ", ".join(str(p.resolve()) for p in contract_roots) + ".\n"
    body += "Retain SCI goals.max_turns=20 and verify the saved native goal is active.\n"
    if prepared.exists():
        saved = json.loads(prepared.read_text())
        if (saved.get("task"), saved.get("approach"), saved.get("profile")) != (args.task, args.approach, args.profile):
            parser.error("Prepared workspace belongs to different settings.")
        if not query.is_file() or query.read_text() != body or saved["config_sha256"] != hashlib.sha256(config.read_bytes()).hexdigest():
            parser.error("Prepared inputs changed; review and prepare a new workspace.")
    else:
        if any(workspace.iterdir()):
            parser.error("Use an empty fresh workspace or the matching prepared-launch manifest.")
        query.write_text(body)
        prepared.write_text(json.dumps({"task": args.task, "approach": args.approach,
                                       "profile": args.profile, "settings_path": str(config), "model": model,
                                       "provider": settings["llm"].get("provider", "openai-codex"),
                                       "reasoning": settings["llm"].get("reasoning_effort", "xhigh"), "sci_source": str(args.sci_source.resolve()),
                                       "sci_python": str(args.sci_python.absolute()),
                                       "goal_sha256": hashlib.sha256(body.encode()).hexdigest(), "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest()}, indent=2) + "\n")
    command = [str(args.sci_python.absolute()), str(env / "scripts" / "start_goal.py"),
               "--sci-source", str(args.sci_source.resolve()), "--profile", args.profile,
               "--goal-file", str(query), "--run-dir", str(workspace), "--model", model,
               "--provider", settings["llm"].get("provider", "openai-codex"),
               "--reasoning", settings["llm"].get("reasoning_effort", "xhigh")]
    if args.approach == "agent_with_specialist":
        command.append("--assisted")
    print(shlex.join(command))
    print("Confirm SCI reports Goal set and /goal status shows an active goal with 20 turns. Use native /background for persistence.")
    print("Fresh-run command only. For an existing run use sci --resume <native-session-id>.")
    if args.start:
        subprocess.run(command, cwd=workspace, check=True)


if __name__ == "__main__":
    main()
