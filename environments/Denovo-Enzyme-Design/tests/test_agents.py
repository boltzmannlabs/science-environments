"""Real local subprocess tests for the harness transport; no model calls."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest


ENVIRONMENT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("denovo_agents", ENVIRONMENT / "runtime/agents.py")
agents = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agents)


class HarnessBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def config(self, source):
        script = self.root / "harness_fixture.py"
        script.write_text(source, encoding="utf-8")
        return {"backend": "command", "argv": [sys.executable, str(script),
                "{task_file}", "{response_file}", "{role}"]}

    def test_real_subprocess_preserves_task_and_separates_reviewer(self):
        config = self.config("""import json,sys
from pathlib import Path
task=json.loads(Path(sys.argv[1]).read_text())
target=Path(sys.argv[2])
temp=target.with_suffix('.tmp')
temp.write_text(json.dumps({'role':sys.argv[3],'task':task}))
temp.replace(target)
print('Narration is not the scientific response')
""")
        task = {"request": "literal $(touch SHOULD_NOT_EXIST) `echo secret`\nquotes: \"'",
                "run_id": "fixture", "response_contract": {"kind": "transport_fixture"}}
        worker = agents.invoke(config, "executor", task, self.root / "worker", 5)
        reviewer = agents.invoke(config, "reviewer", task, self.root / "reviewer", 5)
        for role, result in [("executor", worker), ("reviewer", reviewer)]:
            self.assertIsNone(result["error"], result)
            self.assertEqual(result["exit_code"], 0)
            actual_task = result['response']['task'].copy()
            window = actual_task.pop('_execution_window')
            self.assertEqual(result['response']['role'], role)
            self.assertEqual(actual_task, task)
            self.assertEqual(window, result['execution_window'])
            self.assertEqual(window['timeout_seconds'], 5)
            self.assertLess(window['response_due_utc'], window['deadline_utc'])
            self.assertGreater(window['response_reserve_seconds'], 0)
            self.assertIsNone(window['max_turns'])
            self.assertGreaterEqual(result["cpu_seconds"], 0)
            self.assertIn("Narration", Path(result["stdout_path"]).read_text())
        self.assertIn("Independently inspect", Path(reviewer["prompt_path"]).read_text())
        self.assertNotEqual(worker["response_path"], reviewer["response_path"])
        self.assertFalse((self.root / "worker/SHOULD_NOT_EXIST").exists())
        stale = agents.invoke(config, "executor", {}, self.root / "worker", 5)
        self.assertIn("stale", stale["error"])
        saved_task = json.loads(Path(worker["response_path"]).read_text())["task"]
        saved_task.pop('_execution_window')
        self.assertEqual(saved_task, task)

    def test_failed_malformed_and_nonfinite_results_never_become_responses(self):
        for i, (payload, exit_code) in enumerate([
            ('{"ok":true}', 7), ('not-json', 0), ('[1,2]', 0),
            ('{"score":NaN}', 0), ('{"score":1e999}', 0),
            ('{"status":"PASS","status":"FAIL"}', 0),
        ]):
            with self.subTest(payload=payload, exit_code=exit_code):
                config = self.config(
                    "import sys\nfrom pathlib import Path\n"
                    f"Path(sys.argv[2]).write_text({payload!r})\n"
                    f"sys.exit({exit_code})\n")
                result = agents.invoke(config, "executor", {}, self.root / f"bad{i}", 5)
                self.assertIsNone(result["response"])
                self.assertIsNotNone(result["error"])

    @unittest.skipUnless(os.name == "posix", "POSIX process groups")
    def test_timeout_kills_child_group_and_does_not_accept_partial_output(self):
        config = self.config("""import json,subprocess,sys,time
from pathlib import Path
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])
Path(sys.argv[2]).with_suffix('.child').write_text(str(child.pid))
Path(sys.argv[2]).write_text(json.dumps({'status':'PASS'}))
time.sleep(60)
""")
        result = agents.invoke(config, "repair", {}, self.root / "timeout", 2)
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["response"])
        self.assertLess(result["elapsed_seconds"], 5)
        child = int(Path(result["response_path"]).with_suffix(".child").read_text())
        # The orphan can briefly remain a zombie while PID 1 reaps it. A zombie
        # has stopped executing and is not a surviving scientific process.
        status = Path(f"/proc/{child}/stat")
        for _ in range(40):
            if not status.exists() or status.read_text().split(") ", 1)[1][0] == "Z":
                break
            time.sleep(0.05)
        else:
            os.kill(child, signal.SIGKILL)
            self.fail("Descendant still executing after invocation timeout")

    def test_sci_command_is_finite_and_does_not_resume_or_bypass_approvals(self):
        argv = agents.build_argv({"backend": "sci", "profile": "test-profile",
                                  "max_turns": 12}, "reviewer", Path("task.json"),
                                 Path("response.json"), Path("prompt.txt"), 90)
        self.assertEqual(argv[:4], ["sci", "--profile", "test-profile", "chat"])
        self.assertIn("--oneshot", argv)
        self.assertIn("--query-file", argv)
        self.assertEqual(argv[argv.index("--max-turns") + 1], "12")
        self.assertEqual(argv[argv.index("--run-budget") + 1], "90")
        for option in ["--resume", "--continue", "--yolo", "--accept-hooks"]:
            self.assertNotIn(option, argv)


if __name__ == "__main__":
    unittest.main()
