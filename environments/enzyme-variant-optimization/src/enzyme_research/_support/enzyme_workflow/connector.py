"""Observe existing connector calls; never create a separate HTTP path."""

import json

from .common import WorkflowError, canonical, scoped_root, digest, file_hash, validate_data
from .state import Store


def parse_result(result):
    if isinstance(result, dict):
        return result
    try:
        result = json.loads(result)
        return result if isinstance(result, dict) else {}
    except (ValueError, TypeError):
        return {}


def before(name, args, root=None):
    if name != "boltzmann_submit":
        return None
    root = root if root is not None else scoped_root()
    if not (root / "state.sqlite").is_file():
        return None
    store = Store(root)
    with store.connection() as db:
        row = db.execute("SELECT * FROM intents WHERE experiment_name=?", (args.get("experiment_name"),)).fetchone()
    if row is None:
        return None  # Existing ad-hoc connector calls retain their behavior.
    with store.transaction(row["workflow_id"]) as (db, spec, state):
        current = db.execute("SELECT * FROM intents WHERE id=?", (row["id"],)).fetchone()
        expected = json.loads(current["args"])
        actual = {k: args.get(k) for k in expected}
        if canonical(actual) != canonical(expected):
            raise WorkflowError("Tracked submission differs from approved prepared inputs")
        if current["status"] != "ready":
            raise WorkflowError("Duplicate tracked submission blocked. Poll/recover the original job; never replay a timeout.")
        db.execute("UPDATE intents SET status='submitting' WHERE id=?", (row["id"],))
        state["steps"][row["step_id"]]["status"] = "submitting"
        store.event(db, row["workflow_id"], "submit_started", {"step_id": row["step_id"], "intent_id": row["id"]})
    return {"workflow_id": row["workflow_id"], "step_id": row["step_id"], "intent_id": row["id"], "root": store.root}


def after(name, args, result, receipt=None, root=None):
    data = parse_result(result)
    if name == "boltzmann_submit" and receipt:
        store = Store(receipt["root"])
        with store.transaction(receipt["workflow_id"]) as (db, spec, state):
            step = state["steps"][receipt["step_id"]]
            if step.get("intent_id") != receipt["intent_id"]:
                return
            doc_id = data.get("doc_id")
            if isinstance(doc_id, str) and doc_id and not data.get("error"):
                validate_data(doc_id)
                if data.get("job_name", args["job_name"]) != args["job_name"]:
                    raise WorkflowError("Submission response returned a different backend job name; recover the original job")
                status = "submitted"
                step["doc_id"] = doc_id
            else:
                # Auth/connectivity errors are not proof that the remote job
                # was never accepted unless the connector says safe_to_retry.
                status = "failed" if data.get("safe_to_retry") is True else "submit_unknown"
                doc_id = None
            db.execute("UPDATE intents SET status=?,doc_id=? WHERE id=?", (status, doc_id, receipt["intent_id"]))
            step["status"] = status
            store.event(db, receipt["workflow_id"], "submit_result", {"step_id": receipt["step_id"], "status": status, "doc_id": doc_id})
    elif name == "boltzmann_status":
        root = root if root is not None else scoped_root()
        if not (root / "state.sqlite").is_file():
            return
        store = Store(root)
        with store.connection() as db:
            row = db.execute("SELECT * FROM intents WHERE job_name=? AND doc_id=?",
                             (args.get("job_name"), args.get("doc_id"))).fetchone()
        if row is None:
            return
        status = str(data.get("status", "")).strip().lower()
        translated = {"completed": "remote_completed", "success": "remote_completed", "100%completed": "remote_completed",
                      "failed": "failed", "error": "failed", "running": "running", "pending": "submitted"}.get(status)
        # Poll timeouts and auth errors never prove scientific failure.
        if translated is None or data.get("error"):
            return
        with store.transaction(row["workflow_id"]) as (db, spec, state):
            current = state["steps"][row["step_id"]]
            if current.get("intent_id") != row["id"]:
                return
            if current["status"] in {"complete", "failed"}:
                return
            if current["status"] == "remote_completed" and translated in {"running", "submitted"}:
                return
            current["status"] = translated
            if translated == "remote_completed":
                def links(value):
                    if isinstance(value, dict):
                        for key, item in value.items():
                            if key == "download_link" and isinstance(item, str):
                                yield item
                            else:
                                yield from links(item)
                    elif isinstance(value, list):
                        for item in value:
                            yield from links(item)
                for link in links(data):
                    db.execute("INSERT OR IGNORE INTO output_links(fingerprint,workflow_id,step_id,intent_id) VALUES(?,?,?,?)",
                               (digest(link), row["workflow_id"], row["step_id"], row["id"]))
            store.event(db, row["workflow_id"], "remote_status", {"step_id": row["step_id"], "status": translated})
    elif name == "boltzmann_download" and not data.get("errors") and not data.get("error"):
        root = root if root is not None else scoped_root()
        if not (root / "state.sqlite").is_file() or not isinstance(args.get("download_url"), str):
            return
        store = Store(root)
        with store.connection() as db:
            rows = db.execute("SELECT workflow_id,step_id,intent_id FROM output_links WHERE fingerprint=?", (digest(args["download_url"]),)).fetchall()
        for row in rows:
            with store.transaction(row["workflow_id"]) as (db, spec, state):
                if state["steps"][row["step_id"]].get("intent_id") != row["intent_id"]:
                    continue
                for path in data.get("output_paths", []):
                    from pathlib import Path
                    local = Path(path).expanduser()
                    if local.is_symlink() or not local.is_file() or not local.stat().st_size:
                        raise WorkflowError("Downloaded output is empty, missing or a symbolic link")
                    sha = file_hash(local)
                    db.execute("INSERT OR REPLACE INTO downloads(workflow_id,step_id,sha256,local_path,intent_id) VALUES(?,?,?,?,?)",
                               (row["workflow_id"], row["step_id"], sha, str(local.resolve()), row["intent_id"]))
                    state["steps"][row["step_id"]].setdefault("downloads", {})[sha] = str(local.resolve())
                    store.event(db, row["workflow_id"], "download_verified", {"step_id": row["step_id"], "sha256": sha})
