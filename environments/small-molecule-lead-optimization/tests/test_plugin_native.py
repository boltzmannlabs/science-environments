"""Opt-in real Agent-Scientist loader/registry test in an isolated temporary home."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOST_SOURCE = os.environ.get("LEADOPT_AGENT_SOURCE")
HOST_PYTHON = os.environ.get("LEADOPT_AGENT_PYTHON")


@unittest.skipUnless(HOST_SOURCE and HOST_PYTHON, "set LEADOPT_AGENT_SOURCE and LEADOPT_AGENT_PYTHON for native integration")
class NativePluginTests(unittest.TestCase):
    def test_installed_directory_discovery_skill_and_real_dispatch(self):
        with tempfile.TemporaryDirectory(prefix="leadopt-native-") as scratch:
            home = Path(scratch) / "host"
            home.mkdir()
            db = Path(scratch) / "campaigns.sqlite"
            destination = home / "plugins/leadopt_env"
            install = subprocess.run(
                [HOST_PYTHON, str(ROOT / "scripts/install_plugin.py"), "--destination", str(destination)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            config = {
                "plugins": {"enabled": ["leadopt_env"], "entries": {
                    "leadopt_env": {"settings": {"db_path": str(db)}}}},
            }
            (home / "config.yaml").write_text(json.dumps(config))
            environment = dict(os.environ)
            environment.update({
                "SCI_HOME": str(home), "SCI_RUNTIME_DIR": str(home / "runtime"),
                "PYTHONPATH": str(Path(HOST_SOURCE).resolve()), "PYTHONDONTWRITEBYTECODE": "1",
            })
            probe = r'''
import json
import os
from pathlib import Path
from sci_cli.plugins import PluginManager
from tools.registry import registry

home = Path(os.environ["SCI_HOME"])
manager = PluginManager(scope_key=str(home))
manager.discover_and_load()
plugin = next(p for p in manager.list_plugins() if p["name"] == "leadopt_env")
assert plugin["enabled"] and not plugin["error"], plugin
skill = manager.find_plugin_skill("leadopt_env:lead-optimization")
assert skill and skill.is_relative_to(home / "plugins/leadopt_env") and skill.is_file()
assert registry.get_entry("leadopt_campaign", scope=manager.scope_key)
# This is real installed-handler dispatch. An unknown campaign must be an
# explicit local error, never a scientific submission or fabricated status.
result = json.loads(registry.dispatch("leadopt_campaign", {
    "operation": "status", "campaign_id": "missing-native-campaign"
}, scope=manager.scope_key, session_id="native-session"))
assert "error" in result, result
assert result["scientific_jobs_submitted"] == 0, result
assert result["host_session_id"] == "native-session", result
def call(operation, payload=None):
    result = json.loads(registry.dispatch("leadopt_campaign", {
        "operation": operation, "campaign_id": "native-campaign", "payload": payload or {}
    }, scope=manager.scope_key, session_id="native-session"))
    assert "error" not in result, result
    return result
# Missing scientific task information is advisory. This minimal local task
# exercises persisted core records through the actual installed tool handler.
call("create", {"task": {"schema_version": 1, "id": "native-fixture", "version": "1"}})
call("attach")
check = call("check", {"id": "native-check", "job": "unconfigured-fixture-job",
                       "candidate_ids": [], "resource_requests": {}})
assert check["warnings"] and check["can_continue"] is True and check["submitted"] is False
action = call("action", {"id": "native-action", "attempt_id": "native-attempt",
                "job": "unconfigured-fixture-job", "candidate_ids": [], "status": "unknown",
                "check_id": "native-check", "source": "synthetic native fixture: no service submission",
                "rationale": "Exercise recorded continuation after advisory warnings only."})
assert action["recorded"] is True
call("usage", {"id": "native-usage", "unit": "internal_evaluations", "amount": None,
               "category": "unknown", "scope": "native-attempt",
               "source": "synthetic native fixture: no internal service visibility"})
status = call("status")
assert status["sessions"] == ["native-session"]
assert status["coverage"]["complete"] is False
assert status["usage"][0]["category"] == "unknown" and status["usage"][0]["amount"] is None
manager.unload()
assert registry.get_entry("leadopt_campaign", scope=manager.scope_key) is None
print(json.dumps({"native_loader": "passed", "installed_skill": "passed", "registry_dispatch": "passed"}))
'''
            run = subprocess.run([HOST_PYTHON, "-c", probe], cwd=scratch, env=environment,
                                 text=True, capture_output=True, check=False, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
            self.assertIn('"registry_dispatch": "passed"', run.stdout)


if __name__ == "__main__":
    unittest.main()
