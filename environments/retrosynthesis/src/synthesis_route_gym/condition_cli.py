"""Local condition workflow entrypoints; private study paths remain host-only."""
from pathlib import Path


def add_condition_commands(commands):
    for name in ('condition-plan','condition-agent'):
        child=commands.add_parser(name,help='Choose conditions through finite measured replay')
        child.add_argument('--study',required=True,help='Public registered condition-study JSON')
        child.add_argument('--outcomes',required=True,help='Host-private committed replay JSON; never exposed to the LLM')
        child.add_argument('--predictions',help='Pinned precomputed prediction table shared across methods')
        child.add_argument('--output',required=True)
        child.add_argument('--episode-dir',help='New local checkpoint directory; defaults to OUTPUT.episode')
        child.add_argument('--budget-regime',choices=('budgeted','unbudgeted'),default='budgeted')
        child.add_argument('--max-actions',type=int)
        child.add_argument('--wall-seconds',type=float)
        if name=='condition-agent':
            child.add_argument('--method',choices=('main','main_condition_scientist'),default='main')
            child.add_argument('--scientist-python',required=True)
            child.add_argument('--scientist-source',required=True)
            child.add_argument('--profile-home')
            child.add_argument('--model-calls',type=int)
            child.add_argument('--max-tokens',type=int)
            child.add_argument('--resume',action='store_true')
        else:
            child.add_argument('--policy',choices=('fixed_order','random','public_model_rank',
                                                  'gp_expected_improvement'),default='fixed_order')
            child.add_argument('--seed',type=int,default=0)


def execute_condition(args):
    from .condition_io import load_condition_inputs
    from .condition_episode import ConditionEpisode
    from .host_policy import host_allowance
    from dataclasses import replace
    regime = getattr(args,'budget_regime','budgeted')
    args.max_actions = host_allowance(args.max_actions,regime,80,'Action allowance')
    args.wall_seconds = host_allowance(args.wall_seconds,regime,600,'Wall allowance')
    if args.command == 'condition-agent':
        args.model_calls = host_allowance(args.model_calls,regime,24,'Model-call allowance')
        args.max_tokens = host_allowance(args.max_tokens,regime,350000,'Token allowance')
    inputs=load_condition_inputs(args.study,args.outcomes,args.predictions)
    if regime == 'unbudgeted':
        inputs = {**inputs,'study':replace(inputs['study'],budget=None)}
    root=Path(args.episode_dir or (str(args.output)+'.episode'))
    options={key:inputs[key]for key in ('study_id','target','predictions')}
    options={**options,'max_actions':args.max_actions,'wall_seconds':args.wall_seconds,'regime':regime}
    resume=getattr(args,'resume',False)
    if resume:
        episode=ConditionEpisode.resume(root/'environment',inputs['study'],**options)
    else:
        episode=ConditionEpisode(inputs['study'],store=root/'environment',**options)
    if args.command=='condition-agent':
        from .condition_session import run_condition_agent
        return run_condition_agent(args,episode,root/'runtime',resume=resume)
    from .condition_benchmark import run_fixed_condition_episode
    return run_fixed_condition_episode(episode,args.policy,seed=args.seed)
