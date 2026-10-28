"""Request-level admission, settlement and recoverable shared resource accounting."""
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
from threading import RLock
import time


def _integer(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f'{label} must be an integer >= {minimum}')
    return value


def _finite(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'{label} must be finite and >= {minimum}')
    return value


@dataclass(frozen=True)
class AgentBudget:
    max_model_calls: int | None = 24
    max_tool_calls: int | None = 80
    wall_seconds: float | None = 1800
    max_output_tokens_per_call: int | None = 2048
    max_total_tokens: int | None = 250000
    finalization_model_calls: int = 1
    finalization_tool_calls: int = 1
    finalization_token_fraction: float = 0.1
    finalization_wall_fraction: float = 0.1
    specialist_report_chars: int = 2000
    regime: str = 'budgeted'

    def __post_init__(self):
        if self.regime not in ('budgeted', 'unbudgeted'):
            raise ValueError('Invalid budget regime')
        for name in ('max_model_calls', 'max_tool_calls', 'max_total_tokens', 'wall_seconds'):
            value = getattr(self, name)
            if self.regime == 'unbudgeted':
                if value is not None:
                    raise ValueError('Unbudgeted aggregate limits must all be null')
            elif name == 'wall_seconds':
                if _finite(value, name) == 0:
                    raise ValueError('wall_seconds must be positive')
            else:
                _integer(value, name, 1)
        if self.max_output_tokens_per_call is not None or self.regime == 'budgeted':
            _integer(self.max_output_tokens_per_call, 'max_output_tokens_per_call', 1)
        _integer(self.specialist_report_chars, 'specialist_report_chars', 1)
        for name in ('finalization_model_calls', 'finalization_tool_calls'):
            _integer(getattr(self, name), name)
        for name in ('finalization_token_fraction', 'finalization_wall_fraction'):
            if not 0 <= _finite(getattr(self, name), name) < 1:
                raise ValueError(f'{name} must be < 1')
        if self.regime == 'budgeted' and (self.finalization_model_calls > self.max_model_calls
                                        or self.finalization_tool_calls > self.max_tool_calls):
            raise ValueError('Finalization reservation exceeds shared budget')

    @classmethod
    def unbudgeted(cls, **protocol):
        """Remove research ceilings; optional kwargs retain protocol configuration."""
        for name in ('max_model_calls', 'max_tool_calls', 'wall_seconds', 'max_total_tokens'):
            if protocol.get(name) is not None:
                raise ValueError('Unbudgeted factory cannot accept finite aggregate limits')
        if protocol.get('regime', 'unbudgeted') != 'unbudgeted':
            raise ValueError('Unbudgeted factory cannot change regime')
        return cls(**{**protocol, 'regime': 'unbudgeted', 'max_model_calls': None,
                      'max_tool_calls': None, 'wall_seconds': None, 'max_total_tokens': None,
                      'max_output_tokens_per_call': protocol.get('max_output_tokens_per_call')})


class BudgetExhausted(RuntimeError):
    """Admission stopped before a new model request or tool side effect."""


class CheckpointError(RuntimeError):
    """Durability failed; no further external effect may be admitted."""


@dataclass(frozen=True)
class _Counts:
    model_calls: int = 0
    tool_calls: int = 0
    reserved_tokens: int = 0
    actual_tokens: int = 0
    reservation_tokens_total: int = 0


class SharedLedger:
    """One ledger for parent, specialists and retries, with conservative unknowns.

    Confirmed requests replace their reservations immediately. Stage telemetry
    adds only unaccounted usage. Unknown failed requests retain their reserves.
    Finite snapshots use an absolute deadline; unlimited snapshots have none.
    Both charge downtime. Unknown output bounds remain explicitly marked until
    settlement, so known input reservations never masquerade as full bounds.
    """

    def __init__(self, budget, *, clock=time.monotonic, wall_clock=time.time, on_change=None):
        self.budget, self._clock, self._wall_clock = budget, clock, wall_clock
        self._started, self._wall_started = clock(), wall_clock()
        self._elapsed_floor, self._counts, self._lock = 0.0, _Counts(), RLock()
        self._deadline = None if budget.wall_seconds is None else self._wall_started + budget.wall_seconds
        self._requests, self._stages, self._unmatched = {}, {}, 0
        self._role, self._on_change = 'main', on_change
        self.finalization_only = False

    def _elapsed(self):
        monotonic_elapsed = self._elapsed_floor + max(0, self._clock() - self._started)
        if self._deadline is None:
            return max(monotonic_elapsed, self._elapsed_floor + max(0, self._wall_clock() - self._wall_started))
        return max(monotonic_elapsed, self.budget.wall_seconds - (self._deadline - self._wall_clock()))

    def check_time(self):
        if self.budget.regime == 'unbudgeted':
            return
        if self._elapsed() >= self.budget.wall_seconds:
            raise BudgetExhausted('Shared wall-time budget exhausted')
        if self._role != 'main' and self._elapsed() >= self.budget.wall_seconds * (1 - self.budget.finalization_wall_fraction):
            self._exhausted('wall-time')

    def set_stage(self, role):
        if not isinstance(role, str) or not role:
            raise ValueError('Stage role must be nonempty')
        with self._lock:
            self._role = role

    def finalization_due(self, proposed_tokens=0, *, for_tool=False):
        if self.budget.regime == 'unbudgeted' or self._role != 'main':
            return False
        return (self.finalization_only
                or (not for_tool and self.budget.max_model_calls - self._counts.model_calls <= self.budget.finalization_model_calls)
                or self.budget.max_tool_calls - self._counts.tool_calls <= self.budget.finalization_tool_calls
                or self.budget.max_total_tokens - self._counts.reserved_tokens - self._counts.actual_tokens - proposed_tokens <= math.ceil(self.budget.max_total_tokens * self.budget.finalization_token_fraction)
                or self._elapsed() >= self.budget.wall_seconds * (1 - self.budget.finalization_wall_fraction))

    def _changed(self):
        if self._on_change is not None:
            try:
                self._on_change()
            except Exception as exc:
                raise CheckpointError('Runtime checkpoint failed; execution stopped') from exc

    def _cap(self, resource):
        maximum = getattr(self.budget, 'max_' + resource)
        if maximum is None or self._role == 'main':
            return maximum
        if resource == 'total_tokens':
            return maximum - math.ceil(maximum * self.budget.finalization_token_fraction)
        return maximum - getattr(self.budget, 'finalization_' + resource)

    def _exhausted(self, resource):
        suffix = ' (main finalization allowance protected)' if self._role != 'main' else ''
        raise BudgetExhausted(f'Shared {resource} budget exhausted{suffix}')

    def claim_model_call(self, *, estimated_input_tokens=0, reserved_output_tokens=0):
        unknown_output = reserved_output_tokens is None
        if unknown_output and self.budget.regime != 'unbudgeted':
            raise ValueError('Unknown output bound requires explicit unbudgeted regime')
        reservation = (_integer(estimated_input_tokens, 'estimated_input_tokens') +
                       (0 if unknown_output else _integer(reserved_output_tokens, 'reserved_output_tokens')))
        with self._lock:
            self.check_time()
            if self._cap('model_calls') is not None and self._counts.model_calls >= self._cap('model_calls'):
                self._exhausted('model_calls')
            if self._cap('total_tokens') is not None and self._counts.reserved_tokens + self._counts.actual_tokens + reservation > self._cap('total_tokens'):
                self._exhausted('total_tokens')
            request_id = self._counts.model_calls + 1
            record = {'reserved': reservation, 'actual': None}
            if unknown_output:
                record = {**record, 'output_bound_unknown': True}
            self._requests = {**self._requests, request_id: record}
            self._counts = replace(self._counts, model_calls=request_id,
                reserved_tokens=self._counts.reserved_tokens + reservation,
                reservation_tokens_total=self._counts.reservation_tokens_total + reservation)
            self._changed()
            return request_id

    def settle_request(self, request_id, tokens):
        _integer(request_id, 'request_id', 1)
        _integer(tokens, 'tokens')
        with self._lock:
            record = self._requests.get(request_id)
            if record is None:
                raise ValueError('Unknown request reservation')
            if record['actual'] is not None:
                if record['actual'] != tokens:
                    raise ValueError('Request usage conflict')
                return
            self._requests = {**self._requests, request_id: {**record, 'actual': tokens}}
            self._counts = replace(self._counts,
                reserved_tokens=self._counts.reserved_tokens - record['reserved'],
                actual_tokens=self._counts.actual_tokens + tokens)
            self._changed()

    def record_request_failure(self, request_id, diagnostic):
        with self._lock:
            if request_id not in self._requests:
                raise ValueError('Unknown request reservation')
            safe = {key: diagnostic[key] for key in ('exception_type', 'category', 'http_status') if key in diagnostic}
            self._requests = {**self._requests, request_id: {**self._requests[request_id], 'failure': safe}}
            self._changed()

    def settle_stage(self, tokens, confirmations=None, *, stage_id=None):
        if tokens is not None:
            _integer(tokens, 'Actual tokens')
        confirmations = self._confirmations(confirmations)
        signature = json.dumps([tokens, sorted(confirmations.items())], separators=(',', ':'))
        identity = stage_id or ('requests:' + hashlib.sha256(signature.encode()).hexdigest() if confirmations else None)
        with self._lock:
            if identity in self._stages:
                if self._stages[identity] != signature:
                    raise ValueError('Stage usage conflict')
                return
            if not confirmations.keys() <= self._requests.keys():
                raise ValueError('Unknown request reservation')
            for key, value in confirmations.items():
                actual = self._requests[key]['actual']
                if actual is not None and actual != value:
                    raise ValueError('Request usage conflict')
            if tokens is None:
                return
            accounted = sum(self._requests[key]['actual'] or 0 for key in confirmations)
            if confirmations and sum(confirmations.values()) == tokens:
                for key, value in confirmations.items():
                    self.settle_request(key, value)
            else:
                remainder = max(0, tokens - accounted)
                self._unmatched += remainder
                self._counts = replace(self._counts, actual_tokens=self._counts.actual_tokens + remainder)
            if identity is not None:
                self._stages = {**self._stages, identity: signature}
            self._changed()

    @staticmethod
    def _confirmations(values):
        result = {}
        for key, value in dict(values or {}).items():
            if isinstance(key, str) and key.isdigit():
                key = int(key)
            _integer(key, 'request_id', 1)
            _integer(value, 'Confirmed token counts')
            if key in result:
                raise ValueError('Duplicate request confirmation')
            result[key] = value
        return result

    def record_actual_tokens(self, tokens):
        self.settle_stage(tokens)

    def claim_tool_call(self):
        with self._lock:
            self.check_time()
            if self._cap('tool_calls') is not None and self._counts.tool_calls >= self._cap('tool_calls'):
                self._exhausted('tool_calls')
            self._counts = replace(self._counts, tool_calls=self._counts.tool_calls + 1)
            self._changed()

    def snapshot(self):
        with self._lock:
            unknown = sum(r.get('output_bound_unknown', False) and r['actual'] is None for r in self._requests.values())
            return {**({'unsettled_unknown_output_bounds': unknown} if unknown else {}),
                **asdict(self._counts), 'accounting_version': '3',
                'charged_tokens': self._counts.reserved_tokens + self._counts.actual_tokens,
                'unsettled_requests': sum(r['actual'] is None for r in self._requests.values()),
                'elapsed_seconds': self._elapsed(), 'limits': asdict(self.budget)}

    def export_state(self):
        with self._lock:
            version = 'srg-ledger-v2' if self.budget.regime == 'unbudgeted' else 'srg-ledger-v1'
            return {'schema_version': version, 'budget': asdict(self.budget),
                'counts': asdict(self._counts), 'requests': {str(k): dict(v) for k, v in self._requests.items()},
                'stages': dict(self._stages), 'unmatched_tokens': self._unmatched,
                'deadline_unix': self._deadline, 'saved_at_unix': self._wall_clock(),
                'elapsed_seconds': self._elapsed(), 'finalization_only': self.finalization_only}

    @classmethod
    def from_state(cls, state, *, budget=None, clock=time.monotonic, wall_clock=time.time, on_change=None):
        if not isinstance(state, dict) or state.get('schema_version') not in ('srg-ledger-v1', 'srg-ledger-v2'):
            raise ValueError('Invalid ledger state version')
        saved_budget = AgentBudget(**state['budget'])
        if state['schema_version'] == 'srg-ledger-v1' and saved_budget.regime != 'budgeted':
            raise ValueError('Legacy ledger state requires finite budget')
        if state['schema_version'] == 'srg-ledger-v2' and 'regime' not in state['budget']:
            raise ValueError('Version 2 requires explicit budget regime')
        if budget is not None and budget != saved_budget:
            raise ValueError('Resume budget differs from saved budget')
        ledger = cls(saved_budget, clock=clock, wall_clock=wall_clock, on_change=on_change)
        counts = _Counts(**state['counts'])
        for key, value in asdict(counts).items():
            _integer(value, key)
        requests = {int(key): dict(value) for key, value in state['requests'].items()}
        if (len(requests) != counts.model_calls
                or set(requests) != set(range(1, len(requests) + 1))):
            raise ValueError('Invalid request identities')
        for record in requests.values():
            _integer(record['reserved'], 'reservation')
            unknown = record.get('output_bound_unknown', False)
            if not isinstance(unknown, bool) or (unknown and saved_budget.regime != 'unbudgeted'):
                raise ValueError('Invalid unknown output bound')
            if record['actual'] is not None:
                _integer(record['actual'], 'actual')
        unmatched = _integer(state['unmatched_tokens'], 'unmatched')
        if (counts.reserved_tokens != sum(r['reserved'] for r in requests.values() if r['actual'] is None)
                or counts.actual_tokens != unmatched + sum(r['actual'] or 0 for r in requests.values())
                or counts.reservation_tokens_total != sum(r['reserved'] for r in requests.values())
                or (saved_budget.max_model_calls is not None and counts.model_calls > saved_budget.max_model_calls)
                or (saved_budget.max_tool_calls is not None and counts.tool_calls > saved_budget.max_tool_calls)):
            raise ValueError('Inconsistent ledger counts')
        saved_at = _finite(state['saved_at_unix'], 'saved_at_unix')
        deadline = state['deadline_unix']
        if saved_budget.regime == 'unbudgeted':
            if deadline is not None:
                raise ValueError('Unbudgeted deadline must be null')
        else:
            _finite(deadline, 'deadline_unix')
        elapsed = _finite(state['elapsed_seconds'], 'elapsed_seconds')
        if wall_clock() < saved_at:
            raise ValueError('Wall clock moved backwards; resume refused')
        if deadline is not None and deadline - saved_at > saved_budget.wall_seconds - elapsed + 0.01:
            raise ValueError('Inconsistent deadline')
        stages = state['stages']
        if not isinstance(stages, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in stages.items()):
            raise ValueError('Invalid stage settlement history')
        ledger._counts, ledger._requests, ledger._unmatched = counts, requests, unmatched
        ledger._stages, ledger._deadline = dict(stages), deadline
        ledger._elapsed_floor = elapsed + max(0, wall_clock() - saved_at)
        if (not isinstance(state.get('finalization_only'), bool)
                or (saved_budget.regime == 'unbudgeted' and state['finalization_only'])):
            raise ValueError('Invalid finalization state')
        ledger.finalization_only = state['finalization_only']
        return ledger
