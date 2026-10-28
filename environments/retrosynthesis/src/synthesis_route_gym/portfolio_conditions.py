"""Finite measured-data replay with outcomes hidden from condition policies.

This is a retrospective decision benchmark, not a laboratory or yield simulator.
Only the evaluator loads outcomes; a policy receives ``view()`` dictionaries.
The boundary is an application API, not a security sandbox for untrusted Python.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


def _positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f'{name} must be a positive integer')
    return value


@dataclass(frozen=True)
class ConditionRecord:
    candidate_id: str
    conditions: tuple[tuple[str, str], ...]
    yield_percent: float


@dataclass(frozen=True)
class FiniteConditionStudy:
    """Immutable evaluator state. Never pass this object to an agent/policy."""
    _records: tuple[ConditionRecord, ...]
    observed_ids: tuple[str, ...]
    budget: int | None
    source_url: str
    source_locator: str
    dataset_sha256: str
    substrate: str

    @classmethod
    def from_task(cls, task: dict) -> 'FiniteConditionStudy':
        raw_budget = task.get('budget', 20)
        budget = None if raw_budget is None else _positive_int(raw_budget, 'budget')
        path = Path(task['dataset_path'])
        source_url = task.get('source_url', '')
        source_locator = task.get('source_locator', '')
        if not source_url or not source_locator:
            raise ValueError('source_url and source_locator are required for measured replay')
        columns = task.get('condition_columns', ['ligand', 'additive', 'base'])
        if not columns or len(set(columns)) != len(columns):
            raise ValueError('condition_columns must be a nonempty list of unique column names')
        substrate = task.get('substrate', '')
        if not substrate:
            raise ValueError('substrate is required to avoid mixing different reactions')
        substrate_column = task.get('substrate_column', 'aryl halide')
        yield_column = task.get('yield_column', 'yield')
        if yield_column in columns or substrate_column in columns:
            raise ValueError('condition_columns must exclude yield and substrate columns')
        raw = path.read_bytes()
        reader = csv.DictReader(raw.decode('utf-8-sig').splitlines())
        required = set(columns) | {substrate_column, yield_column}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError(f'Dataset missing columns: {sorted(required - set(reader.fieldnames or ()))!r}')
        records = tuple(_record(row, columns, yield_column) for row in reader
                        if row[substrate_column] == substrate)
        if not records:
            raise ValueError('No measured rows for the requested substrate')
        if len({r.candidate_id for r in records}) != len(records):
            raise ValueError('Duplicate condition combinations require explicit replicate aggregation')
        return cls(records, (), budget, source_url, source_locator,
                   hashlib.sha256(raw).hexdigest(), substrate)

    def view(self) -> dict:
        """A policy may only receive this outcome-filtered representation."""
        return {
            'substrate': self.substrate,
            'candidates': [{'candidate_id': r.candidate_id, 'conditions': dict(r.conditions)}
                           for r in self._records if r.candidate_id not in self.observed_ids],
            'observations': [self._observed_value(key) for key in self.observed_ids],
            'remaining_budget': None if self.budget is None else max(0, self.budget - len(self.observed_ids)),
        }

    def _observed_value(self, candidate_id: str) -> dict:
        record = next(r for r in self._records if r.candidate_id == candidate_id)
        return {'candidate_id': candidate_id, 'conditions': dict(record.conditions),
                'yield_percent': record.yield_percent, 'evidence_kind': 'measured_dataset_replay'}

    def observe(self, candidate_id: str) -> 'FiniteConditionStudy':
        if candidate_id in self.observed_ids:
            raise ValueError('Candidate already observed')
        if candidate_id not in {r.candidate_id for r in self._records}:
            raise ValueError('Unknown candidate')
        if self.budget is not None and len(self.observed_ids) >= self.budget:
            raise ValueError('Condition evaluation budget exhausted')
        return FiniteConditionStudy(self._records, self.observed_ids + (candidate_id,),
                                    self.budget, self.source_url, self.source_locator,
                                    self.dataset_sha256, self.substrate)

    def report(self, policy: str) -> dict:
        observations = self.view()['observations']
        best = max((row['yield_percent'] for row in observations), default=None)
        optimum = max(r.yield_percent for r in self._records)
        return {
            'application': 'condition_optimization', 'policy': policy,
            'evidence_kind': 'measured_dataset_replay', 'observations': observations,
            'budget': self.budget, 'evaluations_used': len(observations),
            'stop_reason': ('candidate_space_exhausted' if len(observations) == len(self._records)
                            else 'budget_exhausted'),
            'best_observed_yield_percent': best,
            'evaluation': {'dataset_optimum_yield_percent': optimum,
                           'simple_regret_percent': None if best is None else optimum - best},
            'provenance': {'source_url': self.source_url, 'source_locator': self.source_locator,
                           'dataset_sha256': self.dataset_sha256, 'substrate': self.substrate},
            'limitations': ['Retrospective dataset replay; no new experiment was performed.',
                           'The evaluator-only optimum is revealed after the run, never to the policy.'],
        }


def _record(row: dict, columns: list, yield_column: str) -> ConditionRecord:
    conditions = tuple((name, row[name]) for name in columns)
    if any(value is None or not value.strip() for _, value in conditions):
        raise ValueError('Missing condition value')
    measured_yield = float(row[yield_column])
    if not math.isfinite(measured_yield) or not 0 <= measured_yield <= 100:
        raise ValueError('Measured yield must be finite and between 0 and 100 percent')
    key = hashlib.sha256(json.dumps(conditions, separators=(',', ':')).encode()).hexdigest()[:20]
    return ConditionRecord(key, conditions, measured_yield)


def _category_ucb(view: dict, rng: random.Random) -> str:
    """Simple marginal observed-category UCB heuristic, not a trained chemistry model."""
    observations = view['observations']
    if not observations:
        return rng.choice(view['candidates'])['candidate_id']
    def score(candidate: dict) -> float:
        terms = []
        for role, value in candidate['conditions'].items():
            outcomes = [row['yield_percent'] for row in observations
                        if row['conditions'][role] == value]
            mean = sum(outcomes) / len(outcomes) if outcomes else 50.0
            bonus = 30.0 * math.sqrt(math.log(len(observations) + 2) / (len(outcomes) + 1))
            terms.append(mean + bonus)
        return sum(terms) / len(terms)
    scored = [(score(candidate), candidate['candidate_id']) for candidate in view['candidates']]
    best = max(value for value, _ in scored)
    return rng.choice([key for value, key in scored if value == best])


def run_condition_task(task: dict, chooser: Callable[[dict], str] | None = None) -> dict:
    policy = task.get('policy', 'fixed_random')
    if policy not in {'fixed_random', 'observed_category_ucb'}:
        raise ValueError('policy must be fixed_random or observed_category_ucb')
    seed = task.get('seed', 0)
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError('seed must be an integer')
    study = FiniteConditionStudy.from_task(task)
    rng = random.Random(seed)
    while True:
        view = study.view()
        if not view['candidates'] or view['remaining_budget'] == 0:
            break
        if chooser is not None:
            selected = chooser(view)
        elif policy == 'fixed_random':
            selected = rng.choice(view['candidates'])['candidate_id']
        else:
            selected = _category_ucb(view, rng)
        study = study.observe(selected)
    return {**study.report('external_policy' if chooser is not None else policy), 'seed': seed}
