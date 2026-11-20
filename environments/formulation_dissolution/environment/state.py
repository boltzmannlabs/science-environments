"""Episode and append-only audit history, atomically saved to local JSON."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import os
import tempfile
from environment.observations import now


@dataclass
class Episode:
    task: dict
    sources: dict = field(default_factory=dict)
    materials: dict = field(default_factory=dict)
    candidates: dict = field(default_factory=dict)
    constraints: dict = field(default_factory=dict)
    predictions: dict = field(default_factory=dict)
    experiments: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    hypotheses: list = field(default_factory=list)
    ranking: list = field(default_factory=list)
    status: str = 'open'
    audit: list = field(default_factory=list)
    budget: dict = field(default_factory=dict)

    def log(self, action: str, outcome: str, detail: dict | None = None):
        self.audit.append({'timestamp': now(), 'action': action, 'outcome': outcome, 'detail': detail or {}})

    def save(self, path: str | Path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement, without modifying source documents.
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix='.episode-')
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(asdict(self), stream, indent=2, allow_nan=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    @classmethod
    def load(cls, path: str | Path) -> 'Episode':
        with open(path) as stream:
            return cls(**json.load(stream))
