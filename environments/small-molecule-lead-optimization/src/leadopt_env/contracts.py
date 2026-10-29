"""Versioned record contracts; scientific omissions are assessed separately."""
import math


def obj(properties, required=()):
    return {"type": "object", "properties": properties,
            "required": list(required), "additionalProperties": False}


S = {"type": "string", "minLength": 1}
N = {"type": "number"}
STRINGS = {"type": "array", "items": S, "uniqueItems": True}


def choice(*values):
    return {"type": "string", "enum": list(values)}


def array(schema):
    return {"type": "array", "items": schema}


CANDIDATE = obj({"id": S, "representation": S, "form_id": S, "source": S,
                 "parent_id": S, "identity_notes": S},
                ("id", "representation", "form_id", "source"))
SIGNATURE = {"endpoint": S, "unit": S, "method": S, "method_version": S,
             "context": S, "kind": choice("predicted", "experimental", "synthetic")}
OBSERVATION = obj({"id": S, "candidate_id": S, "form_id": S, **SIGNATURE,
                   "value": {"type": ["number", "null"]},
                   "qualifier": choice("=", "<", ">", "<=", ">=", "unknown"),
                   "status": choice("completed", "failed", "unknown"),
                   "source": S, "artifact": S, "action_id": S, "uncertainty": S},
                  ("id", "candidate_id", "form_id", "endpoint", "value", "qualifier", "status", "source"))
OBJECTIVE = obj({"id": S, **SIGNATURE, "baseline_id": S,
                 "direction": choice("minimize", "maximize", "range"),
                 "target_min": N, "target_max": N, "minimum_improvement": {"type": "number", "minimum": 0},
                 "support": choice("internal_control", "later_assessment", "unverified", "unsupported"),
                 "support_evidence": S}, ("id", "endpoint", "baseline_id", "direction"))
CONSTRAINT = obj({"id": S, **SIGNATURE, "minimum": N, "maximum": N,
                  "baseline_id": S, "minimum_delta": N, "maximum_delta": N}, ("id", "endpoint"))
TASK = obj({"schema_version": {"type": "integer", "const": 1}, "id": S, "version": S,
            "question": S, "context": S, "sources": STRINGS,
            "starting_candidates": array(CANDIDATE), "initial_observations": array(OBSERVATION),
            "objectives": array(OBJECTIVE), "constraints": array(CONSTRAINT),
            "allowed_jobs": STRINGS,
            "candidate_scope": obj({"mode": choice("analogues", "fixed_library"), "allowed_ids": STRINGS}, ("mode",)),
            "budgets": {"type": "object", "additionalProperties": {"type": "number", "minimum": 0}},
            "evaluation": obj({"kind": choice("search_score", "different_predictor", "heldout_measurement", "synthetic"),
                               "protocol": S, "source_version": S,
                               "objectives": array(OBJECTIVE), "constraints": array(CONSTRAINT)},
                              ("kind", "protocol", "source_version"))},
           ("schema_version", "id", "version"))
CHECK = obj({"id": S, "job": S, "candidate_ids": STRINGS,
             "resource_requests": {"type": "object", "additionalProperties": {"type": "number", "minimum": 0}},
             "question": S}, ("id", "job", "candidate_ids", "resource_requests"))
ACTION = obj({"id": S, "attempt_id": S, "job": S, "candidate_ids": STRINGS,
              "status": choice("accepted", "running", "completed", "failed", "unknown"),
              "check_id": S, "job_id": S, "source": S, "rationale": S},
             ("id", "attempt_id", "job", "candidate_ids", "status", "source"))
USAGE = obj({"id": S, "unit": S, "amount": {"type": ["number", "null"], "minimum": 0},
             "category": choice("requested", "observed", "estimated", "unknown"),
             "scope": S, "source": S, "attempt_id": S},
            ("id", "unit", "amount", "category", "scope", "source"))
DECISION = obj({"id": S, "question": S, "outcome": choice("supported", "contradicted", "inconclusive"),
                "evidence_ids": STRINGS, "next_action": S, "rationale": S},
               ("id", "question", "outcome", "evidence_ids", "next_action", "rationale"))
FREEZE = obj({"id": S, "candidate_ids": STRINGS, "rationale": S, "stopping_reason": S},
             ("id", "candidate_ids", "rationale", "stopping_reason"))
SCHEMAS = {"task": TASK, "candidate": CANDIDATE, "observation": OBSERVATION,
           "check": CHECK, "action": ACTION, "usage": USAGE, "decision": DECISION, "freeze": FREEZE}


def validate(value, schema, path="record"):
    """Validate the JSON Schema subset used above, without runtime dependencies."""
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    checks = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
              "string": lambda v: isinstance(v, str), "null": lambda v: v is None,
              "number": lambda v: type(v) in (int, float) and math.isfinite(v),
              "integer": lambda v: type(v) is int}
    if types and not any(checks[t](value) for t in types):
        raise ValueError(f"{path}: expected {types}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: unsupported value")
    if "const" in schema and value != schema["const"]:
        raise ValueError(f"{path}: unsupported schema version")
    if isinstance(value, str) and (len(value) < schema.get("minLength", 0) or not value.strip()):
        raise ValueError(f"{path}: empty string")
    if type(value) in (float, int) and value < schema.get("minimum", -math.inf):
        raise ValueError(f"{path}: below minimum")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(f"{path}: missing {key}")
        for key, item in value.items():
            child = schema.get("properties", {}).get(key, schema.get("additionalProperties", True))
            if child is False:
                raise ValueError(f"{path}: unknown field {key}")
            if isinstance(child, dict):
                validate(item, child, f"{path}.{key}")
    if isinstance(value, list):
        if schema.get("uniqueItems") and len(value) != len(set(value)):
            raise ValueError(f"{path}: duplicate values")
        for i, item in enumerate(value):
            validate(item, schema.get("items", {}), f"{path}[{i}]")


def validate_task(task):
    validate(task, TASK, "task")
    groups = [(group, task.get(group, [])) for group in ("starting_candidates", "initial_observations", "objectives", "constraints")]
    groups += [("evaluation." + group, task.get("evaluation", {}).get(group, [])) for group in ("objectives", "constraints")]
    for group, records in groups:
        ids = [r["id"] for r in records]
        if len(ids) != len(set(ids)):
            raise ValueError(f"task.{group}: duplicate IDs")
    rules = task.get("objectives", []) + task.get("constraints", [])
    rules += task.get("evaluation", {}).get("objectives", []) + task.get("evaluation", {}).get("constraints", [])
    for rule in rules:
        for lo, hi in (("target_min", "target_max"), ("minimum", "maximum"), ("minimum_delta", "maximum_delta")):
            if lo in rule and hi in rule and rule[lo] > rule[hi]:
                raise ValueError(f"{rule['id']}: inverted range")
