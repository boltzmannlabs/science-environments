"""Explicit local resource-regime conversion; scientific permissions stay bound."""
from dataclasses import replace
import math
from .schemas import Budget


def task_regime(task, regime=None):
    regime = task.budget.regime if regime is None else regime
    if regime not in {'budgeted', 'unbudgeted'}:
        raise ValueError('Unknown budget regime')
    if regime == task.budget.regime:
        return task
    if regime == 'budgeted':
        raise ValueError('Supply explicit finite task ceilings to restore budgeted execution')
    return task.model_copy(update={'budget': Budget.unbudgeted(top_k=task.budget.top_k)})


def science_regime(options, regime):
    if regime not in {'budgeted', 'unbudgeted'}:
        raise ValueError('Unknown budget regime')
    result = dict(options)
    if regime == 'budgeted':
        return result
    limits = result.get('scientific_limits')
    if limits is not None:
        result = {**result, 'scientific_limits': replace(limits,
            retrieval_calls=0 if limits.retrieval_calls == 0 else None,
            observation_calls=0 if limits.observation_calls == 0 else None)}
    study = result.get('condition_study')
    if study is not None:
        result = {**result, 'condition_study': replace(study, budget=None)}
    return result


def tool_timeout(value, episode_limit):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('Tool timeout must be finite and positive')
    return value if episode_limit is None else min(value, episode_limit)


def host_allowance(value, regime, default, name):
    if regime == 'unbudgeted':
        if value is not None:
            raise ValueError(f'{name} cannot impose a finite ceiling in unbudgeted execution')
        return None
    return default if value is None else value
