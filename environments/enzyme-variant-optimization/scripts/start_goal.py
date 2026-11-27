"""Start an environment task through native SCI command handling."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sci-source", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--goal-file", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--reasoning", required=True)
    parser.add_argument("--assisted", action="store_true")
    args = parser.parse_args()
    if not sys.stdin.isatty():
        parser.error("Native interactive goal startup requires a terminal.")
    source = args.sci_source.resolve()
    if not (source / "cli.py").is_file():
        parser.error("SCI source must contain cli.py.")
    workspace = args.run_dir.resolve()
    if not workspace.is_dir():
        parser.error("The prepared run directory does not exist.")
    os.chdir(workspace)
    sys.path.insert(0, str(source))
    import sci_bootstrap  # Standard SCI dependency/runtime bootstrap, including managed interpreters.
    from sci_cli.profiles import get_profile_dir, profile_exists
    if args.profile in {"default", "main"} or not profile_exists(args.profile):
        parser.error("Select an existing dedicated execution profile.")
    os.environ["SCI_HOME"] = str(get_profile_dir(args.profile))
    from sci_cli.config import load_config_readonly
    config = load_config_readonly()
    if (config.get("goals") or {}).get("max_turns", 20) != 20:
        parser.error("This launch requires the retained goals.max_turns=20 setting.")
    if args.assisted:
        from agent.specialist_store import load
        for role in ("method", "recovery", "evaluator"):
            item = load(f"enzyme-{role}")
            info = item.package_info or {}
            if info.get("version") != "1.2.0" or info.get("state") != "ready" or not item.enabled:
                parser.error(f"Install and review enzyme-{role} 1.2.0 in this profile first.")
        coordinator = Path(os.environ["SCI_HOME"]) / "skills/enzyme-coordinator/SKILL.md"
        if not coordinator.is_file() or "version: 1.2.0" not in coordinator.read_text():
            parser.error("Install the reviewed enzyme-coordinator 1.2.0 skill first.")
    query_path = args.goal_file.resolve()
    if query_path.parent != workspace:
        parser.error("The goal file must be in the prepared workspace.")
    manifest = json.loads((workspace / "PREPARED_LAUNCH.json").read_text())
    if (manifest.get("profile"), manifest.get("sci_source"), manifest.get("sci_python")) != (
        args.profile, str(source), str(Path(sys.executable).absolute())
    ):
        parser.error("Profile, source or interpreter differs from the prepared launch.")
    effective = (args.model, args.provider, args.reasoning, args.assisted)
    expected = (manifest.get("model"), manifest.get("provider"), manifest.get("reasoning"),
                manifest.get("approach") == "agent_with_specialist")
    if effective != expected:
        parser.error("Model, provider, reasoning or approach differs from the prepared launch.")
    settings_path = Path(manifest["settings_path"])
    if hashlib.sha256(settings_path.read_bytes()).hexdigest() != manifest.get("config_sha256"):
        parser.error("The frozen settings changed; prepare a fresh reviewed workspace.")
    text = query_path.read_text()
    if manifest.get("goal_sha256") != hashlib.sha256(text.encode()).hexdigest():
        parser.error("The prepared goal changed; review and prepare a fresh workspace.")
    if not text.startswith("/goal "):
        parser.error("The prepared file must contain the native /goal command.")
    intent = workspace / "LAUNCH_INTENT.json"
    try:
        with intent.open("x") as stream:
            json.dump({"state": "start_requested_reconcile_before_any_retry", "profile": args.profile,
                       "sci_source": str(source)}, stream, indent=2)
    except FileExistsError:
        parser.error("A launch was already attempted. Reconcile its native session and resume it.")
    import cli as cli_module
    if Path(cli_module.__file__).resolve() != source / "cli.py":
        parser.error("SCI imported a different source checkout. Reconcile this attempt before retrying.")
    from cli import _build_cli_from_args
    toolsets = ["web", "file", "terminal", "skills", "todo", "code_execution", "boltzmann"]
    # MCP names are profile-specific: preserve the configured spelling, e.g. tool_universe.
    for name, entry in (config.get("mcp_servers") or {}).items():
        if (isinstance(entry, dict) and entry.get("enabled", True)
                and re.sub(r"[^a-z0-9]", "", name.lower()) == "tooluniverse"):
            toolsets.append(name)
    if args.assisted:
        toolsets.append("delegation")
    cli = _build_cli_from_args(
        model=args.model, provider=args.provider, reasoning=args.reasoning,
        toolsets=",".join(toolsets),
        api_key=None, base_url=None, max_turns=None, run_budget=None,
        verbose=None, compact=None, resume=None, checkpoints=False,
        pass_session_id=True, ignore_rules=False,
        skills="enzyme-coordinator" if args.assisted else None,
    )
    with intent.open("w") as stream:
        json.dump({"state": "native_session_created", "session_id": cli.session_id,
                   "profile": args.profile, "sci_source": str(source)}, stream, indent=2)
    # Plain queued commands reach slash routing. _SeededQueryMessage bypasses it.
    cli._seeded_first_message = text
    cli.run()


if __name__ == "__main__":
    main()
