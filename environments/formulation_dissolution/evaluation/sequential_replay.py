"""Evaluator-owned reveal controller; no outcome before charged selection."""
from dataclasses import dataclass, field

@dataclass
class Replay:
    """Pool is private to evaluator; public view excludes labels and outcomes."""
    _pool: dict
    max_observations: int
    revealed: dict = field(default_factory=dict)

    def catalog(self):
        return [{'candidate_id':key} for key in sorted(self._pool)]

    def select(self,candidate_id):
        if candidate_id in self.revealed:
            return {'status':'already_revealed','candidate_id':candidate_id}
        if len(self.revealed)>=self.max_observations:
            return {'status':'budget_exhausted'}
        if candidate_id not in self._pool or self._pool[candidate_id].get('data_origin')!='experimental':
            return {'status':'unscorable_candidate','candidate_id':candidate_id}
        observation={**self._pool[candidate_id], 'event_type':'historical_replay_not_new_measurement'}
        self.revealed[candidate_id]=observation
        return {'status':'success','observation':observation,'charged_observations':len(self.revealed)}


def benchmark(pool=None, budget=None):
    """Refuse replay without a frozen eligible pool and finite observation budget."""
    if not pool or budget is None: return {'status':'not_evaluated','reason':'no frozen eligible measured candidate pool or budget','track':'replay'}
    replay=Replay(pool,budget)
    return {'status':'ready','catalog':replay.catalog(),'measured_rewards':None,'track':'replay'}
