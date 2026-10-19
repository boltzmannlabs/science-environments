"""Host-enforced protocol: no arbitrary paths, commands or remote tool calls."""
import csv
import hashlib
import json
import math
import threading
import time
from pathlib import Path
from enzyme_environment.data_views import compact_scores

TOOLS = (
    {"type": "function", "name": "benchmark_read", "description": "Read a permitted benchmark dataset page.",
     "parameters": {"type": "object", "properties": {
         "dataset": {"type": "string", "enum": ["task", "candidates", "train", "development"]},
         "offset": {"type": "integer", "minimum": 0},
         "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
         "required": ["dataset"], "additionalProperties": False}},
    {"type": "function", "name": "benchmark_submit", "description": "Submit exactly ten unique candidate IDs in ranked order, once.",
     "parameters": {"type": "object", "properties": {
         "candidate_ids": {"type": "array", "items": {"type": "string"}, "minItems": 10, "maxItems": 10},
         "rationale": {"type": "string", "maxLength": 4000}},
         "required": ["candidate_ids", "rationale"], "additionalProperties": False}},
)
NAMES = frozenset(t["name"] for t in TOOLS)
SCORE_TOOL = {"type": "function", "name": "benchmark_score",
    "description": "Predict scores for 1-50 known candidates using the pinned frozen predictor. Predictions are not experimental answers or kcat.",
    "parameters": {"type": "object", "properties": {
        "candidate_ids": {"type": "array", "items": {"type": "string"},
                          "minItems": 1, "maxItems": 50, "uniqueItems": True}},
        "required": ["candidate_ids"], "additionalProperties": False}}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def strict_json(raw):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("Duplicate JSON key")
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Non-finite JSON")))


class Audit:
    """Hash-chained log held outside the guest. Host operator remains trusted."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("x", encoding="utf-8")
        self.previous = "0" * 64
        self.lock = threading.RLock()

    def record(self, kind, **values):
        with self.lock:
            row = {"time_ns": time.time_ns(), "kind": kind, "previous": self.previous, **values}
            row["hash"] = digest(row)
            self.previous = row["hash"]
            self.file.write(json.dumps(row, sort_keys=True) + "\n")
            self.file.flush()

    def close(self):
        self.file.close()


def verify_audit(path):
    previous = "0" * 64
    rows = []
    for line in Path(path).read_text().splitlines():
        row = strict_json(line)
        actual = row.pop("hash")
        if row["previous"] != previous or digest(row) != actual:
            raise ValueError("Audit chain mismatch")
        row["hash"] = actual
        previous = actual
        rows.append(row)
    return rows


class Policy:
    def __init__(self, datasets, output, audit, predictor=None, max_unique_scores=200,compact_candidates=False):
        self.datasets = datasets
        if type(compact_candidates) is not bool:raise ValueError("Compact observation control must be boolean internally")
        self.compact_candidates=compact_candidates
        self.output = Path(output)
        self.audit = audit
        self.known = {r["candidate_id"] for r in datasets["candidates"]}
        if len(self.known) != len(datasets["candidates"]):
            raise ValueError("Duplicate pool IDs")
        if type(max_unique_scores) is not int or not 1 <= max_unique_scores <= 200:
            raise ValueError("Unique prediction budget must be an integer from 1 to 200")
        if predictor is not None and predictor.candidate_ids != self.known:
            raise ValueError("Predictor and policy candidate pools differ")
        self.predictor = predictor
        self.max_unique_scores = max_unique_scores
        self.prediction_cache = {}
        self.score_requests = 0
        self.cache_hits = 0
        self.tools = TOOLS if predictor is None else (*TOOLS, SCORE_TOOL)
        self.names = frozenset(t["name"] for t in self.tools)
        self.submitted = False
        self.calls = 0
        self.lock = threading.RLock()

    def tool(self, name, args):
        with self.lock:
            self.calls += 1
            try:
                if self.calls > 200:
                    raise ValueError("Tool-call limit reached")
                if name not in self.names or not isinstance(args, dict):
                    raise ValueError("Tool not permitted or invalid arguments")
                if name == "benchmark_read":
                    if set(args) - {"dataset", "offset", "limit"}:
                        raise ValueError("Unexpected read field")
                    key = args.get("dataset")
                    if key not in self.datasets:
                        raise ValueError("Dataset not permitted")
                    offset, limit = args.get("offset", 0), args.get("limit", 50)
                    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 50:
                        raise ValueError("Invalid page")
                    rows = self.datasets[key]
                    result = {"dataset": key, "total": len(rows), "rows": rows[offset:offset + limit]}
                    if key=="candidates" and self.compact_candidates:
                        result["rows"]=[{"candidate_id":r["candidate_id"],"mutation":r["mutation"]} for r in result["rows"]]
                        result["representation"]="reference_sequence_in_task_plus_single_substitution"
                        result["omitted_redundant_fields"]=["sequences"]
                elif name == "benchmark_score":
                    if set(args) != {"candidate_ids"}:
                        raise ValueError("Unexpected or missing score field")
                    if self.submitted:
                        raise ValueError("Selection already submitted; prediction is closed")
                    ids = self.predictor.validate_request(args["candidate_ids"])
                    new = [cid for cid in ids if cid not in self.prediction_cache]
                    if len(self.prediction_cache) + len(new) > self.max_unique_scores:
                        raise ValueError("Unique candidate-score budget exceeded")
                    values = {cid: self.predictor.predict_one(cid) for cid in new}
                    if any(type(value) not in (int, float) or not math.isfinite(value) for value in values.values()):
                        raise ValueError("Frozen predictor produced invalid values")
                    self.prediction_cache.update(values)
                    self.score_requests += len(ids)
                    self.cache_hits += len(ids) - len(new)
                    result = {"model_id": self.predictor.model_id,
                              "score_type": "prediction_not_experimental_measurement",
                              "rows": [{"candidate_id": cid, "predicted_score": self.prediction_cache[cid]}
                                       for cid in ids],
                              "accounting": {"unique_candidates_scored": len(self.prediction_cache),
                                             "candidate_score_requests": self.score_requests,
                                             "cache_hits": self.cache_hits,
                                             "unique_candidate_limit": self.max_unique_scores}}
                    if self.compact_candidates:
                        result=compact_scores(result)
                else:
                    if set(args) != {"candidate_ids", "rationale"}:
                        raise ValueError("Unexpected or missing submission field")
                    ids, why = args["candidate_ids"], args["rationale"]
                    if not isinstance(ids, list) or len(ids) != 10 or any(not isinstance(x, str) for x in ids):
                        raise ValueError("Exactly ten candidate IDs required")
                    if len(set(ids)) != 10 or not set(ids) <= self.known:
                        raise ValueError("Duplicate or unknown candidate ID")
                    if not isinstance(why, str) or not why.strip() or len(why) > 4000:
                        raise ValueError("A short rationale is required")
                    if self.submitted:
                        raise ValueError("Selection already submitted; no overwrite allowed")
                    self.output.mkdir(parents=True, exist_ok=True)
                    with (self.output / "selection.csv").open("x", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["candidate_id", "rank"])
                        writer.writerows((item, i) for i, item in enumerate(ids, 1))
                    (self.output / "rationale.txt").write_text(why + "\n")
                    self.submitted = True
                    result = {"accepted": True, "count": 10}
                self.audit.record("tool", name=name, arguments=args, allowed=True, result_hash=digest(result))
                return result
            except (ValueError, TypeError, OSError) as exc:
                self.audit.record("tool", name=str(name)[:100], arguments_hash=digest(args), allowed=False, error=str(exc))
                raise


def validate_model_request(body, tools=TOOLS):
    if not isinstance(body, dict):
        raise ValueError("Model request must be an object")
    allowed = {"model", "input", "instructions", "tools", "tool_choice", "parallel_tool_calls", "stream", "store",
               "reasoning", "text", "max_output_tokens", "include", "truncation", "prompt_cache_key"}
    if set(body) - allowed:
        raise ValueError("Unapproved model request fields: " + ", ".join(sorted(set(body) - allowed)))
    if body.get("model") != "gpt-6.1-sol" or body.get("stream") is not True or body.get("store", False) is not False:
        raise ValueError("Pinned streaming model and store=false required")
    if "prompt_cache_key" in body and (not isinstance(body["prompt_cache_key"], str) or not 1 <= len(body["prompt_cache_key"]) <= 128):
        raise ValueError("Invalid cache scope")
    requested_tools = body.get("tools", [])
    if not isinstance(requested_tools, list) or any(not isinstance(t, dict) or not isinstance(t.get("name"), str) for t in requested_tools):
        raise ValueError("Invalid tool list")
    if len(requested_tools) != len(tools) or {t.get("name") for t in requested_tools} != {t["name"] for t in tools}:
        raise ValueError("Only the configured benchmark tools are permitted")
    for tool in requested_tools:
        reference = next(t for t in tools if t["name"] == tool.get("name"))
        if tool.get("type") != "function" or tool.get("parameters") != reference["parameters"]:
            raise ValueError("Tool schema changed")
    maximum = body.get("max_output_tokens", 4096)
    if type(maximum) is not int or not 1 <= maximum <= 4096:
        raise ValueError("Model output limit exceeded")
    # Reject remote image/file references and any nested data-fetching instructions.
    def scan(value):
        if isinstance(value, dict):
            if any(k in value for k in ("image_url", "file_url", "file_id", "server_url", "connector_id")):
                raise ValueError("Remote content is not permitted")
            for item in value.values():
                scan(item)
        elif isinstance(value, list):
            for item in value:
                scan(item)
    scan(body)
    return body
