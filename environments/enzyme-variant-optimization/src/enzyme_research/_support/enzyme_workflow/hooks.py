"""Native pre/post hooks observe calls without replacing connector handlers."""

import sqlite3
import threading

from . import connector
from .common import WorkflowError, canonical, scoped_root


class CallObserver:
    def __init__(self):
        self.receipts = {}
        self.lock = threading.Lock()

    def key(self, tool_name, args, tool_call_id, task_id):
        return (str(scoped_root()), tool_call_id or (threading.get_ident(), task_id),
                tool_name, canonical(args))

    def pre(self, tool_name="", args=None, tool_call_id=None, task_id=None, **kwargs):
        if tool_name != "boltzmann_submit":
            return
        try:
            receipt = connector.before(tool_name, args or {})
            if receipt:
                with self.lock:
                    self.receipts[self.key(tool_name, args, tool_call_id, task_id)] = receipt
        except (WorkflowError, OSError, ValueError, TypeError, sqlite3.Error) as exc:
            message = str(exc) if isinstance(exc, WorkflowError) else "Workflow tracking unavailable; submission blocked"
            return {"action": "block", "message": message}

    def post(self, tool_name="", args=None, result=None, tool_call_id=None, task_id=None,
             error_type=None, **kwargs):
        if tool_name not in {"boltzmann_submit", "boltzmann_status", "boltzmann_download"}:
            return
        receipt = None
        if tool_name == "boltzmann_submit":
            with self.lock:
                receipt = self.receipts.pop(self.key(tool_name, args, tool_call_id, task_id), None)
            if receipt is None:
                return
            if error_type == "plugin_block":
                # A different hook may veto after our reservation. Preserve an
                # uncertain state rather than guessing execution or replaying.
                result = {"error": "Submission blocked after workflow reservation"}
        connector.after(tool_name, args or {}, result, receipt)
