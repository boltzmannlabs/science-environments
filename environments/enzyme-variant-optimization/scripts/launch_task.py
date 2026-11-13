"""Prepare a native SCI task prompt; start only with explicit --start."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--approach", choices=("agent_alone", "agent_with_specialist"), required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--start", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"task_\d{3}_[a-z0-9_]+", args.task) or not re.fullmatch(r"v[1-9]\d*", args.version):
        parser.error("Use a numbered task ID and configuration version such as v1.")
    env = Path(__file__).resolve().parents[1]
    config = env / "config" / args.task / args.version / (args.approach + ".json")
    if not config.is_file():
        parser.error("This task/version/approach has no selected configuration.")
    settings = json.loads(config.read_text())
    model = settings.get("llm", {}).get("model")
    if not model:
        parser.error("The configuration has no selected model; choose and freeze settings first.")
    workspace = args.run_dir.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    query = workspace / "START_SCI_TASK.txt"
    prepared = workspace / "PREPARED_LAUNCH.json"
    intent = workspace / "LAUNCH_INTENT.json"
    if intent.exists() or any(workspace.glob("jobs*.json")) or (workspace / "RUN_PLAN.json").exists():
        parser.error("Existing run workspace: use its native SCI resume ID; do not relaunch.")
    body = (f"Execute {env / 'tasks' / (args.task + '.md')} with {config}.\n"
                     f"Read ENVIRONMENT_SPEC.md and MODELS_AND_TOOLS.md in {env}. Work only in {workspace}.\n"
                     "Consult current native tool contracts, freeze actual effective settings and inputs, "
                     "execute the full task-specific scope and preserve all outputs/failures/accounting. "
                     "Exclude MLDE. Do not duplicate pending or acceptance-unknown jobs. "
                     "Agent-alone uses no specialists; assisted uses the reviewed native saved proposer/critic. "
                     "Keep paper winner/reference files and other-arm outputs outside design inputs. "
                     "Do not claim improvement or completion without actual evidence.\n")
    if prepared.exists():
        saved = json.loads(prepared.read_text())
        if (saved.get("task"), saved.get("version"), saved.get("approach")) != (args.task, args.version, args.approach):
            parser.error("Prepared workspace belongs to different settings.")
        if not query.is_file() or query.read_text() != body or saved["config_sha256"] != hashlib.sha256(config.read_bytes()).hexdigest():
            parser.error("Prepared inputs changed; review and prepare a new workspace.")
    else:
        if any(workspace.iterdir()):
            parser.error("Use an empty fresh workspace or the matching prepared-launch manifest.")
        query.write_text(body)
        prepared.write_text(json.dumps({"task": args.task, "version": args.version, "approach": args.approach,
                                       "config_sha256": hashlib.sha256(config.read_bytes()).hexdigest()}, indent=2) + "\n")
    command = ["sci", "--cli", "--no-daemon", "--no-restore-cwd", "chat", "--query-file=" + str(query),
               "--model", model, "--provider", settings["llm"].get("provider", "openai-codex"),
               "--reasoning", settings["llm"].get("reasoning_effort", "xhigh"), "--max-turns", "1000",
               "--toolsets", "web,file,terminal,skills,todo,code_execution,boltzmann,tooluniverse" +
               (",delegation" if args.approach == "agent_with_specialist" else ""), "--pass-session-id"]
    print(shlex.join(command))
    print("Fresh-run command only. For an existing run use sci --resume <native-session-id>.")
    if args.start:
        intent.write_text(json.dumps({"command": command, "state": "start_requested_reconcile_before_any_retry"}, indent=2) + "\n")
        subprocess.run(command, cwd=env, check=True)


if __name__ == "__main__":
    main()
