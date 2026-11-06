"""config/ and benchmark/ stay in sync with tasks/. Runnable standalone or pytest."""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import env_lib  # noqa: E402


def test_environment_json_matches_task_docs():
    env = env_lib.load_environment_json()
    assert env, "config/environment.json missing (run scripts/gen_config.py)"
    files = env_lib.task_files()
    assert [t["file"] for t in env["tasks"]] == files, "config task list != tasks/*.md"
    assert env["task_count"] == len(files)
    for fname in files:
        parsed = env_lib.parse_task(os.path.join(env_lib.tasks_dir(), fname))
        entry = next(t for t in env["tasks"] if t["file"] == fname)
        assert entry["doi"] == parsed["doi"], fname
        assert entry["pmc"] == parsed["pmc"], fname
        assert entry["pass_bar"] == parsed["pass_bar"], fname
        assert entry["expected_outputs"] == parsed["expected_outputs"], fname
        assert parsed["pass_bar"] and re.search(r"\d", parsed["pass_bar"]), fname
        if parsed["task_format"] == "capability_workflow":
            assert entry["grading_mode"] == "manual_review_required"
            assert entry["evaluator_file"] == parsed["evaluator_file"]
            assert entry["time_limit_minutes"] is None
            assert entry["budget_source"] == "execution_context"


def test_benchmark_json_matches_config():
    bench = env_lib.load_benchmark()
    env = env_lib.load_environment_json()
    assert bench, "benchmark/benchmark.json missing"
    assert [t["id"] for t in bench["tasks"]] == [t["id"] for t in env["tasks"]]


def test_papers_csv_rows():
    rows = env_lib.load_papers_csv()
    assert len(rows) == len(env_lib.task_files()), f"papers.csv has {len(rows)} rows"
    for row in rows:
        assert re.match(r"^10\.\d{4,9}/\S+$", "10." + row["doi"].split("doi.org/10.")[-1]) or \
               row["doi"].startswith("https://doi.org/10."), row["doi"]
        assert row["pmc"].startswith("PMC"), row["pmc"]
        assert row["pdbs"], row["task_id"]


def test_workflow_cannot_pass_legacy_single_score_grader():
    import json
    import tempfile
    for task in env_lib.load_environment_json()["tasks"]:
        if task.get("task_format") != "capability_workflow":
            continue
        with tempfile.TemporaryDirectory() as run_dir:
            for name in task["expected_outputs"]:
                with open(os.path.join(run_dir, name), "w", encoding="utf-8") as fh:
                    fh.write("placeholder\n")
            with open(os.path.join(run_dir, "metrics.json"), "w", encoding="utf-8") as fh:
                json.dump({"best_docking_score": -100}, fh)
            try:
                env_lib.grade_run(task["id"], run_dir, verbose=False)
            except SystemExit as exc:
                assert "scientific review required" in str(exc)
            else:
                raise AssertionError("File presence and a favourable score must not certify this workflow")


if __name__ == "__main__":
    for name in [n for n in dir() if n.startswith("test_")]:
        getattr(sys.modules[__name__], name)()
        print(f"ok: {name}")
