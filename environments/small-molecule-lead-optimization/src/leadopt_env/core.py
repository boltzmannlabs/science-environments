"""Transactional advisory records. Never submits scientific jobs."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from .assessment import assess, budget_warnings, eligible, resource_summary, task_warnings, warning
from .contracts import SCHEMAS, S, obj, validate, validate_task


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class CampaignStore:
    def __init__(self, db_path):
        self.path = Path(db_path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    id TEXT PRIMARY KEY, task TEXT NOT NULL, created TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, campaign TEXT NOT NULL,
                    kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL,
                    UNIQUE(campaign, kind, id), FOREIGN KEY(campaign) REFERENCES campaigns(id));
                CREATE TABLE IF NOT EXISTS bindings (
                    session TEXT PRIMARY KEY, campaign TEXT NOT NULL,
                    FOREIGN KEY(campaign) REFERENCES campaigns(id));
            """)

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def _append(self, db, cid, kind, eid, data):
        old = db.execute("SELECT data FROM events WHERE campaign=? AND kind=? AND id=?", (cid, kind, eid)).fetchone()
        encoded = canonical(data)
        if old:
            if old["data"] != encoded:
                raise ValueError(f"conflicting {kind} ID: {eid}")
            return False
        db.execute("INSERT INTO events(campaign,kind,id,data,created) VALUES(?,?,?,?,?)", (cid, kind, eid, encoded, self._now()))
        return True

    def _records(self, db, cid):
        return [{"sequence": r["seq"], "kind": r["kind"], "id": r["id"],
                 "recorded_at": r["created"], "data": json.loads(r["data"])}
                for r in db.execute("SELECT * FROM events WHERE campaign=? ORDER BY seq", (cid,))]

    def _report(self, db, cid, task):
        events = self._records(db, cid)
        grouped = {kind: [e["data"] for e in events if e["kind"] == kind]
                   for kind in SCHEMAS if kind != "task"}
        candidates = {r["id"]: r for r in grouped["candidate"]}
        latest_actions = {r["attempt_id"]: r for r in grouped["action"]}
        action_status = {r["id"]: latest_actions[r["attempt_id"]]["status"] for r in grouped["action"]}
        comparisons, constraints = assess(task, candidates, grouped["observation"], action_status)
        pending = [r for r in latest_actions.values() if r["status"] in ("accepted", "running", "unknown")]
        checks = {r["request"]["id"]: r for r in grouped["check"]}
        commitments = [{"attempt_id": r["attempt_id"], "status": r["status"],
                        "resource_requests": checks.get(r.get("check_id"), {}).get("request", {}).get("resource_requests"),
                        "observed_consumption": False} for r in pending]
        findings = task_warnings(task) + budget_warnings(task, grouped["usage"])
        for r in grouped["action"]:
            if "allowed_jobs" in task and r["job"] not in task["allowed_jobs"]:
                findings.append(warning("job_not_allowed", r["id"], "violation"))
            for candidate_id in r["candidate_ids"]:
                if eligible(candidate_id, task) == "fail":
                    findings.append(warning("candidate_not_allowed", candidate_id, "violation"))
                if candidate_id not in candidates:
                    findings.append(warning("unknown_candidate", candidate_id))
            check = checks.get(r.get("check_id"))
            if check is None:
                findings.append(warning("action_without_check", r["id"]))
            elif check["request"]["job"] != r["job"] or check["request"]["candidate_ids"] != r["candidate_ids"]:
                findings.append(warning("action_differs_from_check", r["id"]))
        return {"schema_version": 1, "campaign_id": cid, "task": task, "task_digest": digest(task),
                "candidates": list(candidates.values()), "observations": grouped["observation"],
                "actions": grouped["action"], "checks": grouped["check"], "decisions": grouped["decision"],
                "usage": grouped["usage"], "resource_summary": resource_summary(grouped["usage"]),
                "unresolved_usage_commitments": commitments, "comparisons": comparisons,
                "assessments": constraints, "candidate_eligibility": {k: eligible(k, task) for k in candidates},
                "warnings": findings, "sessions": [r[0] for r in db.execute("SELECT session FROM bindings WHERE campaign=? ORDER BY session", (cid,))],
                "freezes": [{"id": r["request"]["id"], "digest": r["digest"]} for r in grouped["freeze"]],
                "events": events,
                "coverage": {"mode": "explicit_agent_records", "complete": False,
                             "limitations": ["Scientific calls are not intercepted or submitted by this environment.",
                                             "Records and provenance are agent supplied, not independently authenticated.",
                                             "Remote internal scoring and unrecorded model/tool calls remain unknown.",
                                             "Campaign storage is not an access-control or evaluator-isolation boundary."]}}

    def _check(self, report, request):
        task = report["task"]
        findings = task_warnings(task) + budget_warnings(task, report["usage"], request["resource_requests"])
        allowed = task.get("allowed_jobs")
        if allowed is not None and request["job"] not in allowed:
            findings.append(warning("job_not_allowed", request["job"], "violation"))
        known = {c["id"] for c in report["candidates"]}
        for cid in request["candidate_ids"]:
            if cid not in known:
                findings.append(warning("unknown_candidate", cid))
            if eligible(cid, task) == "fail":
                findings.append(warning("candidate_not_allowed", cid, "violation"))
            for row in report["assessments"]:
                if row["candidate_id"] == cid and row["status"] != "pass":
                    findings.append(warning("constraint_" + row["status"], row["constraint_id"],
                                            "violation" if row["status"] == "fail" else "missing_information"))
        if report["unresolved_usage_commitments"]:
            findings.append(warning("unresolved_work", "Reconcile pending/unknown attempts before repeating work; continuation remains your decision."))
        return {"request": request, "warnings": findings, "can_continue": True,
                "policy": "warn_and_record", "timing": "explicit_check", "submitted": False,
                "advice": "Resolve warnings where possible; record your next action and rationale."}

    def campaign_for_session(self, session_id):
        with self._db() as db:
            row = db.execute("SELECT campaign FROM bindings WHERE session=?", (session_id,)).fetchone()
            return row[0] if row else None

    def dispatch(self, operation, campaign_id=None, payload=None):
        validate(campaign_id, S, "campaign_id")
        payload = {} if payload is None else payload
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        with self._db() as db:
            if operation == "create":
                validate(payload, obj({"task": SCHEMAS["task"]}, ("task",)))
                task = payload["task"]
                validate_task(task)
                old = db.execute("SELECT task FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
                if old and old["task"] != canonical(task):
                    raise ValueError("campaign already exists with a different immutable task")
                if not old:
                    db.execute("INSERT INTO campaigns VALUES(?,?,?)", (campaign_id, canonical(task), self._now()))
                    for kind, field in (("candidate", "starting_candidates"), ("observation", "initial_observations")):
                        for record in task.get(field, []):
                            if kind == "observation" and record["candidate_id"] not in {c["id"] for c in task.get("starting_candidates", [])}:
                                raise ValueError("initial observation references unknown candidate")
                            self._append(db, campaign_id, kind, record["id"], record)
                return self._report(db, campaign_id, task)
            row = db.execute("SELECT task FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
            if not row:
                raise KeyError("unknown campaign")
            task = json.loads(row["task"])
            if operation in ("status", "report"):
                if payload:
                    raise ValueError("status/report payload must be empty")
                return self._report(db, campaign_id, task)
            if operation in ("attach", "detach"):
                validate(payload, obj({"session_id": S}, ("session_id",)))
                session = payload["session_id"]
                binding = db.execute("SELECT campaign FROM bindings WHERE session=?", (session,)).fetchone()
                if binding and binding[0] != campaign_id:
                    raise ValueError("session belongs to another campaign; detach explicitly from that campaign first")
                if operation == "attach":
                    db.execute("INSERT OR IGNORE INTO bindings VALUES(?,?)", (session, campaign_id))
                else:
                    db.execute("DELETE FROM bindings WHERE session=? AND campaign=?", (session, campaign_id))
                return {"campaign_id": campaign_id, "session_id": session, "attached": operation == "attach"}
            if operation not in SCHEMAS or operation == "task":
                raise ValueError("unknown operation")
            validate(payload, SCHEMAS[operation])
            old = db.execute("SELECT data FROM events WHERE campaign=? AND kind=? AND id=?", (campaign_id, operation, payload["id"])).fetchone()
            if old:
                existing = json.loads(old["data"])
                original = existing["request"] if operation in ("check", "freeze") else existing
                if canonical(original) != canonical(payload):
                    raise ValueError(f"conflicting {operation} ID: {payload['id']}")
                return existing if operation in ("check", "freeze") else {"recorded": False, "idempotent": True, "record": existing}
            report = self._report(db, campaign_id, task)
            known = {c["id"] for c in report["candidates"]}
            if operation == "candidate" and payload.get("parent_id") not in known | {None}:
                raise ValueError("unknown parent candidate")
            if operation == "observation":
                if payload["candidate_id"] not in known:
                    raise ValueError("unknown candidate; register identity first")
                if payload.get("action_id") and payload["action_id"] not in {a["id"] for a in report["actions"]}:
                    raise ValueError("unknown action reference")
                if payload.get("action_id"):
                    action = next(a for a in report["actions"] if a["id"] == payload["action_id"])
                    if payload["candidate_id"] not in action["candidate_ids"]:
                        raise ValueError("observation candidate differs from linked action")
            if operation == "usage":
                if (payload["category"] == "unknown") != (payload["amount"] is None):
                    raise ValueError("unknown usage requires null amount; other categories require a finite amount")
            if operation == "decision":
                evidence_ids = {o["id"] for o in report["observations"]}
                if not set(payload["evidence_ids"]) <= evidence_ids:
                    raise ValueError("decision cites unknown observations")
                if payload["outcome"] != "inconclusive" and not payload["evidence_ids"]:
                    raise ValueError("supported/contradicted decision requires evidence")
            if operation == "action":
                previous = [a for a in report["actions"] if a["attempt_id"] == payload["attempt_id"]]
                if previous:
                    last = previous[-1]
                    for key in ("job", "candidate_ids", "check_id", "job_id"):
                        if key in last and payload.get(key) != last[key]:
                            raise ValueError(f"attempt identity changed: {key}")
                    if last["status"] in ("completed", "failed"):
                        raise ValueError("terminal attempt cannot be reopened; record a new attempt")
                    if last["status"] == "running" and payload["status"] == "accepted":
                        raise ValueError("running attempt cannot return to accepted")
            record = payload
            if operation == "check":
                record = self._check(report, payload)
            if operation == "freeze":
                if not payload["candidate_ids"] or not set(payload["candidate_ids"]) <= known:
                    raise ValueError("freeze requires known selected candidates")
                snapshot = {k: v for k, v in report.items() if k not in ("events", "freezes", "sessions")}
                snapshot["submission"] = payload
                snapshot["frozen_at"] = self._now()
                record = {"request": payload, "snapshot": snapshot, "digest": digest(snapshot)}
            self._append(db, campaign_id, operation, payload["id"], record)
            if operation in ("check", "freeze"):
                return record
            return {"recorded": True, "idempotent": False, "record": record,
                    "warnings": self._report(db, campaign_id, task)["warnings"]}
