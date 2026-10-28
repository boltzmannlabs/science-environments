"""Native A*/MCTS portfolio adapted from SynthChem's 20261027 source snapshot."""
import math
import time
from .planning import _route_id
from .schemas import RouteCandidate
from .validation import assess_route
from .synthchem_pool import EnvironmentProposalPool
from .synthchem_native import require_native, run_native_phase

VERSION = 'srg-synthchem-portfolio-v1'

def _eligible(a):
    return (a.graph_valid and a.inventory_complete and a.constraint_compliant
            and a.quantity_status in {'complete','not_requested'} and not a.acquisition_only)

def _options(env, algorithm, width, nodes, reserve):
    if algorithm not in ('portfolio','astar','mcts'):
        raise ValueError('Expected portfolio, astar or mcts')
    if type(width) is not int or not 1<=width<=100:
        raise ValueError('Expansion width must be an integer in [1,100]')
    if type(nodes) is not int or not 1<=nodes<=100000:
        raise ValueError('Graph limit must be an integer in [1,100000]')
    reserve = min(5.0,env.task.budget.max_wall_seconds/10) if reserve is None else reserve
    if type(reserve) not in (int,float) or not math.isfinite(reserve) or not 0<=reserve<env.task.budget.max_wall_seconds:
        raise ValueError('Invalid finalization reserve')
    return reserve

def _collect(env, rows, phase, collected):
    rejected, result = [], dict(collected)
    for row in rows:
        try:
            route = RouteCandidate(route_id=_route_id(row['steps']),target=env.task.target,steps=row['steps'])
        except (ValueError,TypeError,KeyError):
            rejected.append({'reason':'invalid_route_contract','found_by':phase})
            continue
        assessment = assess_route(env.task,route)
        if not _eligible(assessment):
            rejected.append({'route_id':route.route_id,'found_by':phase,
                'reasons':[f.code for f in assessment.findings if f.severity=='error'],
                'quantity_status':assessment.quantity_status})
            continue
        old = result.get(route.route_id)
        phases = sorted(set((old['found_by'] if old else [])+[phase]))
        result = {**result,route.route_id:{'route':route,'found_by':phases,'review_penalty':row['review_penalty']}}
    return result,rejected

def _diversify(collected):
    pending = sorted(collected.values(),key=lambda r:(r['review_penalty'],len(r['route'].steps),r['route'].route_id))
    ordered, seen = [], set()
    def root(row):
        return tuple(sorted(u.smiles for s in row['route'].steps if s.product==row['route'].target for u in s.reactants))
    while pending:
        index = next((i for i,r in enumerate(pending)
            if r['review_penalty']==pending[0]['review_penalty'] and root(r) not in seen),0)
        row = pending[index]
        pending = pending[:index]+pending[index+1:]
        ordered.append(row); seen.add(root(row))
    return ordered

def _submit(env, rows):
    proposed = []
    for row in rows:
        status = env.search_status()
        if status['terminated'] or status['truncated'] or (env.task.budget.max_actions is not None and status['usage']['actions']>=env.task.budget.max_actions-1):
            break
        if len(proposed)>=env.task.budget.top_k:
            break
        route = row['route']
        response = env.dispatch('propose_route',{'route':route.model_dump(mode='json')})
        if response['status']=='ok':
            proposed.append(route.route_id)
    status = env.search_status()
    if status['terminated'] or status['truncated']:
        return [],'not_submitted_episode_closed'
    response = env.dispatch('submit',{'route_ids':proposed})
    if response['status']!='ok':
        return [],'not_submitted_'+response['status']
    return response['result']['accepted_route_ids'],'submitted'

def run_synthchem_workflow(env, *, algorithm='portfolio', expansion_top_k=10,
                           max_graph_nodes=10000, finalization_reserve_seconds=None):
    """Native phases share total expansion/time allowance; node caps are per phase.

    Host submission checks inventory, quantity, constraints and graph integrity.
    Accepted routes retain predicted chemistry and are not experimentally solved.
    """
    if env.task.budget.regime == 'unbudgeted':
        return _unbudgeted_workflow(env, algorithm, expansion_top_k)
    reserve = _options(env,algorithm,expansion_top_k,max_graph_nodes,finalization_reserve_seconds)
    require_native()
    pool = EnvironmentProposalPool(env,expansion_top_k,min(max_graph_nodes,10000),reserve)
    stock = frozenset(i.smiles for i in env.task.inventory if i.available_mmol != 0)
    phases = ['astar','mcts'] if algorithm=='portfolio' else [algorithm]
    searches, collected, rejected = [], {}, []
    reason = 'search_phases_finished'
    if env.task.target in stock:
        reason = 'target_in_stock_no_synthesis'
    elif env.task.constraints.max_steps==0:
        reason = 'step_limit'
    else:
        for index,name in enumerate(phases):
            remaining = pool.max_calls-pool.calls
            pool.set_phase(pool.max_calls,pool.deadline)
            if remaining<=0 or pool.stopped:
                reason = pool.admission_reason(backend=True) or 'backend_call_quota'
                searches.append({'algorithm':name,'status':'not_run','reason':reason})
                continue
            left = len(phases)-index
            quota = max(1,remaining//left)
            duration = max(0,pool.deadline-time.monotonic())/left
            deadline = time.monotonic()+duration
            pool.set_phase(pool.calls+quota,deadline-min(1.0,duration*.1))
            report,rows,errors = run_native_phase(pool,name,stock,seed=env.seed,
                depth=env.task.constraints.max_steps,max_nodes=max_graph_nodes,quota=quota,
                route_limit=env.task.budget.top_k*5,phase_deadline=deadline)
            searches.append(report)
            collected, invalid = _collect(env,rows,name,collected)
            rejected.extend(errors+invalid)
    ordered = _diversify(collected)
    accepted, submission = _submit(env,ordered)
    if submission!='submitted':
        reason = 'episode_closed_before_submission'
    return {'method':'fixed_workflow','algorithm':'synthchem_'+algorithm+'_v1','version':VERSION,
        'searches':searches,'accepted_route_ids':accepted,'submission_status':submission,'stop_reason':reason,
        'route_provenance':{r['route'].route_id:r['found_by'] for r in ordered},'rejected_routes':rejected,
        'proposal_pool':pool.manifest(),'max_graph_nodes_per_phase':max_graph_nodes,
        'expansion_top_k':expansion_top_k,'finalization_reserve_seconds':reserve,'episode':env.export(),
        'limitations':['Graph closure and deterministic acceptance do not establish chemical feasibility.',
            'Native phases share proposal calls, not their search trees or score scales.',
            'Phase deadlines are admission limits; in-flight backend calls may overrun a phase.',
            'MCTS depth counts sequential steps; A* depth counts the longest synthesis branch.',
            'No supplied routes, literature seeds or learned search heuristic are used.']}


def _unbudgeted_workflow(env, algorithm, width):
    from .synthchem_unbounded import UnboundedNativePhase
    if algorithm not in ('portfolio','astar','mcts') or type(width) is not int or not 1 <= width <= 100:
        raise ValueError('Invalid native search algorithm or expansion width')
    pool = EnvironmentProposalPool(env,width,None,0)
    stock = frozenset(i.smiles for i in env.task.inventory if i.available_mmol != 0)
    names = ['astar','mcts'] if algorithm == 'portfolio' else [algorithm]
    phases, collected, rejected = [], {}, []
    reason = 'frontier_exhausted'
    if env.task.target not in stock and env.task.constraints.max_steps:
        phases = [UnboundedNativePhase(pool,name,stock,seed=env.seed,
                  depth=env.task.constraints.max_steps) for name in names]
    try:
        while any(not phase.done for phase in phases):
            for phase in phases:
                if phase.done:
                    continue
                phase.advance()
                for row in phase.rows():
                    collected, invalid = _collect(env,[row],phase.name,collected)
                    rejected.extend(invalid)
                    if len(collected) >= env.task.budget.top_k:
                        reason = 'route_quota'
                        break
                if phase.termination not in (None,'frontier_exhausted'):
                    reason = phase.termination
                    break
                if reason == 'route_quota':
                    break
            if reason != 'frontier_exhausted':
                break
    finally:
        for phase in phases:
            phase.close(reason)
    ordered = _diversify(collected)
    accepted, submission = _submit(env,ordered)
    if submission != 'submitted':
        reason = 'episode_closed_before_submission'
    natural = submission == 'submitted' and reason in {'frontier_exhausted','route_quota'}
    return {'method':'fixed_workflow','algorithm':'synthchem_'+algorithm+'_v1','version':VERSION,
        'status':'completed' if natural else 'interrupted' if env.search_status()['truncated'] else 'failed',
        'naturally_completed':natural,
        'searches':[p.report() for p in phases], 'accepted_route_ids':accepted,
        'submission_status':submission,'stop_reason':reason,
        'route_provenance':{r['route'].route_id:r['found_by'] for r in ordered},
        'rejected_routes':rejected+[e for p in phases for e in p.errors],
        'proposal_pool':pool.manifest(),'max_graph_nodes_per_phase':None,
        'expansion_top_k':width,'finalization_reserve_seconds':None,'episode':env.export(),
        'limitations':['Structural closure does not establish chemical feasibility.']}
