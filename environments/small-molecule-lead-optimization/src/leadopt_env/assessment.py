"""Conservative numerical comparisons; no molecular equivalence inference."""
import math

from .contracts import SIGNATURE


def warning(code, detail, category="missing_information"):
    return {"code": code, "category": category, "detail": detail}


def task_warnings(task):
    findings = []
    for key in ("question", "context", "sources", "starting_candidates", "objectives", "allowed_jobs", "budgets", "candidate_scope", "evaluation"):
        if not task.get(key):
            findings.append(warning("missing_task_information", key))
    for objective in task.get("objectives", []):
        if objective.get("support") not in ("internal_control", "later_assessment") or not objective.get("support_evidence"):
            findings.append(warning("objective_support_unverified", objective["id"]))
        if any(not objective.get(k) for k in SIGNATURE):
            findings.append(warning("objective_signature_incomplete", objective["id"]))
    return findings


def eligible(candidate_id, task):
    scope = task.get("candidate_scope", {})
    if scope.get("mode") == "analogues":
        return "pass"
    if scope.get("mode") == "fixed_library" and "allowed_ids" in scope:
        return "pass" if candidate_id in scope["allowed_ids"] else "fail"
    return "unresolved"


def evidence_for(candidate_id, rule, candidates, observations, action_status=None):
    candidate = candidates.get(candidate_id)
    if candidate is None:
        return None, "unknown candidate"
    if any(not rule.get(k) for k in SIGNATURE):
        return None, "incomplete endpoint/method/context signature"
    matches = [r for r in observations if r["candidate_id"] == candidate_id
               and r["form_id"] == candidate["form_id"]
               and all(r.get(k) == rule[k] for k in SIGNATURE)]
    if len(matches) != 1:
        return None, "missing evidence" if not matches else "multiple observations require an explicit aggregation policy"
    record = matches[0]
    if record.get("action_id") and (action_status or {}).get(record["action_id"]) != "completed":
        return None, "linked action has not completed successfully"
    if record["status"] != "completed" or record["qualifier"] != "=" or record["value"] is None:
        return None, "incomplete or censored evidence"
    return record, None


def assess(task, candidates, observations, action_status=None):
    comparisons, assessments = [], []
    for cid in candidates:
        for rule in task.get("objectives", []):
            row = {"candidate_id": cid, "objective_id": rule["id"], "status": "unresolved",
                   "delta": None, "improvement": None, "evidence_kind": rule.get("kind"),
                   "baseline_id": rule["baseline_id"]}
            current, issue = evidence_for(cid, rule, candidates, observations, action_status)
            baseline, base_issue = evidence_for(rule["baseline_id"], rule, candidates, observations, action_status)
            if issue or base_issue:
                row["reason"] = issue or base_issue
            elif rule.get("support") not in ("internal_control", "later_assessment") or not rule.get("support_evidence"):
                row["reason"] = "objective capability support is unresolved"
            else:
                delta = current["value"] - baseline["value"]
                if rule["direction"] == "range":
                    if "target_min" not in rule or "target_max" not in rule:
                        row["reason"] = "missing target range"
                        comparisons.append(row)
                        continue
                    lo, hi = rule["target_min"], rule["target_max"]
                    distance = lambda x: max(lo - x, 0, x - hi)
                    improvement = distance(baseline["value"]) - distance(current["value"])
                else:
                    improvement = delta * (1 if rule["direction"] == "maximize" else -1)
                if not math.isfinite(delta) or not math.isfinite(improvement):
                    row["reason"] = "comparison exceeds finite numeric range"
                    comparisons.append(row)
                    continue
                minimum = rule.get("minimum_improvement", 0)
                passed = improvement >= minimum if minimum > 0 else improvement > 0
                row.update(delta=delta, improvement=improvement, status="pass" if passed else "fail",
                           observation_id=current["id"], baseline_observation_id=baseline["id"],
                           baseline_value=baseline["value"], candidate_value=current["value"])
            comparisons.append(row)
        for rule in task.get("constraints", []):
            row = {"candidate_id": cid, "constraint_id": rule["id"], "status": "unresolved"}
            current, issue = evidence_for(cid, rule, candidates, observations, action_status)
            bounds = ("minimum", "maximum", "minimum_delta", "maximum_delta")
            if issue:
                row["reason"] = issue
            elif not any(k in rule for k in bounds):
                row["reason"] = "missing constraint bound"
            else:
                failures = []
                value = current["value"]
                if "minimum" in rule: failures.append(value < rule["minimum"])
                if "maximum" in rule: failures.append(value > rule["maximum"])
                if "minimum_delta" in rule or "maximum_delta" in rule:
                    baseline, issue = evidence_for(rule.get("baseline_id"), rule, candidates, observations, action_status)
                    if issue:
                        row["reason"] = issue
                        assessments.append(row)
                        continue
                    delta = value - baseline["value"]
                    if not math.isfinite(delta):
                        row["reason"] = "comparison exceeds finite numeric range"
                        assessments.append(row)
                        continue
                    if "minimum_delta" in rule: failures.append(delta < rule["minimum_delta"])
                    if "maximum_delta" in rule: failures.append(delta > rule["maximum_delta"])
                    row["delta"] = delta
                row.update(status="fail" if any(failures) else "pass", observation_id=current["id"])
            assessments.append(row)
    return comparisons, assessments


def resource_summary(records):
    """Each record is an increment, not a cumulative counter. Unknowns never sum to zero."""
    result = {}
    for r in records:
        unit = result.setdefault(r["unit"], {})
        key = (r["category"], r["scope"])
        bucket = unit.setdefault("|".join(key), {"category": key[0], "scope": key[1], "amount": 0, "record_ids": []})
        bucket["record_ids"].append(r["id"])
        bucket["amount"] = None if r["amount"] is None or bucket["amount"] is None else bucket["amount"] + r["amount"]
    return result


def budget_warnings(task, usage, requested=None):
    findings = []
    for unit, limit in task.get("budgets", {}).items():
        observed = [r for r in usage if r["unit"] == unit and r["category"] == "observed" and r["scope"] == "campaign"]
        unknown = [r for r in usage if r["unit"] == unit and (r["category"] == "unknown" or r["amount"] is None)]
        total = sum(r["amount"] for r in observed if r["amount"] is not None)
        if not observed or unknown:
            findings.append(warning("usage_incomplete", unit))
        if total > limit or total + (requested or {}).get(unit, 0) > limit:
            findings.append(warning("budget_exceeded", f"{unit}: observed {total}, allowance {limit}", "violation"))
        elif total == limit:
            findings.append(warning("budget_reached", f"{unit}: observed {total}, allowance {limit}", "advice"))
    return findings
