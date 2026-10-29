"""Same main search policy with a pinned pretrained yield tool available or absent."""
import hashlib
from pathlib import Path
from . import development_runner as runner


def load_predictor(path):
    from .public_yield import ReactionT5YieldPredictor
    return ReactionT5YieldPredictor.from_manifest(path)


def make_model_search_plan(selection, inputs, runtime):
    manifest = runtime.get('reaction_yield_model_manifest')
    if not isinstance(manifest,str) or not manifest:
        raise ValueError('A pinned local yield manifest is required')
    model_hash = runner.digest(manifest)
    if runtime.get('model_manifest_sha256',model_hash) != model_hash:
        raise ValueError('Model manifest integrity mismatch')
    runtime = {**runtime,'model_manifest_sha256':model_hash}
    base = runner.make_plan(selection,inputs,stage='C',arms=('main',),
                            regimes=('budgeted',),runtime=runtime)
    rows = []
    for row in base['runs']:
        pair = [{**row,'run_id':'F_search-'+row['run_id']+'-'+variant,
                 'model_enabled':enabled}
                for variant,enabled in (('model_off',False),('model_on',True))]
        rows.extend(sorted(pair,key=lambda r:hashlib.sha256(
            ('srg12-model-order-v1:'+r['run_id']).encode()).hexdigest()))
    return {**base,'stage':'F_search','runs':rows,
        'model_manifest_sha256':model_hash,
        'intervention':'Only pretrained yield-tool availability changes; same main policy, inputs and search tools.',
        'prediction_scope':'Yield predictions are not measured reaction feasibility.',
        'interpretation':'Report actual predictor calls, usable scores and no-exposure cases. A single repeat is descriptive.'}


def _expand(runtime, supplied):
    if supplied is None:
        from .adapters import LocalRetroAdapter
        supplied = LocalRetroAdapter(repo_root=runtime['repo_root'],
            python_executable=runtime['chemistry_python'],
            timeout_seconds=runtime['tool_timeout_seconds']).expand
    def checked(target_smiles,top_k=10):
        if top_k != runtime['expansion_top_k']:
            return {'status':'error','message':'Expansion width differs from frozen protocol','predictions':[]}
        return supplied(target_smiles=target_smiles,top_k=top_k)
    return checked


def _exposure(episode, enabled):
    events = [e for e in episode.get('events',[]) if e['action']=='predict_reaction_yield']
    envelopes = [e.get('result',{}) for e in events]
    rows = [p for e in envelopes for p in (e.get('data') or {}).get('predictions',[])]
    calls = sum(e.get('usage',{}).get('backend_calls',0) for e in envelopes)
    return {'model_enabled':enabled,'predictor_action_attempts':len(events),
        'predictor_backend_calls':calls,'model_exercised':calls > 0,
        'scored_predictions':sum(p.get('status')=='scored' for p in rows),
        'abstained_predictions':sum(p.get('status')=='abstained' for p in rows),
        'failed_action_attempts':sum(e.get('status')!='ok' for e in events),
        'scientific_gain_established':False}


def execute_model_search(task,row,runtime,folder,*,expand=None):
    if row.get('arm') != 'main' or type(row.get('model_enabled')) is not bool:
        raise ValueError('Model ablation requires explicit on/off and the same main policy')
    manifest = runtime.get('reaction_yield_model_manifest')
    if (not isinstance(manifest,str) or runtime.get('model_manifest_sha256') is None
            or runner.digest(manifest) != runtime['model_manifest_sha256']):
        raise ValueError('Model manifest integrity mismatch')
    from .environment import SynthesisRouteEnv
    enabled = row['model_enabled']
    predictor = load_predictor(runtime['reaction_yield_model_manifest']) if enabled else None
    env = SynthesisRouteEnv(task,seed=row['seed'],expand=_expand(runtime,expand),
        reaction_yield_predictor=predictor,store=Path(folder)/'environment')
    try:
        result = runner._execute_agent(task,row,runtime,folder,env)
    except KeyboardInterrupt:
        env.cancel('external_operator_interruption')
        raise
    if runner.digest(manifest) != runtime['model_manifest_sha256']:
        raise ValueError('Model manifest integrity changed during execution')
    return {**result,'model_ablation':_exposure(result['episode'],enabled)}
