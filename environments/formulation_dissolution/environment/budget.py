"""Configurable, persistent counters and elapsed-time/experiment gates."""
from dataclasses import dataclass, field, asdict
from time import monotonic
from math import isfinite


@dataclass
class Budget:
    limits: dict = field(default_factory=dict)
    used: dict = field(default_factory=dict)
    started: float = field(default_factory=monotonic)

    def __post_init__(self):
        for mapping in (self.limits, self.used):
            if not isinstance(mapping, dict) or any(
                not isinstance(v, (int, float)) or isinstance(v, bool)
                or not isfinite(v) or v < 0 for v in mapping.values()
            ):
                raise ValueError('budgets require finite nonnegative numeric counters; omit unknown limits')

    def charge(self, key: str, amount: float = 1):
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or not isfinite(amount) or amount < 0:
            raise ValueError('budget charge must be nonnegative')
        if key in self.limits and self.used.get(key, 0) + amount > self.limits[key]:
            raise RuntimeError('budget_exhausted:' + key)
        if 'elapsed_seconds' in self.limits and monotonic() - self.started > self.limits['elapsed_seconds']:
            raise RuntimeError('budget_exhausted:elapsed_seconds')
        self.used[key] = self.used.get(key, 0) + amount

    def snapshot(self):
        return {'limits': self.limits, 'used': self.used, 'elapsed_seconds': monotonic()-self.started}

    @classmethod
    def restore(cls, snapshot):
        return cls(snapshot['limits'], snapshot['used'], monotonic()-snapshot.get('elapsed_seconds', 0))
