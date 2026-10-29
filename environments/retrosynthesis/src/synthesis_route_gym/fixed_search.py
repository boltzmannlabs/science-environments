"""Bounded, inventory-aware fixed search; heuristic priority is not feasibility.

This policy only uses public task fields and normalized expansion predictions.
Shared cache snapshots are trusted host inputs, not independently verified model
artifacts. Cold and shared-precomputed comparisons must be reported separately.
"""
from dataclasses import dataclass
import hashlib
import heapq
import json
import math
from .planning import _route_id, _step
from .schemas import RouteCandidate
from .tool_contracts import ExpandRequest, ExpansionResult
from .validation import assess_route

VERSION = 'best_first_AND_OR_v1'
CACHE_VERSION = 'srg-expansion-cache-v1'
MAX_CACHE_BYTES = 32_000_000
MAX_CACHE_ENTRIES = 10000
SCORE_RULE = ('ascending (preparative_steps + unresolved_unique_precursors, '
              'unresolved_unique_precursors, preparative_steps, canonical_route_signature); '
              'uncalibrated structural heuristic, no optimality or feasibility guarantee')


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _digest(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _cache_key(fingerprint, args):
    return _digest({'registry':fingerprint, 'capability':'expand', 'arguments':args})


def _cache_input(raw, mode):
    if (not isinstance(mode,str) or mode not in {'cold', 'shared_precomputed'}
            or (raw is not None and mode != 'shared_precomputed')):
        raise ValueError('Supplied expansion cache requires shared_precomputed cache mode')
    empty = {'schema_version':CACHE_VERSION, 'entries':{}, 'backend_calls':0, 'elapsed_seconds':0.0}
    if raw is None:
        return empty
    try:
        if len(_json(raw)) > MAX_CACHE_BYTES:
            raise ValueError('Cache snapshot too large')
        raw = json.loads(_json(raw))
        if (set(raw) != set(empty) or raw['schema_version'] != CACHE_VERSION
                or not isinstance(raw['entries'],dict) or len(raw['entries']) > MAX_CACHE_ENTRIES
                or type(raw['backend_calls']) is not int or raw['backend_calls'] < len(raw['entries'])
                or type(raw['elapsed_seconds']) not in {int,float} or raw['elapsed_seconds'] < 0):
            raise ValueError('Invalid cache snapshot')
        for key, row in raw['entries'].items():
            if set(row) != {'registry_fingerprint','arguments','data'}:
                raise ValueError('Invalid cache record')
            fingerprint = row['registry_fingerprint']
            if not isinstance(fingerprint,str) or len(fingerprint)!=64 or any(c not in '0123456789abcdef' for c in fingerprint):
                raise ValueError('Invalid cache fingerprint')
            args = ExpandRequest.model_validate(row['arguments']).model_dump(mode='json')
            data = ExpansionResult.model_validate(row['data']).model_dump(mode='json')
            if (args != row['arguments'] or data != row['data'] or key != _cache_key(fingerprint,args)
                    or len(data['predictions']) > args['top_k']
                    or any(p['product'] != args['smiles'] for p in data['predictions'])):
                raise ValueError('Mismatched cache record')
        return raw
    except (TypeError, ValueError, KeyError, RecursionError) as exc:
        raise ValueError('Invalid expansion cache snapshot') from exc


@dataclass(frozen=True)
class _State:
    steps: tuple
    pending: tuple

    @property
    def signature(self):
        return tuple(sorted((s.product,tuple(sorted(u.smiles for u in s.reactants))) for s in self.steps))

    @property
    def priority(self):
        return (len(self.steps)+len(self.pending), len(self.pending), len(self.steps), self.signature)


def _pending(target, steps, stock):
    products = {s.product for s in steps}
    materials = {target} | {u.smiles for s in steps for u in s.reactants}
    return tuple(sorted(materials - products - stock))


def _has_cycle(steps):
    dependencies = {s.product:tuple(u.smiles for u in s.reactants) for s in steps}
    def visit(molecule, active, visited):
        if molecule in active:
            return True, visited
        if molecule in visited or molecule not in dependencies:
            return False, visited
        for precursor in dependencies[molecule]:
            cyclic, visited = visit(precursor, active | {molecule}, visited)
            if cyclic:
                return True, visited
        return False, visited | {molecule}
    visited = set()
    for molecule in dependencies:
        cyclic, visited = visit(molecule,set(),visited)
        if cyclic:
            return True
    return False


def _eligible(assessment):
    return (assessment['graph_valid'] and assessment['inventory_complete']
        and assessment['constraint_compliant'] and not assessment['acquisition_only']
        and assessment['quantity_status'] in {'complete','not_requested'})


class _Search:
    """Episode-local controller; input task/cache objects are never mutated."""
    def __init__(self, env, top_k, max_states, cache, mode, reserve):
        self.env, self.top_k, self.max_states = env, top_k, max_states
        self.cache, self.initial_cache = cache, cache
        self.cache_mode, self.reserve = mode, reserve
        self.structure_task = env.task.model_copy(update={'inventory':()})
        self.stock = frozenset(s.smiles for s in env.task.inventory if s.available_mmol != 0)
        initial = _State((), _pending(env.task.target, (), self.stock))
        self.frontier = [(initial.priority, initial)]
        self.seen = frozenset({initial.signature})
        self.candidates = ()
        self.metrics = dict.fromkeys(('duplicate_states','cycle_prunes','invalid_prunes',
            'step_limit_prunes','frontier_capacity_prunes','expansion_budget_prunes',
            'rejected_candidates','cache_hits','precomputed_cache_hits','cache_misses',
            'failed_expansions','cache_capacity_prunes','search_states','generated_states'),0)
        self.metrics = {**self.metrics,'peak_frontier_states':1,'peak_dedup_signatures':1}
        self.stop_reason = 'frontier_exhausted'
        self.local_keys = frozenset()
        self.local_backend_calls, self.local_backend_seconds = 0, 0.0
        self.unresolved_backend_calls = 0
        self.cache_bytes = len(_json(cache))

    def count(self, key, value=1):
        self.metrics = {**self.metrics, key:self.metrics[key]+value}

    def admission(self):
        status = self.env.search_status()
        if status['terminated'] or status['truncated']:
            return 'episode_closed'
        budget = self.env.task.budget
        if budget.max_wall_seconds is not None and status['usage']['wall_seconds'] >= budget.max_wall_seconds-self.reserve:
            return 'wall_reserve'
        if budget.max_actions is not None and status['usage']['actions'] >= budget.max_actions-1:
            return 'action_reserve'
        if self.max_states is not None and self.metrics['search_states'] >= self.max_states:
            return 'frontier_state_budget'
        return None

    def predictions(self, molecule):
        args = {'smiles':molecule,'top_k':self.top_k}
        key = self.env.expansion_cache_identity(args)
        if key in self.cache['entries']:
            self.count('cache_hits')
            if key not in self.local_keys:
                self.count('precomputed_cache_hits')
            return self.cache['entries'][key]['data']['predictions']
        limit = self.env.task.budget.max_expansions
        if limit is not None and self.env.search_status()['usage']['expansions'] >= limit:
            self.count('expansion_budget_prunes')
            return []
        self.count('cache_misses')
        response = self.env.dispatch('expand',args)
        envelope = response['result'].get('tool_result',{})
        self.local_backend_calls += envelope.get('usage',{}).get('backend_calls',1)
        if not envelope:
            self.unresolved_backend_calls += 1
        self.local_backend_seconds += envelope.get('usage',{}).get('elapsed_seconds',0.0)
        if response['status'] != 'ok':
            self.count('failed_expansions')
            return []
        data = ExpansionResult.model_validate({'predictions':response['result']['predictions']}).model_dump(mode='json')
        row = {'registry_fingerprint':self.env.search_status()['capability_fingerprint'],
               'arguments':args,'data':data}
        size = len(_json(row))+len(key)+4
        if len(self.cache['entries']) < MAX_CACHE_ENTRIES and self.cache_bytes+size < MAX_CACHE_BYTES-1000:
            self.cache = {**self.cache,'entries':{**self.cache['entries'],key:row}}
            self.local_keys = self.local_keys | {key}
            self.cache_bytes += size
        else:
            self.count('cache_capacity_prunes')
        return data['predictions']

    def complete(self, state):
        route = RouteCandidate(route_id=_route_id(state.steps),target=self.env.task.target,steps=state.steps)
        response = self.env.dispatch('propose_route',{'route':route.model_dump(mode='json')})
        if response['status']=='ok' and _eligible(response['result']['assessment']):
            self.candidates = (*self.candidates,route.route_id)
        else:
            self.count('rejected_candidates')

    def child(self, state, prediction):
        try:
            step = _step(prediction)
        except (TypeError,ValueError,KeyError):
            self.count('invalid_prunes')
            return None
        steps = (*state.steps,step)
        if step.product != state.pending[0]:
            self.count('invalid_prunes')
            return None
        if _has_cycle(steps):
            self.count('cycle_prunes')
            return None
        route = RouteCandidate(route_id=_route_id(steps),target=self.env.task.target,steps=steps)
        assessment = assess_route(self.structure_task,route)
        if not assessment.graph_valid or not assessment.constraint_compliant:
            self.count('invalid_prunes')
            return None
        return _State(steps,_pending(self.env.task.target,steps,self.stock))

    def enqueue(self, state):
        if state.signature in self.seen:
            self.count('duplicate_states')
            return
        self.seen = self.seen | {state.signature}
        self.count('generated_states')
        heapq.heappush(self.frontier,(state.priority,state))
        if self.max_states is not None and len(self.frontier)>self.max_states:
            evicted = max(self.frontier,key=lambda item:item[0])
            self.frontier = [item for item in self.frontier if item[0] != evicted[0]]
            self.seen = self.seen - {evicted[1].signature}
            heapq.heapify(self.frontier)
            self.count('frontier_capacity_prunes')
        self.metrics = {**self.metrics,
            'peak_frontier_states':max(self.metrics['peak_frontier_states'],len(self.frontier)),
            'peak_dedup_signatures':max(self.metrics['peak_dedup_signatures'],len(self.seen))}

    def run(self):
        while self.frontier and len(self.candidates)<self.env.task.budget.top_k:
            reason = self.admission()
            if reason:
                self.stop_reason = reason
                break
            _, state = heapq.heappop(self.frontier)
            self.count('search_states')
            if not state.pending:
                self.complete(state)
            elif len(state.steps)>=self.env.task.constraints.max_steps:
                self.count('step_limit_prunes')
            else:
                for prediction in self.predictions(state.pending[0]):
                    status = self.env.search_status()
                    if status['terminated'] or status['truncated']:
                        break
                    child = self.child(state,prediction)
                    if child is not None:
                        self.enqueue(child)
        if len(self.candidates)>=self.env.task.budget.top_k:
            self.stop_reason = 'route_quota'
        elif self.stop_reason=='frontier_exhausted' and self.metrics['expansion_budget_prunes']:
            self.stop_reason = 'expansion_budget'
        elif (self.stop_reason=='frontier_exhausted' and self.metrics['failed_expansions']
              and self.env.task.budget.regime == 'unbudgeted'):
            self.stop_reason = 'backend_failure'
        status = self.env.search_status()
        if status['terminated'] or status['truncated']:
            self.stop_reason = 'episode_closed'
        if not status['terminated'] and not status['truncated']:
            self.env.dispatch('submit',{'route_ids':list(self.candidates)})
        return self.result()

    def result(self):
        cache = {**self.cache, 'backend_calls':self.initial_cache['backend_calls']+self.local_backend_calls,
                 'elapsed_seconds':self.initial_cache['elapsed_seconds']+self.local_backend_seconds}
        accounting = {'mode':self.cache_mode,
            'precomputation_backend_calls':self.initial_cache['backend_calls'],
            'precomputation_backend_seconds':self.initial_cache['elapsed_seconds'],
            'episode_backend_calls':self.local_backend_calls,'episode_backend_seconds':self.local_backend_seconds,
            'episode_unresolved_backend_calls':self.unresolved_backend_calls,
            'scope':'Host-declared cache provenance; external artifacts not independently verified. '
                    'Cache hits avoid inference and are reported separately from environment expansion calls. '
                    'Missing envelopes reserve one backend call; recorded backend seconds are a lower bound.'}
        return {'method':'fixed_workflow','algorithm':VERSION,'scoring_rule':SCORE_RULE,
            'stop_reason':self.stop_reason,'search_states':self.metrics['search_states'],
            'expansion_top_k':self.top_k,'max_frontier_states':self.max_states,
            'finalization_reserve_seconds':self.reserve,
            'finalization_policy':('No aggregate research ceiling or finalization reserve.'
                if self.env.task.budget.regime == 'unbudgeted' else
                'One action reserved for submission; wall reserve is admission-only. '
                'In-flight timeout or cancellation may still truncate without a submission.'),
            'metrics':dict(self.metrics),
            'cache_accounting':accounting,'expansion_cache':cache,'episode':self.env.export()}


def run_best_first_workflow(env, *, expansion_top_k=10, max_frontier_states=10000,
                            expansion_cache=None, cache_mode='cold', finalization_reserve_seconds=None):
    """Run deterministic best-first AND/OR search under the environment budget.

    At most ``max_frontier_states`` states are visited and retained in the frontier.
    Deduplication retains only visited and queued signatures (at most twice that cap).
    Full precursor multiplicity stays on reaction steps; shared intermediates have one producer.
    A route only fills the shortlist when it passes the environment submission
    gates. Unknown requested quantities cannot be promoted to complete amounts.
    """
    unbudgeted = env.task.budget.regime == 'unbudgeted'
    valid_frontier = ((max_frontier_states is None and unbudgeted) or
        (type(max_frontier_states) is int and 1<=max_frontier_states<=100000))
    if type(expansion_top_k) is not int or not 1<=expansion_top_k<=100 or not valid_frontier:
        raise ValueError('Invalid fixed-search limits')
    default_reserve = 0.0 if unbudgeted else min(5.0,env.task.budget.max_wall_seconds/10)
    reserve = default_reserve if finalization_reserve_seconds is None else finalization_reserve_seconds
    if (type(reserve) not in {int,float} or not math.isfinite(reserve)
            or reserve<0 or (not unbudgeted and reserve>=env.task.budget.max_wall_seconds)):
        raise ValueError('Invalid finalization reserve')
    if unbudgeted:
        max_frontier_states, reserve = None, 0.0
    cache = _cache_input(expansion_cache,cache_mode)
    return _Search(env,expansion_top_k,max_frontier_states,cache,cache_mode,reserve).run()
