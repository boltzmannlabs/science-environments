"""Host-only CLI configuration for persistent Small Molecule candidate episodes."""
def add_handoff_command(commands):
    child = commands.add_parser('handoff', help='Run a local persistent Small Molecule candidate handoff')
    for name in ('input', 'output', 'output-dir', 'scientist-python', 'scientist-source'):
        child.add_argument('--' + name, required=True)
    for name in ('profile-home', 'repo-root', 'chemistry-python', 'science-config',
                 'orchestration-policy', 'condition-model', 'cn-condition-model', 'reaction-yield-model'):
        child.add_argument('--' + name)
    child.add_argument('--method', choices=('main', 'main_strategist', 'main_route_critic',
        'main_role_prompt', 'main_all_advisors', 'main_adaptive'), default='main')
    child.add_argument('--model-calls', type=int)
    child.add_argument('--budget-regime', choices=('budgeted','unbudgeted'))
    child.add_argument('--timeout', type=float, default=60)
    child.add_argument('--resume', action='store_true')
    child.add_argument('--impurity-model', action='store_true')
    child.add_argument('--impurity-device', choices=('cpu', 'cuda'), default='cpu')


def execute_handoff(args):
    from .cli import load_json
    from .handoff import SmallMoleculeHandoff
    from .handoff_runner import run_handoff
    from .science_config import load_science_config
    from .adapters import LocalRetroAdapter
    from .host_policy import task_regime, science_regime, tool_timeout, host_allowance
    from .handoff import build_handoff_task
    payload = SmallMoleculeHandoff.model_validate(load_json(args.input))
    task = task_regime(build_handoff_task(payload), args.budget_regime)
    payload = payload.model_copy(update={'budget':task.budget})
    args.model_calls = host_allowance(args.model_calls, task.budget.regime, 24, 'Model-call allowance')
    timeout = tool_timeout(args.timeout, payload.budget.max_wall_seconds)
    adapter = LocalRetroAdapter(repo_root=args.repo_root, python_executable=args.chemistry_python,
                                timeout_seconds=timeout)
    options = load_science_config(args.science_config) if args.science_config else {}
    options = {**science_regime(options, task.budget.regime), 'expand': adapter.expand}
    if args.condition_model:
        from .ranking import ConditionRanker
        options = {**options, 'condition_ranker': ConditionRanker.load(args.condition_model)}
    if args.cn_condition_model:
        from .cn_model import CNConditionModel
        options = {**options, 'cn_condition_model': CNConditionModel.load(args.cn_condition_model)}
    if args.reaction_yield_model:
        from .public_yield import ReactionT5YieldPredictor
        options = {**options, 'reaction_yield_predictor': ReactionT5YieldPredictor.from_manifest(args.reaction_yield_model)}
    if args.impurity_model:
        from .adapters.impurity_local import LocalImpurityAdapter
        options = {**options, 'impurity': LocalImpurityAdapter(repo_root=args.repo_root,
            python_executable=args.chemistry_python, timeout_seconds=timeout, device=args.impurity_device)}
    return run_handoff(args, payload, args.output_dir, resume=args.resume, environment_options=options)
