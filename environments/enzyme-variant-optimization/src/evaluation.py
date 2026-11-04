"""Compare reviewed, same-protocol measurements without executing scientific tools."""
from __future__ import annotations

import math
import re
from statistics import mean


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value


def _number(value, field):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be a finite number")
    return number


def _identity(row):
    candidate = _text(row.get("candidate_id"), "candidate_id")
    sequence_hash = row.get("sequence_sha256")
    if not isinstance(sequence_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", sequence_hash):
        raise ValueError(f"{candidate}: sequence_sha256 must be a lowercase SHA-256 digest")
    return candidate, sequence_hash


def evaluate(protocol, observations, selection):
    """Score only a fully observed eligible selection; retain missing and rejected rows.

    Eligibility and evidence references are reviewer declarations. This function
    neither verifies molecular artifacts nor establishes statistical significance.
    """
    for key in ("parent_id", "metric", "unit", "protocol_id"):
        _text(protocol.get(key), key)
    direction = protocol.get("direction")
    if direction not in ("minimize", "maximize"):
        raise ValueError("direction must be minimize or maximize")
    maximum = protocol.get("max_selected")
    if type(maximum) is not int or maximum < 1:
        raise ValueError("max_selected must be a positive integer")
    margin = _number(protocol.get("min_improvement"), "min_improvement")
    if margin < 0:
        raise ValueError("min_improvement must be nonnegative")
    if type(protocol.get("ratio_allowed")) is not bool:
        raise ValueError("ratio_allowed must be a boolean")
    if len(selection) > maximum:
        raise ValueError("selection exceeds max_selected")

    selected_ids, selected_hashes, selected = set(), set(), []
    for rank, row in enumerate(selection, 1):
        candidate, sequence_hash = _identity(row)
        if str(row.get("rank")) != str(rank):
            raise ValueError("selection ranks must be contiguous from 1 in file order")
        if candidate == protocol["parent_id"]:
            raise ValueError("parent cannot appear in the designed selection")
        if candidate in selected_ids or sequence_hash in selected_hashes:
            raise ValueError("selection contains duplicate IDs or sequences")
        selected_ids.add(candidate)
        selected_hashes.add(sequence_hash)
        selected.append((candidate, sequence_hash, rank))

    measured = {}
    for row in observations:
        candidate, sequence_hash = _identity(row)
        if candidate in measured:
            raise ValueError(f"{candidate}: duplicate observation")
        for key in ("metric", "unit", "protocol_id"):
            if row.get(key) != protocol[key]:
                raise ValueError(f"{candidate}: incompatible {key}")
        eligibility = row.get("eligibility")
        if eligibility not in ("true", "false", "unknown"):
            raise ValueError(f"{candidate}: eligibility must be true, false or unknown")
        _text(row.get("evidence_path"), "evidence_path")
        value = row.get("value")
        value = None if value is None or value == "" else _number(value, f"{candidate} value")
        measured[candidate] = (sequence_hash, value, eligibility, row["evidence_path"])

    parent = measured.get(protocol["parent_id"])
    parent_value = parent[1] if parent and parent[2] == "true" else None
    if parent and parent[0] in selected_hashes:
        raise ValueError("parent sequence cannot appear under another selected ID")
    rows = []
    for candidate, sequence_hash, rank in selected:
        observation = measured.get(candidate)
        item = {"candidate_id": candidate, "rank": rank, "sequence_sha256": sequence_hash,
                "value": None, "status": "unresolved", "signed_improvement": None,
                "numerically_improved": None, "parent_ratio": None, "evidence_path": None}
        if observation:
            observed_hash, value, eligibility, evidence = observation
            if sequence_hash != observed_hash:
                raise ValueError(f"{candidate}: selection and observation sequence hashes disagree")
            item.update(value=value, evidence_path=evidence)
            if eligibility == "false":
                item["status"] = "ineligible"
            elif eligibility == "true" and value is not None and parent_value is not None:
                delta = value - parent_value if direction == "maximize" else parent_value - value
                if not math.isfinite(delta):
                    raise ValueError(f"{candidate}: comparison overflow")
                item.update(status="evaluated", signed_improvement=delta,
                            numerically_improved=delta > margin)
                if protocol["ratio_allowed"] and parent_value > 0 and value >= 0:
                    ratio = value / parent_value
                    if not math.isfinite(ratio):
                        raise ValueError(f"{candidate}: ratio overflow")
                    item["parent_ratio"] = ratio
        rows.append(item)

    eligible = [row for row in rows if row["status"] == "evaluated"]
    complete = bool(rows) and len(eligible) == len(rows)
    status = "scored" if complete else "incomplete"
    if not rows:
        status = "no_selection"
    elif any(row["status"] == "ineligible" for row in rows):
        status = "invalid_selection"
    return {"status": status, "metric": protocol["metric"], "unit": protocol["unit"],
            "protocol_id": protocol["protocol_id"], "parent_value": parent_value,
            "selected_count": len(rows), "evaluated_eligible_count": len(eligible),
            "numerically_improved_count": sum(row["numerically_improved"] for row in eligible),
            "mean_signed_improvement": mean(row["signed_improvement"] for row in eligible) if complete else None,
            "rows": rows,
            "scope": "Reviewed declarations only; not molecular validation or experimental proof."}
