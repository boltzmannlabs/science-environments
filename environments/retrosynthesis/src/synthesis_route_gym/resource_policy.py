"""Pure resource projections shared by native and chemistry-process advisors.

Null means no aggregate ceiling only within an explicit unbudgeted contract;
unknown usage is represented separately in the accounting ledger.
"""
import math


RESOURCE_KEYS = ('remaining_model_calls', 'remaining_tool_calls', 'remaining_tokens', 'remaining_seconds')


def _nonnegative(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{label} must be finite and nonnegative')


def remaining(limit, used):
    """Return unbounded (None) or nonnegative remaining finite resources."""
    _nonnegative(used, 'usage')
    if limit is None:
        return None
    _nonnegative(limit, 'limit')
    return max(0, limit - used)


def agent_resources(ledger):
    """Preserve finite context identities and explicitly mark unlimited contexts."""
    snapshot, limits = ledger.snapshot(), ledger.budget
    values = {
        'remaining_model_calls': remaining(limits.max_model_calls, snapshot['model_calls']),
        'remaining_tool_calls': remaining(limits.max_tool_calls, snapshot['tool_calls']),
        'remaining_tokens': remaining(limits.max_total_tokens, snapshot['charged_tokens']),
        'remaining_seconds': remaining(limits.wall_seconds, snapshot['elapsed_seconds']),
    }
    return {**values, 'regime': 'unbudgeted'} if limits.regime == 'unbudgeted' else values


def _validate_resources(resources, regime):
    expected = set(RESOURCE_KEYS) | ({'regime'} if regime == 'unbudgeted' else set())
    if not isinstance(resources, dict) or set(resources) != expected:
        raise ValueError('Resource projection must explicitly match budget regime')
    if regime == 'unbudgeted':
        if resources['regime'] != regime or any(resources[key] is not None for key in RESOURCE_KEYS):
            raise ValueError('Unbudgeted remaining resources must all be null')
    else:
        for key in RESOURCE_KEYS:
            _nonnegative(resources[key], key)


def advisor_admissible(ledger, resources, prompt):
    """Apply finite parent-finalization reserves, never invent unlimited ceilings."""
    limits = ledger.budget
    _validate_resources(resources, limits.regime)
    if not isinstance(prompt, str):
        raise ValueError('Advisor prompt must be text')
    if limits.regime == 'unbudgeted':
        return True
    input_bound = len(prompt.encode('utf-8')) + 4096
    return (not ledger.finalization_only
        and resources['remaining_model_calls'] >= max(3, limits.finalization_model_calls + 2)
        and resources['remaining_tool_calls'] >= limits.finalization_tool_calls + 2
        and resources['remaining_tokens'] >= input_bound + limits.max_output_tokens_per_call
            + math.ceil(limits.max_total_tokens * limits.finalization_token_fraction)
        and resources['remaining_seconds'] > max(1, limits.wall_seconds * limits.finalization_wall_fraction))
