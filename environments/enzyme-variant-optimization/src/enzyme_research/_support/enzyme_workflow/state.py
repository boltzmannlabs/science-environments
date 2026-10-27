"""Transactional, profile-local state. A crashed submit stays ambiguous."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .common import WorkflowError, canonical, now, scoped_root


class Store:
    def __init__(self, root=None):
        self.root = Path(root) if root is not None else scoped_root()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.root / "state.sqlite"
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id TEXT PRIMARY KEY, spec TEXT NOT NULL, state TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY, workflow_id TEXT NOT NULL,
                    time TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS intents (
                    id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, step_id TEXT NOT NULL,
                    experiment_name TEXT UNIQUE NOT NULL, args TEXT NOT NULL,
                    status TEXT NOT NULL, doc_id TEXT, job_name TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS one_remote_job
                    ON intents(job_name, doc_id) WHERE doc_id IS NOT NULL;
                CREATE TABLE IF NOT EXISTS output_links (
                    fingerprint TEXT NOT NULL, workflow_id TEXT NOT NULL, step_id TEXT NOT NULL,
                    intent_id TEXT NOT NULL, PRIMARY KEY(fingerprint,workflow_id,step_id,intent_id));
                CREATE TABLE IF NOT EXISTS downloads (
                    workflow_id TEXT NOT NULL, step_id TEXT NOT NULL,
                    sha256 TEXT NOT NULL, local_path TEXT NOT NULL,
                    intent_id TEXT NOT NULL, PRIMARY KEY(intent_id,sha256));
            ''')
            for table in ("output_links", "downloads"):
                columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
                if "intent_id" not in columns:
                    # Pre-release observer records without an attempt identity
                    # are retained, but cannot authorize a later ingestion.
                    db.execute(f"ALTER TABLE {table} ADD COLUMN intent_id TEXT")
        os.chmod(self.path, 0o600)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def transaction(self, workflow_id):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT spec,state FROM workflows WHERE id=?", (workflow_id,)).fetchone()
            if row is None:
                raise WorkflowError("Unknown workflow in this profile")
            spec, state = json.loads(row["spec"]), json.loads(row["state"])
            yield db, spec, state
            db.execute("UPDATE workflows SET state=? WHERE id=?", (canonical(state), workflow_id))

    def event(self, db, workflow_id, kind, data):
        db.execute("INSERT INTO events(workflow_id,time,kind,data) VALUES(?,?,?,?)",
                   (workflow_id, now(), kind, canonical(data)))

    def read(self, workflow_id):
        with self.connection() as db:
            row = db.execute("SELECT spec,state FROM workflows WHERE id=?", (workflow_id,)).fetchone()
            if row is None:
                raise WorkflowError("Unknown workflow in this profile")
            events = [dict(row) for row in db.execute(
                "SELECT seq,time,kind,data FROM events WHERE workflow_id=? ORDER BY seq", (workflow_id,))]
            for event in events:
                event["data"] = json.loads(event["data"])
            return {"workflow_id": workflow_id, "spec": json.loads(row["spec"]),
                    "state": json.loads(row["state"]), "events": events}
