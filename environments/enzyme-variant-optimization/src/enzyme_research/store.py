"""Transactional research state and append-only hash-chained events."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import uuid

from .contracts import ResearchError, canonical, digest, identifier, safe_data, task_contract, candidate_record, candidate_library, observation_record, ARMS


class Store:
    def __init__(self, root):
        self.root = Path(root).absolute()
        if self.root.is_symlink() or self.root.resolve() != self.root:
            raise ResearchError("Research state cannot use symbolic path aliases")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = self.root / "research.sqlite"
        if self.db.is_symlink():
            raise ResearchError("State database cannot be a symbolic link")
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS campaigns(id TEXT PRIMARY KEY, task TEXT NOT NULL, arm TEXT NOT NULL, status TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS candidates(campaign TEXT NOT NULL, id TEXT NOT NULL, value TEXT NOT NULL, UNIQUE(campaign,id));
                CREATE TABLE IF NOT EXISTS observations(campaign TEXT NOT NULL,id TEXT NOT NULL,value TEXT NOT NULL, UNIQUE(campaign,id));
                CREATE TABLE IF NOT EXISTS decisions(campaign TEXT NOT NULL,round INTEGER NOT NULL,value TEXT NOT NULL,status TEXT NOT NULL, UNIQUE(campaign,round));
                CREATE TABLE IF NOT EXISTS calls(campaign TEXT NOT NULL,id TEXT NOT NULL,tool TEXT NOT NULL,args TEXT NOT NULL,status TEXT NOT NULL,result TEXT, UNIQUE(campaign,id));
                CREATE TABLE IF NOT EXISTS call_keys(campaign TEXT NOT NULL,operation_key TEXT NOT NULL,call_id TEXT NOT NULL,args_sha256 TEXT NOT NULL, UNIQUE(campaign,operation_key));
                CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,campaign TEXT NOT NULL,payload TEXT NOT NULL,previous TEXT NOT NULL,sha256 TEXT NOT NULL);
            ''')
        os.chmod(self.db, 0o600)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.db, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @contextmanager
    def transaction(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            yield db

    def event(self, db, campaign, name, payload):
        safe_data(payload)
        value = {"event": name, "time": datetime.now(timezone.utc).isoformat(), "data": payload}
        last = db.execute("SELECT sha256 FROM events WHERE campaign=? ORDER BY seq DESC LIMIT 1", (campaign,)).fetchone()
        previous = last[0] if last else "0" * 64
        sha = digest({"previous": previous, "payload": value})
        db.execute("INSERT INTO events(campaign,payload,previous,sha256) VALUES(?,?,?,?)", (campaign, canonical(value), previous, sha))

    def start(self, task, arm):
        task = task_contract(task)
        if arm not in ARMS:
            raise ResearchError("Research arm must be fixed, base or specialist")
        source = Path(task["parent"]["structure"]["path"])
        if source.is_symlink() or not source.is_file() or not 0 < source.stat().st_size <= 10 * 1024**2:
            raise ResearchError("Parent structure must be a bounded existing regular file")
        if hashlib.sha256(source.read_bytes()).hexdigest() != task["parent"]["structure"]["sha256"]:
            raise ResearchError("Parent structure does not match the task freeze")
        campaign = "research-" + uuid.uuid4().hex[:16]
        parent = task["parent"]
        record = {"candidate_id": parent["candidate_id"], "parent_id": None,
                  "sequence": parent["sequence"], "sequence_sha256": hashlib.sha256(parent["sequence"].encode()).hexdigest(),
                  "mutations_from_reference": [], "structure_status": "supplied_requires_validation", "status": "reference"}
        if task["evidence_track"] == "protected_measured_library":
            record.update(library_id=task["candidate_library"]["library_id"],
                          library_member_id=candidate_library(task)[parent["sequence"]],
                          library_members_sha256=task["candidate_library"]["members_sha256"])
        with self.transaction() as db:
            db.execute("INSERT INTO campaigns VALUES(?,?,?,?)", (campaign, canonical(task), arm, "running"))
            db.execute("INSERT INTO candidates VALUES(?,?,?)", (campaign, parent["candidate_id"], canonical(record)))
            self.event(db, campaign, "campaign_started", {"task_sha256": digest(task), "arm": arm})
        return campaign

    def status(self, campaign):
        identifier(campaign, "campaign_id")
        with self.connection() as db:
            row = db.execute("SELECT * FROM campaigns WHERE id=?", (campaign,)).fetchone()
            if row is None:
                raise ResearchError("Unknown campaign")
            result = {"campaign_id": campaign, "task": json.loads(row["task"]), "arm": row["arm"], "status": row["status"]}
            for table in ("candidates", "observations"):
                result[table] = [json.loads(r["value"]) for r in db.execute(f"SELECT value FROM {table} WHERE campaign=? ORDER BY rowid", (campaign,))]
            result["decisions"] = [{"round": r["round"], "status": r["status"], "value": json.loads(r["value"])} for r in db.execute("SELECT * FROM decisions WHERE campaign=? ORDER BY round", (campaign,))]
            result["calls"] = [{"call_id": r["id"], "tool": r["tool"], "status": r["status"], "args": json.loads(r["args"]), "result": json.loads(r["result"]) if r["result"] else None} for r in db.execute("SELECT * FROM calls WHERE campaign=? ORDER BY rowid", (campaign,))]
            result["events"] = [{"seq": r["seq"], "payload": json.loads(r["payload"]), "previous": r["previous"], "sha256": r["sha256"]} for r in db.execute("SELECT * FROM events WHERE campaign=? ORDER BY seq", (campaign,))]
        previous = "0" * 64
        for event in result["events"]:
            if event["previous"] != previous or digest({"previous": previous, "payload": event["payload"]}) != event["sha256"]:
                raise ResearchError("Research event chain is corrupt")
            previous = event["sha256"]
        result["structures"] = [event["payload"]["data"] for event in result["events"]
                                if event["payload"]["event"] == "structure_version_registered"]
        result["structure_assessments"] = [
            {"structure_id": sid, "candidate_id": cid, "kind": observation["kind"],
             "outcome": observation["coordinate_scope"]["outcomes"][sid],
             "execution_mode": observation["coordinate_scope"]["execution_mode"],
             "observation_id": observation["observation_id"], "source_call_id": observation["source_call_id"]}
            for observation in result["observations"] if "coordinate_scope" in observation
            for sid, cid in observation["coordinate_scope"]["structure_candidates"].items()]
        return result

    def add_structure_version(self, campaign, value):
        """Append a verified coordinate version without creating a new sequence.

        The structure adapter supplies parser-derived metadata and an exact
        source receipt. This store operation is not exposed to the agent.
        """
        safe_data(value)
        identifier(value.get("structure_id"), "structure_id")
        state = self.status(campaign)
        candidate = next((c for c in state["candidates"] if c["candidate_id"] == value.get("candidate_id")), None)
        if candidate is None or value.get("sequence_sha256") != candidate["sequence_sha256"]:
            raise ResearchError("Coordinate version must match an existing exact candidate sequence")
        source = value.get("source", {})
        call = next((c for c in state["calls"] if c["call_id"] == source.get("source_call_id")), None)
        if call is None or call["tool"] != "boltzmann_submit" or call["status"] != "completed":
            raise ResearchError("Coordinate version requires a completed original scientific submission")
        with self.transaction() as db:
            previous = [json.loads(r[0])["data"] for r in db.execute("SELECT payload FROM events WHERE campaign=?", (campaign,))
                        if json.loads(r[0]).get("event") == "structure_version_registered"]
            existing = next((v for v in previous if v["structure_id"] == value["structure_id"]), None)
            if existing is not None:
                if existing != value:
                    raise ResearchError("An immutable coordinate version cannot be changed")
                return existing
            row = db.execute("SELECT value FROM candidates WHERE campaign=? AND id=?", (campaign, value["candidate_id"])).fetchone()
            current = json.loads(row[0])
            if current["sequence_sha256"] != value["sequence_sha256"]:
                raise ResearchError("Candidate sequence changed before coordinate registration")
            current["structure_status"] = "available_requires_quality_validation"
            db.execute("UPDATE candidates SET value=? WHERE campaign=? AND id=?", (canonical(current), campaign, value["candidate_id"]))
            self.event(db, campaign, "structure_version_registered", value)
        return value

    def add_candidates(self, campaign, values, *, provenance=None):
        state = self.status(campaign)
        if provenance is not None:
            safe_data(provenance)
        records = [candidate_record(state["task"], value) for value in values]
        known = {c["candidate_id"]: c for c in state["candidates"]}
        if not records:
            raise ResearchError("Empty candidate batches are rejected")
        sequences = {c["sequence"] for c in known.values()}
        ids = set(known)
        for record in records:
            if record["parent_id"] not in known:
                raise ResearchError("Candidate parent is unknown")
            if record["candidate_id"] in ids or record["sequence"] in sequences:
                raise ResearchError("Duplicate candidate identity or sequence")
            ids.add(record["candidate_id"])
            sequences.add(record["sequence"])
        if len(ids) - 1 > state["task"]["budget"]["max_unique_candidates"]:
            raise ResearchError("Candidate budget exhausted")
        with self.transaction() as db:
            # Recheck identities and counts under the write lock: two agents
            # must not race past the task's candidate budget.
            current = [json.loads(r[0]) for r in db.execute("SELECT value FROM candidates WHERE campaign=?", (campaign,))]
            current_ids = {c["candidate_id"] for c in current}
            current_sequences = {c["sequence"] for c in current}
            if len(current) - 1 + len(records) > state["task"]["budget"]["max_unique_candidates"]:
                raise ResearchError("Candidate budget exhausted")
            for record in records:
                if record["candidate_id"] in current_ids or record["sequence"] in current_sequences:
                    raise ResearchError("Duplicate candidate identity or sequence")
            for record in records:
                db.execute("INSERT INTO candidates VALUES(?,?,?)", (campaign, record["candidate_id"], canonical(record)))
            self.event(db, campaign, "candidates_added", {"candidate_ids": [r["candidate_id"] for r in records]})
            if provenance is not None:
                self.event(db, campaign, "sequence_output_imported", provenance)
        return records

    def add_observation(self, campaign, value):
        value = observation_record(value)
        state = self.status(campaign)
        known = {c["candidate_id"] for c in state["candidates"]}
        if set(value["candidate_ids"]) - known:
            raise ResearchError("Observation refers to unknown candidates")
        if state["task"]["evidence_track"] != "synthetic" and value["evidence_level"] == "synthetic_fixture":
            raise ResearchError("Synthetic results cannot enter a live campaign")
        call = next((c for c in state["calls"] if c["call_id"] == value["source_call_id"]), None)
        if call is None or call["status"] != "completed":
            raise ResearchError("An observation requires a completed tracked source call")
        if "coordinate_scope" in value:
            versions = {record["structure_id"]: record["candidate_id"] for record in state["structures"]}
            versions["supplied-" + state["task"]["parent"]["structure"]["sha256"][:20]] = state["task"]["parent"]["candidate_id"]
            if any(versions.get(sid) != cid for sid, cid in value["coordinate_scope"]["structure_candidates"].items()):
                raise ResearchError("Structural measurements refer to an unknown or different candidate's coordinate version")
        for artifact in value["artifacts"]:
            path = Path(artifact["path"])
            if path.is_symlink() or not path.is_file() or path.stat().st_size == 0 or hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
                raise ResearchError("Observation artifact is missing, empty or changed")
        with self.transaction() as db:
            existing = db.execute("SELECT value FROM observations WHERE campaign=? AND id=?", (campaign, value["observation_id"])).fetchone()
            if existing is not None:
                if json.loads(existing[0]) != value:
                    raise ResearchError("An immutable scientific observation cannot be overwritten")
                return value
            db.execute("INSERT INTO observations VALUES(?,?,?)", (campaign, value["observation_id"], canonical(value)))
            self.event(db, campaign, "observation_added", {"observation_id": value["observation_id"], "sha256": digest(value)})
        return value

    def prepare_call(self, campaign, tool, args):
        return self.reserve_call(campaign, tool, args)[0]

    def reserve_call(self, campaign, tool, args, *, operation_key=None):
        """Reserve once under the write lock; a restart never repeats a send.

        An existing prepared/sending reservation also counts as an unresolved
        operation. Only an operator reconciliation may establish its outcome.
        """
        safe_data(args)
        if operation_key is not None:
            identifier(operation_key, "operation_key")
        state = self.status(campaign)
        allowed = {"boltzmann_upload", "boltzmann_submit", "boltzmann_status", "boltzmann_download", "boltzmann_fetch_tool_log", "synthetic_observation"}
        if tool not in allowed or (tool == "synthetic_observation" and state["task"]["evidence_track"] != "synthetic"):
            raise ResearchError("Unapproved external operation")
        if tool in {"boltzmann_submit", "boltzmann_upload"} and args.get("job_name") not in state["task"]["allowed_jobs"]:
            raise ResearchError("Scientific job is outside this task's allowed tools")
        with self.transaction() as db:
            if operation_key is not None:
                existing = db.execute("SELECT * FROM call_keys WHERE campaign=? AND operation_key=?", (campaign, operation_key)).fetchone()
                if existing is not None:
                    if existing["args_sha256"] != digest({"tool": tool, "args": args}):
                        raise ResearchError("An operation key cannot be reused with different arguments")
                    return existing["call_id"], False
            if tool == "boltzmann_submit":
                rows = db.execute("SELECT status FROM calls WHERE campaign=? AND tool='boltzmann_submit'", (campaign,)).fetchall()
                if len(rows) >= state["task"]["budget"]["max_scientific_submissions"]:
                    raise ResearchError("Scientific submission budget exhausted")
                if sum(r[0] not in {"completed", "definite_failure"} for r in rows) >= state["task"]["budget"]["max_outstanding_jobs"]:
                    raise ResearchError("Existing submission must be reconciled or completed before another job")
            call_id = "call-" + uuid.uuid4().hex[:16]
            db.execute("INSERT INTO calls VALUES(?,?,?,?,?,?)", (campaign, call_id, tool, canonical(args), "prepared", None))
            if operation_key is not None:
                db.execute("INSERT INTO call_keys VALUES(?,?,?,?)", (campaign, operation_key, call_id, digest({"tool": tool, "args": args})))
            self.event(db, campaign, "call_prepared", {"call_id": call_id, "tool": tool, "args_sha256": digest(args)})
        return call_id, True

    def call_transition(self, campaign, call_id, target, result=None):
        safe_data(result)
        transitions = {"prepared": {"sending"}, "sending": {"completed", "accepted", "submit_unknown", "definite_failure", "operation_unknown"},
                       "accepted": {"completed", "definite_failure"}, "submit_unknown": {"accepted"}, "operation_unknown": set(),
                       "completed": set(), "definite_failure": set()}
        with self.transaction() as db:
            row = db.execute("SELECT * FROM calls WHERE campaign=? AND id=?", (campaign, call_id)).fetchone()
            if row is None or target not in transitions.get(row["status"], set()):
                raise ResearchError("Invalid or repeated call transition; reconcile the original operation")
            if target == "accepted" and (not isinstance(result, dict) or not isinstance(result.get("doc_id"), str) or not result["doc_id"]):
                raise ResearchError("Accepted submissions require the actual document ID")
            db.execute("UPDATE calls SET status=?,result=? WHERE campaign=? AND id=?", (target, canonical(result), campaign, call_id))
            self.event(db, campaign, "call_" + target, {"call_id": call_id, "result": result})

    def save_decision(self, campaign, value):
        safe_data(value)
        state = self.status(campaign)
        round_number = len(state["decisions"]) + 1
        if round_number > state["task"]["budget"]["max_rounds"]:
            raise ResearchError("Research round budget exhausted")
        if state["decisions"] and state["decisions"][-1]["status"] != "observed":
            raise ResearchError("Previous decision requires execution and observations before revision")
        with self.transaction() as db:
            db.execute("INSERT INTO decisions VALUES(?,?,?,?)", (campaign, round_number, canonical(value), "planned"))
            self.event(db, campaign, "decision_saved", {"round": round_number, "sha256": digest(value)})
        return round_number

    def decision_observed(self, campaign, round_number, observation_ids):
        state = self.status(campaign)
        known = {o["observation_id"]: o for o in state["observations"]}
        if (type(round_number) is not int or not isinstance(observation_ids, list) or not observation_ids
                or any(not isinstance(oid, str) for oid in observation_ids)
                or len(set(observation_ids)) != len(observation_ids) or set(observation_ids) - set(known)):
            raise ResearchError("A completed decision needs actual known observations")
        decision = next((d for d in state["decisions"] if d["round"] == round_number and d["status"] == "planned"), None)
        if decision is None:
            raise ResearchError("Decision is missing or already observed")
        saved = next(e["seq"] for e in state["events"] if e["payload"]["event"] == "decision_saved"
                     and e["payload"]["data"]["round"] == round_number)
        added = {e["payload"]["data"]["observation_id"]: e["seq"] for e in state["events"]
                 if e["payload"]["event"] == "observation_added"}
        prepared = {e["payload"]["data"]["call_id"]: e["seq"] for e in state["events"]
                    if e["payload"]["event"] == "call_prepared"}
        if any(added.get(oid, -1) <= saved for oid in observation_ids):
            raise ResearchError("Decision feedback must include new observations from this investigation, not prior results")
        chosen = decision["value"]["action"]
        calls = {c["call_id"]: c for c in state["calls"]}
        matching = []
        for oid in observation_ids:
            source = calls[known[oid]["source_call_id"]]
            if (source["status"] == "completed" and prepared.get(source["call_id"], -1) > saved
                    and source["tool"] in {"boltzmann_submit", "synthetic_observation"}
                    and source["args"].get("job_name") == chosen["job_name"]
                    and source["args"].get("experiment_data") == chosen["experiment_data"]):
                matching.append(oid)
        if not matching:
            raise ResearchError("Decision feedback needs the completed selected scientific action, not an unrelated job")
        with self.transaction() as db:
            row = db.execute("SELECT status FROM decisions WHERE campaign=? AND round=?", (campaign, round_number)).fetchone()
            if row is None or row[0] != "planned":
                raise ResearchError("Decision is missing or already observed")
            db.execute("UPDATE decisions SET status='observed' WHERE campaign=? AND round=?", (campaign, round_number))
            self.event(db, campaign, "decision_observed", {"round": round_number, "observation_ids": observation_ids,
                                                          "selected_action_observation_ids": matching})
