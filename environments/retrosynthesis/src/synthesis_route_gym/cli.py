"""Local command-line research interface. No command submits cloud science jobs."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
from .schemas import Task, RouteCandidate
from .validation import assess_route


def load_json(path):
    path = Path(path)
    if path.stat().st_size > 20_000_000:
        raise ValueError("Input exceeds the 20 MB local task limit")
    return json.loads(path.read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, allow_nan=False) + "\n"
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, prefix=".srg-") as file:
        file.write(payload)
        temporary = Path(file.name)
    temporary.replace(path)


def _parser():
    parser = argparse.ArgumentParser(prog="retrosynthesis")
    commands = parser.add_subparsers(dest="command", required=True)
    from .condition_cli import add_condition_commands
    add_condition_commands(commands)
    from .handoff_cli import add_handoff_command
    add_handoff_command(commands)
    for command in ("validate", "plan", "replay", "agent"):
        child = commands.add_parser(command)
        child.add_argument("--task", required=True)
        child.add_argument("--output", required=True)
        child.add_argument("--budget-regime", choices=("budgeted", "unbudgeted"))
        if command != "validate":
            child.add_argument("--condition-model", help="Host-controlled local JSON scientific model artifact")
            child.add_argument("--cn-condition-model", help="Optional host JSON C-N screening-hit model; separate from Doyle yield prediction")
            child.add_argument("--reaction-yield-model", help="Explicit local public-yield model manifest; no automatic download")
            child.add_argument("--science-config", help="Host-only versioned source/replay configuration; never a model tool argument")
        if command != "validate":
            child.add_argument("--impurity-model", action="store_true", help="Opt in to the existing local REBOLT impurity checkpoint")
            child.add_argument("--impurity-device", choices=("cpu","cuda"), default="cpu")
        if command == "validate":
            child.add_argument("--route", required=True)
        elif command == "replay":
            child.add_argument("--actions", required=True)
            child.add_argument("--repo-root")
            child.add_argument("--chemistry-python")
            child.add_argument("--timeout", type=float, default=60)
        else:
            child.add_argument("--repo-root")
            child.add_argument("--chemistry-python")
            child.add_argument("--timeout", type=float, default=60)
            child.add_argument("--seed", type=int, default=0)
        if command == "agent":
            child.add_argument("--scientist-python", required=True)
            child.add_argument("--scientist-source", required=True)
            child.add_argument("--profile-home")
            child.add_argument("--method", choices=("main", "specialists", "main_strategist", "main_route_critic",
                               "main_role_prompt", "main_all_advisors", "main_adaptive"), default="main")
            child.add_argument("--orchestration-policy", help="Host-only experimental advisor policy JSON; main-only remains default")
            child.add_argument("--model-calls", type=int)
            child.add_argument("--episode-dir", help="Host-owned local checkpoint directory; defaults to OUTPUT.episode")
            child.add_argument("--resume", action="store_true", help="Resume the same task/configuration without resetting resources")
        if command == "plan":
            child.add_argument("--search-policy", choices=("breadth_first", "best_first",
                               "synthchem_portfolio", "synthchem_astar", "synthchem_mcts"),
                               default="synthchem_portfolio", help="SynthChem portfolio by default; older policies remain selectable")
            child.add_argument("--expansion-backend", choices=("localretro", "aizynthfinder"),
                               default="localretro", help="Single-step proposal source; independent of search policy")
            child.add_argument("--aizynth-config", help="Host model configuration required for the aizynthfinder backend")
            child.add_argument("--expansion-top-k", type=int, default=10)
            child.add_argument("--max-frontier-states", type=int,
                               help="Frontier/state cap; native graph node cap for SynthChem policies")
    child = commands.add_parser("predict-yield", help="Predict supplied reaction yields through a budgeted local episode")
    child.add_argument('--budget-regime', choices=('budgeted','unbudgeted'))
    for option in ("task", "model", "input", "output"):
        child.add_argument("--" + option, required=True)
    for command in ("portfolio", "review-queue", "evaluate", "enrich-rebolt"):
        child = commands.add_parser(command)
        child.add_argument("--input", required=True)
        child.add_argument("--output", required=True)
        if command == "evaluate":
            child.add_argument("--reviews", required=True)
        if command == "enrich-rebolt":
            child.add_argument("--task", required=True)
    return parser


def _agent(args, env):
    from .agent_session import run_persistent_agent
    root = Path(args.episode_dir or (str(args.output) + '.episode'))
    return run_persistent_agent(args, env, root / 'runtime', resume=args.resume)


def execute(args):
    if args.command == 'handoff':
        from .handoff_cli import execute_handoff
        return execute_handoff(args)
    if args.command in {"condition-plan", "condition-agent"}:
        from .condition_cli import execute_condition
        return execute_condition(args)
    if args.command == "predict-yield":
        from .environment import SynthesisRouteEnv
        from .public_yield import ReactionT5YieldPredictor
        from .host_policy import task_regime, science_regime, tool_timeout, host_allowance
        task = task_regime(Task.model_validate(load_json(args.task)), getattr(args, 'budget_regime', None))
        predictor = ReactionT5YieldPredictor.from_manifest(args.model)
        env = SynthesisRouteEnv(task, reaction_yield_predictor=predictor)
        result = env.dispatch("predict_reaction_yield", load_json(args.input))
        return {"action_result": result, "episode": env.export()}
    if args.command in {"validate", "plan", "replay", "agent"}:
        from .environment import SynthesisRouteEnv
        from .host_policy import task_regime, science_regime, tool_timeout, host_allowance
        task = task_regime(Task.model_validate(load_json(args.task)), getattr(args, 'budget_regime', None))
        if args.command == 'agent':
            args.model_calls = host_allowance(args.model_calls, task.budget.regime, 24, 'Model-call allowance')
        if args.command == 'plan':
            args.max_frontier_states = host_allowance(args.max_frontier_states, task.budget.regime, 10000, 'Frontier cap')
        if args.command == "validate":
            return assess_route(task, RouteCandidate.model_validate(load_json(args.route))).model_dump(mode="json")
        expand = None
        if args.command in {"plan", "agent"}:
            from .adapters import AiZynthFinderAdapter, LocalRetroAdapter
            timeout = tool_timeout(args.timeout, task.budget.max_wall_seconds)
            if args.command == "plan" and args.expansion_backend == "aizynthfinder":
                if not args.aizynth_config:
                    raise ValueError("The aizynthfinder backend requires --aizynth-config")
                if not Path(args.aizynth_config).is_file():
                    raise ValueError("AiZynthFinder model configuration does not exist")
                adapter = AiZynthFinderAdapter(config_path=args.aizynth_config,
                    python_executable=args.chemistry_python or sys.executable, timeout_seconds=timeout)
            else:
                adapter = LocalRetroAdapter(repo_root=args.repo_root, python_executable=args.chemistry_python,
                                            timeout_seconds=timeout)
            expand = adapter.expand
        from .ranking import ConditionRanker
        model_path = getattr(args, "condition_model", None)
        condition_ranker = ConditionRanker.load(model_path) if model_path else None
        cn_path = getattr(args, "cn_condition_model", None)
        cn_model = None
        if cn_path:
            from .cn_model import CNConditionModel
            cn_model = CNConditionModel.load(cn_path)
        yield_path = getattr(args, "reaction_yield_model", None)
        yield_predictor = None
        if yield_path:
            from .public_yield import ReactionT5YieldPredictor
            yield_predictor = ReactionT5YieldPredictor.from_manifest(yield_path)
        from .science_config import load_science_config
        science = load_science_config(args.science_config) if args.science_config else {}
        if getattr(args,"impurity_model",False):
            from .adapters.impurity_local import LocalImpurityAdapter
            science = {**science,"impurity":LocalImpurityAdapter(repo_root=args.repo_root,
                python_executable=args.chemistry_python,timeout_seconds=tool_timeout(args.timeout,task.budget.max_wall_seconds),
                device=args.impurity_device)}
        science = science_regime(science, task.budget.regime)
        if args.command == "agent":
            store = Path(args.episode_dir or (str(args.output) + '.episode')) / 'environment'
            if args.resume:
                env = SynthesisRouteEnv.resume(store, expected_task=task, expand=expand,
                                               condition_ranker=condition_ranker, cn_condition_model=cn_model,
                                               reaction_yield_predictor=yield_predictor, **science)
            else:
                env = SynthesisRouteEnv(task, seed=args.seed, expand=expand,
                                        condition_ranker=condition_ranker, cn_condition_model=cn_model,
                                        reaction_yield_predictor=yield_predictor, store=store, **science)
        else:
            env = SynthesisRouteEnv(task, seed=getattr(args, "seed", 0), expand=expand,
                                    condition_ranker=condition_ranker, cn_condition_model=cn_model,
                                    reaction_yield_predictor=yield_predictor, **science)
        if args.command == "plan":
            if args.search_policy.startswith("synthchem_"):
                from .synthchem_search import run_synthchem_workflow
                return run_synthchem_workflow(env, algorithm=args.search_policy.removeprefix("synthchem_"),
                                             expansion_top_k=args.expansion_top_k,
                                             max_graph_nodes=args.max_frontier_states)
            from .planning import run_fixed_workflow
            from .fixed_search import run_best_first_workflow
            policy = run_best_first_workflow if args.search_policy == "best_first" else run_fixed_workflow
            return policy(env, expansion_top_k=args.expansion_top_k,
                          max_frontier_states=args.max_frontier_states)
        if args.command == "agent":
            return _agent(args, env)
        for action in load_json(args.actions):
            env.dispatch(action["action"], action.get("arguments", {}))
        return env.export()
    if args.command == "portfolio":
        from .portfolio import dispatch_portfolio
        def validate(payload):
            return assess_route(Task.model_validate(payload["task"]), RouteCandidate.model_validate(payload["route"])).model_dump(mode="json")
        return dispatch_portfolio(load_json(args.input), inventory_validator=validate)
    if args.command == "review-queue":
        from .benchmark import review_queue
        return review_queue(load_json(args.input))
    if args.command == "enrich-rebolt":
        from .rebolt_bridge import enrich_rebolt_paths
        paths, review = enrich_rebolt_paths(load_json(args.input), Task.model_validate(load_json(args.task)))
        return {"paths": paths, "review_bundle": review}
    from .benchmark import evaluate_episode
    reviews = load_json(args.reviews)
    return [{"method": run["method"], **evaluate_episode(run["episode"], reviews)} for run in load_json(args.input)]


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        result = execute(args)
        write_json(args.output, result)
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    status = result["action_result"]["status"] if args.command == "predict-yield" else "ok"
    if args.command in {"condition-agent", "condition-plan"}:
        submitted = result.get("episode", {}).get("submission", {}).get("status")
        if submitted not in {"selected", "abstained"}:
            status = "incomplete"
    print(json.dumps({"status": status, "output": str(Path(args.output).resolve())}))
    return 0 if status == "ok" else 1
