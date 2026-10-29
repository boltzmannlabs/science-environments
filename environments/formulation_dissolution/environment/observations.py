"""Evidence-labelled scientific observations with strict serialization contracts."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

LABELS = frozenset({'measured','literature_reported','predicted','derived','assumed','unknown'})
STATUSES = frozenset({'success','failure','insufficient_data','tool_unavailable','approval_required'})


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Value:
    name: str
    value: Any
    unit: str | None
    label: str
    source_id: str | None = None
    method: str | None = None
    timestamp: str = field(default_factory=now)
    batch_id: str | None = None
    version: str | None = None
    uncertainty: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.label not in LABELS:
            raise ValueError('invalid evidence label')
        if isinstance(self.value, (int, float)) and not isinstance(self.value, bool) and not self.unit:
            raise ValueError('numeric scientific value needs a unit')
        if self.label in {'measured','literature_reported'} and not self.source_id:
            raise ValueError('measured/literature value requires source ID')


@dataclass
class Observation:
    task_id: str
    status: str
    result_type: str = 'unknown'
    candidate_id: str | None = None
    results: list[Value] = field(default_factory=list)
    units: dict = field(default_factory=dict)
    constraints: dict = field(default_factory=lambda: {'passed': [], 'failed': [], 'not_evaluated': []})
    uncertainty: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=lambda: {'tool': None, 'version': None, 'source_ids': []})
    warnings: list[str] = field(default_factory=list)
    missing_data: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.status not in STATUSES or self.result_type not in LABELS:
            raise ValueError('invalid observation status or evidence label')
        if any(not isinstance(v, Value) for v in self.results):
            raise ValueError('results must contain Value instances')
        if self.results and any(v.label != self.result_type for v in self.results):
            raise ValueError('result_type does not match value evidence labels')

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Observation':
        data = dict(data)
        data['results'] = [Value(**v) for v in data.get('results', [])]
        return cls(**data)
