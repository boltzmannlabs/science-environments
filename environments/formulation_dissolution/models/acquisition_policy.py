"""Transparent illustrative acquisition ranking, not a validated policy."""


def rank(items: list[dict], weights: dict[str,float], *, remaining_cost: float | None = None) -> list[dict]:
    """Require all objectives and verified feasibility; maximize weighted score."""
    if not weights or any(not isinstance(v, (int,float)) or v < 0 for v in weights.values()):
        raise ValueError('explicit nonnegative objective weights required')
    output = []
    for item in items:
        if item.get('feasible') is not True:
            continue
        if any(k not in item.get('objectives', {}) for k in weights):
            continue
        cost = item.get('cost')
        if cost is None or cost < 0 or remaining_cost is not None and cost > remaining_cost:
            continue
        score = sum(weights[k] * item['objectives'][k] for k in weights)
        output.append({'id':item['id'],'score':score,'cost':cost,'status':'illustrative_unvalidated'})
    return sorted(output, key=lambda x:(-x['score'], x['cost'], x['id']))
