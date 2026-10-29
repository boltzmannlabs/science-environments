"""Host-owned persistent agent sessions, bound to one task and runtime configuration."""
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from .agent_bridge import BridgeError, run_agent_scientist_bridge
from .agent_runner import AgentBudget, resolve_main_profile, _validated_schemas
from .episode_store import EpisodeStore
from .observation import task_prompt
from .planning import environment_tool_schemas


def _tool_binding(args, env):
    model = getattr(args, 'condition_model', None)
    model_path = Path(model).expanduser().resolve() if model else None
    package = Path(__file__).parent
    # Runtime changes require an explicit migration, never silent resume.
    sources = sorted(package.glob('*.py')) + sorted((package / 'adapters').glob('*.py'))
    return {
        'version': 'srg-host-tools-v1',
        'seed': getattr(args, 'seed', env.seed),
        'repo_root': str(Path(args.repo_root).expanduser().resolve()) if getattr(args, 'repo_root', None) else None,
        'chemistry_python': str(Path(args.chemistry_python).expanduser().resolve()) if getattr(args, 'chemistry_python', None) else None,
        'adapter_timeout_seconds': getattr(args, 'timeout', None),
        'condition_model_path': str(model_path) if model_path else None,
        'condition_model_sha256': hashlib.sha256(model_path.read_bytes()).hexdigest() if model_path else None,
        'implementation_hashes': {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    }


def _orchestration_policy(args):
    path = getattr(args, 'orchestration_policy', None)
    modes = {'main_role_prompt', 'main_all_advisors', 'main_adaptive'}
    if args.method not in modes:
        if path is not None:
            raise ValueError('Orchestration policy requires an orchestration mode')
        return None
    from .orchestration import normalize_policy
    value = None
    if path is not None:
        with Path(path).open('rb') as stream:
            raw = stream.read(100001)
        if len(raw) > 100000:
            raise ValueError('Orchestration policy exceeds input bound')
        value = json.loads(raw)
    return normalize_policy(args.method, value)


def run_persistent_agent(args, env, runtime_path, *, resume=False, prompt=None, tool_schemas=None):
    if env.task.budget.regime == 'unbudgeted' and args.model_calls is not None:
        raise ValueError('Unbudgeted episodes cannot impose a model-call allowance')
    profile = resolve_main_profile(args.profile_home)
    orchestration_policy = _orchestration_policy(args)
    selected_prompt = task_prompt(env) if prompt is None else prompt
    if not isinstance(selected_prompt, str) or not selected_prompt.strip() or len(selected_prompt) > 100000:
        raise ValueError('Host task prompt must be a bounded nonempty string')
    selected_schemas = _validated_schemas(environment_tool_schemas() if tool_schemas is None else tool_schemas)
    limits = (AgentBudget.unbudgeted() if env.task.budget.regime == 'unbudgeted' else
              AgentBudget(max_model_calls=args.model_calls, max_tool_calls=env.task.budget.max_actions,
                         wall_seconds=env.task.budget.max_wall_seconds,
                         max_total_tokens=env.task.budget.max_llm_tokens))
    binding = {'task_sha256': env._task_sha256, 'mode': args.method, 'budget': asdict(limits),
               'tools': _tool_binding(args, env),
               'scientific_registry': env._scientific_tools.fingerprint,
               'application_configuration':env._application_fingerprint,
               'source_access_mode':env._source_access_mode,
               'scientific_limits': asdict(env._scientific_limits),
               'scientist_python': str(Path(args.scientist_python).resolve()),
               'scientist_source': str(Path(args.scientist_source).resolve()),
               'profile_home': str(profile.home),
               'profile': {'model':profile.model, 'provider':profile.provider},
               'prompt_sha256':hashlib.sha256(selected_prompt.encode()).hexdigest(),
               'tool_schemas_sha256':hashlib.sha256(json.dumps(selected_schemas,sort_keys=True,allow_nan=False).encode()).hexdigest()}
    if orchestration_policy is not None:
        binding = {**binding, 'orchestration_policy': orchestration_policy}
    store = EpisodeStore(runtime_path)
    if resume:
        record, revision = store.load()
        if record.get('binding') != binding:
            raise ValueError('Runtime checkpoint binding differs from requested configuration')
    else:
        record = {'binding': binding, 'runtime': None, 'result': None}
        revision = store.initialize(record)

    def checkpoint(state):
        nonlocal record, revision
        new_record = {**record, 'runtime': state}
        revision = store.commit(new_record, expected_revision=revision)
        record = new_record

    if (env.task.budget.max_wall_seconds is not None
            and env._usage_dict()["wall_seconds"] >= env.task.budget.max_wall_seconds):
        env.cancel("episode_deadline_expired")
    state = env.inspect()
    identity = {'model':profile.model, 'provider':profile.provider,
                'identity_source':'frozen session main-profile binding'}
    if state['terminated'] or state['truncated']:
        result = record.get('result') or {**identity,'completed':False,'stop_reason':'episode_already_closed',
                                         'resource_accounting':'no_new_provider_request'}
    else:
        try:
            result = run_agent_scientist_bridge(selected_prompt, env.dispatch,
                tool_schemas=selected_schemas, scientist_python=args.scientist_python,
                scientist_source=args.scientist_source, profile_home=args.profile_home,
                mode=args.method, budget=limits, resume_state=record['runtime'],
                orchestration_policy=orchestration_policy,
                checkpoint=checkpoint, cancel=env.cancel, action_executor=env.dispatch,
                remaining_seconds=(None if env.task.budget.max_wall_seconds is None else
                    max(0.001, env.task.budget.max_wall_seconds - env._usage_dict()["wall_seconds"])),
                cancelled=lambda: env.inspect()['truncated'])
        except BridgeError as exc:
            # Details can contain runtime/provider values. Preserve safe type and host state.
            result = {**identity,'completed':False,'error_type':type(exc).__name__,
                      'stop_reason':'bridge_interrupted','resource_accounting':'unknown_after_bridge_interruption'}
        record = {**record, 'result': result}
        store.commit(record, expected_revision=revision)
    episode = env.export()
    status = ('submitted_routes' if episode['submitted_route_ids'] else 'submitted_empty') if episode['terminated'] else 'not_submitted'
    return {'method': args.method, 'agent': result, 'episode': episode,
            'submission_status': status, 'runtime_checkpoint': record['runtime']}
