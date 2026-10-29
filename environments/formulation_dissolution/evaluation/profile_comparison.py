"""Comparison of supplied profiles, never replacement of missing measurements."""

import math
from evaluation.six_model_pipeline import scores

CONTEXT = (
    "api",
    "strength_mg",
    "dosage_form",
    "method_id",
    "method_version",
    "storage_condition",
    "time_unit",
    "release_unit",
    "dose_basis",
    "candidate_id",
)


def compare(predicted, observed):
    """Matched user-supplied profiles; no fitting, interpolation or QC decision.

    Input objects contain CONTEXT, time, values, evidence_label, data_origin,
    source_id. Measured provenance is an attestation, not independently
    authenticated by this function. f1/f2 are mathematical factors only.
    """
    if observed is None:
        return {
            "status": "not_evaluated",
            "reason": "missing experimental observations",
        }
    if not isinstance(predicted, dict) or not isinstance(observed, dict):
        raise ValueError("profile objects required")
    if (
        observed.get("evidence_label") != "measured"
        or observed.get("data_origin") != "experimental"
        or not observed.get("source_id")
    ):
        raise ValueError("source-linked measured experimental observations required")
    if predicted.get("evidence_label") != "predicted":
        raise ValueError("prediction evidence label required")
    if any(
        predicted.get(k) is None
        or observed.get(k) is None
        or predicted[k] != observed[k]
        for k in CONTEXT
    ):
        return {
            "status": "not_evaluated",
            "reason": "missing or incompatible scientific context",
        }
    if predicted["release_unit"] != "%" or predicted["time_unit"] not in ("h", "min"):
        raise ValueError("matching explicit % release and h or min time units required")
    ts = observed.get("time", [])
    ys, ps = observed.get("values", []), predicted.get("values", [])
    if (
        not ts
        or ts != predicted.get("time")
        or len(ys) != len(ts)
        or len(ps) != len(ts)
    ):
        raise ValueError(
            "aligned original time grid and values required; no interpolation"
        )
    if not all(
        isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
        for x in ts + ys + ps
    ):
        raise ValueError("finite numeric times and values required")
    if ts != sorted(set(ts)) or ts[0] < 0:
        raise ValueError("unique increasing nonnegative times required")
    pairs = [(a, p) for t, a, p in zip(ts, ys, ps) if t > 0]
    if not pairs:
        raise ValueError("nonzero times required")
    a, p = map(list, zip(*pairs))
    result = {
        "status": "evaluated_supplied_profile_discrepancy",
        **scores(a, p),
        "source_id": observed["source_id"],
        "n_scored_times": len(a),
        "f1_math_only": None,
        "f2_math_only": None,
        "regulatory_similarity": "not_evaluated",
        "limitation": "single supplied profile discrepancy, not independent held-out validation; provenance is caller-attested",
    }
    if len(a) >= 3 and all(0 <= x <= 100 for x in a + p) and sum(a) > 0:
        # Restrict late-time redundancy, but do NOT infer required unit counts,
        # CV limits, sample design, ER method acceptability or regulatory status.
        if sum(x > 85 for x in a) <= 1 and sum(x > 85 for x in p) <= 1:
            result["f1_math_only"] = (
                100 * sum(abs(x - y) for x, y in zip(a, p)) / sum(a)
            )
            result["f2_math_only"] = 50 * math.log10(
                100 / math.sqrt(1 + sum((x - y) ** 2 for x, y in zip(a, p)) / len(a))
            )
    return result
