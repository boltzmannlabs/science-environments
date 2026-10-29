"""Registration/installation checks; scientific services are never invoked."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from leadopt_env.plugin import register


class Context:
    def __init__(self, db_path=None):
        self.tools, self.skills, self.prompt_sections = {}, {}, {}
        self.db_path = db_path

    def register_tool(self, **values):
        self.tools[values["name"]] = values

    def register_skill(self, name, path, **_kwargs):
        self.skills[name] = Path(path)

    def register_system_prompt_section(self, name, text, **_kwargs):
        self.prompt_sections[name] = text

    def get_config(self, name, default=None):
        return self.db_path if name == "db_path" else default


class PluginTests(unittest.TestCase):
    def test_registration_has_no_state_or_execution_side_effect(self):
        ctx = Context()
        register(ctx)
        self.assertIn("leadopt_campaign", ctx.tools)
        self.assertTrue(ctx.skills["lead-optimization"].is_file())
        self.assertIn("warning-only", ctx.prompt_sections["leadopt.environment"])

    def test_describe_works_without_configured_database(self):
        ctx = Context()
        register(ctx)
        result = json.loads(ctx.tools["leadopt_campaign"]["handler"]({"operation": "describe"}))
        self.assertIn("task", result["record_schemas"])
        self.assertIn("candidate", result["record_schemas"])

    def test_installer_preserves_existing_destination(self):
        spec = importlib.util.spec_from_file_location("leadopt_installer", ROOT / "scripts/install_plugin.py")
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory() as scratch:
            destination = Path(scratch) / "leadopt_env"
            installer.install(destination)
            skill = destination / "skills/lead-optimization/SKILL.md"
            self.assertTrue(skill.is_file())
            marker = destination / "existing-user-file"
            marker.write_text("preserve")
            with self.assertRaises(FileExistsError):
                installer.install(destination)
            self.assertEqual(marker.read_text(), "preserve")

    def test_session_attachment_uses_host_or_explicit_child_identity(self):
        with tempfile.TemporaryDirectory() as scratch:
            ctx = Context(str(Path(scratch) / "campaign.sqlite"))
            register(ctx)
            handle = ctx.tools["leadopt_campaign"]["handler"]
            def call(operation, payload=None, session_id=None):
                return json.loads(handle({"operation": operation, "campaign_id": "test",
                                          "payload": payload or {}}, session_id=session_id))
            call("create", {"task": {"schema_version": 1, "id": "test", "version": "1"}})
            attached = call("attach", session_id="actual-host-session")
            self.assertEqual(attached["session_id"], "actual-host-session")
            child = call("attach", {"session_id": "explicit-child"}, session_id="actual-host-session")
            self.assertEqual(child["session_id"], "explicit-child")
            self.assertEqual(set(call("status")["sessions"]), {"actual-host-session", "explicit-child"})
            self.assertIn("error", call("attach"))

    def test_bound_host_session_cannot_silently_mutate_another_campaign(self):
        with tempfile.TemporaryDirectory() as scratch:
            ctx = Context(str(Path(scratch) / "campaign.sqlite"))
            register(ctx)
            handle = ctx.tools["leadopt_campaign"]["handler"]
            def call(campaign, operation, payload=None):
                return json.loads(handle({"operation": operation, "campaign_id": campaign,
                                          "payload": payload or {}}, session_id="actual-session"))
            for cid in ("a", "b"):
                self.assertNotIn("error", call(cid, "create", {"task": {
                    "schema_version": 1, "id": cid, "version": "1"}}))
            call("a", "attach")
            candidate = {"id": "compound", "representation": "CCO", "form_id": "as-supplied",
                         "source": "synthetic fixture"}
            result = call("b", "candidate", candidate)
            self.assertEqual(result["error_type"], "session_campaign_mismatch")
            self.assertEqual(result["host_session_id"], "actual-session")
            self.assertEqual(call("b", "status")["candidates"], [])
            self.assertNotIn("error", call("a", "candidate", candidate))
            call("a", "detach")
            call("b", "attach")
            self.assertNotIn("error", call("b", "candidate", candidate))

    def test_storage_failure_is_explicit_and_preserves_host_identity(self):
        with tempfile.TemporaryDirectory() as scratch:
            database = Path(scratch) / "not-a-database"
            database.write_text("This is intentionally corrupt fixture data")
            ctx = Context(str(database))
            register(ctx)
            handle = ctx.tools["leadopt_campaign"]["handler"]
            result = json.loads(handle({"operation": "status", "campaign_id": "a"},
                                       session_id="actual-session"))
            self.assertEqual(result["error_type"], "storage_error")
            self.assertEqual(result["host_session_id"], "actual-session")
            self.assertIn("no operation was retried", result["error"])
            self.assertEqual(database.read_text(), "This is intentionally corrupt fixture data")


if __name__ == "__main__":
    unittest.main()
