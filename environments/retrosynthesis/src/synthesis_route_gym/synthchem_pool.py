"""SRG proposal boundary inspired by SynthChem's 20261027 portfolio snapshot.

Only normalized environment predictions enter; no literature or supplied seeds.
"""
from copy import deepcopy
import json
import time
from .chemistry import canonical_smiles, element_counts
from .planning import _step
from .schemas import RouteCandidate
from .validation import assess_route
from .resource_policy import remaining

MAX_CACHE_BYTES = 32_000_000


class EnvironmentProposalPool:
    """Episode-local successful-response cache; uncached expansion is host-metered."""
    def __init__(self, env, width, max_entries, reserve):
        self.env, self.width, self.max_entries = env, width, max_entries
        self.reserve = reserve
        usage = env.search_status()['usage']
        self.max_calls = remaining(env.task.budget.max_expansions, usage['expansions'])
        duration = remaining(env.task.budget.max_wall_seconds, usage['wall_seconds']+reserve)
        self.deadline = None if duration is None else time.monotonic()+duration
        self.phase_limit, self.phase_deadline = self.max_calls, self.deadline
        self.calls, self.cache_bytes = 0, 0
        self.cache = {}
        self.metrics = dict.fromkeys(('backend_calls','unresolved_backend_calls','cache_hits',
            'failed_expansions','rejected_predictions','cache_capacity_skips'),0)
        self.backend_seconds = 0.0
        self.failures = ()

    def _count(self, key, amount=1):
        self.metrics = {**self.metrics,key:self.metrics[key]+amount}

    def set_phase(self, limit, deadline):
        limits = [item for item in (limit,self.max_calls) if item is not None]
        deadlines = [item for item in (deadline,self.deadline) if item is not None]
        self.phase_limit = min(limits) if limits else None
        self.phase_deadline = min(deadlines) if deadlines else None

    def admission_reason(self, *, backend=False):
        state = self.env.search_status()
        if state['terminated'] or state['truncated']:
            return 'episode_closed'
        if self.phase_deadline is not None and time.monotonic() >= self.phase_deadline:
            return 'wall_reserve'
        # Native search registers routes after extraction: reserve proposal + submit.
        budget = self.env.task.budget
        if budget.max_actions is not None and state['usage']['actions'] >= budget.max_actions-2:
            return 'action_reserve'
        if backend and ((self.phase_limit is not None and self.calls >= self.phase_limit) or
                (budget.max_expansions is not None and state['usage']['expansions'] >= budget.max_expansions)):
            return 'backend_call_quota'
        return None

    @property
    def stopped(self):
        return self.admission_reason(backend=True) is not None

    def _accepted_predictions(self, product, predictions):
        rows, seen = [], set()
        for prediction in predictions:
            step = _step(prediction)
            key = (step.product,tuple(sorted(u.smiles for u in step.reactants)))
            route = RouteCandidate(route_id='structural-check',target=product,steps=(step,))
            task = self.env.task.model_copy(update={'target':product})
            audit = assess_route(task,route)
            if (step.product != product or product in [u.smiles for u in step.reactants]
                    or not audit.graph_valid or not audit.constraint_compliant or key in seen):
                self._count('rejected_predictions')
                continue
            seen.add(key)
            supplied = {}
            for use in step.reactants:
                for element,count in element_counts(use.smiles).items():
                    supplied = {**supplied,element:supplied.get(element,0)+count}
            deficit = any(e != 8 and count > supplied.get(e,0)
                          for e,count in element_counts(product).items())
            rows.append({**prediction,'search_cost':1.0+float(deficit),
                'input_review_required':deficit,'search_cost_basis':'step_plus_structural_count_warning_not_feasibility'})
        return rows

    def expand(self, smiles):
        product = canonical_smiles(smiles)
        args = {'smiles':product,'top_k':self.width}
        key = self.env.expansion_cache_identity(args)
        if self.admission_reason() is not None:
            return []
        if key in self.cache:
            self._count('cache_hits')
            return deepcopy(self.cache[key])
        if self.admission_reason(backend=True) is not None:
            return []
        self.calls += 1
        response = self.env.dispatch('expand',args)
        envelope = response['result'].get('tool_result',{})
        self._count('backend_calls',envelope.get('usage',{}).get('backend_calls',1))
        self._count('unresolved_backend_calls',int(not envelope))
        self.backend_seconds += envelope.get('usage',{}).get('elapsed_seconds',0.0)
        if response['status'] != 'ok':
            self._count('failed_expansions')
            self.failures = (*self.failures,{'product':product,'status':response['status'],
                'code':envelope.get('error',{}).get('code') if envelope.get('error') else None})
            return []
        rows = self._accepted_predictions(product,response['result']['predictions'])
        size = len(json.dumps(rows,allow_nan=False).encode())+len(key)
        if (self.max_entries is None or len(self.cache)<self.max_entries) and self.cache_bytes+size<=MAX_CACHE_BYTES:
            self.cache = {**self.cache,key:deepcopy(rows)}
            self.cache_bytes += size
        else:
            self._count('cache_capacity_skips')
        return rows

    def manifest(self):
        return {**self.metrics,'expansion_actions':self.calls,'cached_products':len(self.cache),
            'cache_bytes':self.cache_bytes,'backend_seconds':self.backend_seconds,
            'failures':list(self.failures),'cache_scope':'episode_and_host_expansion_identity',
            'backend_call_count_scope':'known envelope calls plus one reserved per missing envelope; unresolved count explicit',
            'supplied_route_seeds':0,'evidence_seeds':0}
