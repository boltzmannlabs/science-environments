"""Adapter contracts: bounded inference, truthful provenance, and tool-only platform access."""

import json
import sys
from pathlib import Path

import pytest

from synthesis_route_gym.adapters import (
    AiZynthFinderAdapter,
    LocalRetroAdapter,
    RegisteredPlatformAdapter,
)
from synthesis_route_gym.adapters.common import normalise_prediction, run_worker


def test_prediction_preserves_stereo_and_labels_prediction():
    prediction = normalise_prediction(
        {"reactants": ["C[C@H](O)C(=O)O"], "product": "CC(=O)C(=O)O", "score": 0.7},
        "test-model", "v1",
    )
    assert "@" in prediction["reactants"][0]
    assert prediction["evidence_status"] == "predicted"
    assert prediction["source"] == {"tool": "test-model", "version": "v1"}
    assert "feasible" not in prediction


@pytest.mark.parametrize("reactants,score", [([], 0.1), (["bad smiles"], 0.1), (["CCO"], float("nan"))])
def test_malformed_model_output_is_rejected(reactants, score):
    with pytest.raises(ValueError):
        normalise_prediction({"reactants": reactants, "product": "CC=O", "score": score}, "m", "1")


def test_localretro_unavailable_has_no_fake_predictions(tmp_path):
    result = LocalRetroAdapter(tmp_path, python_executable=tmp_path / "missing").expand("CCO")
    assert result["status"] == "unavailable"
    assert result["predictions"] == []
    assert result["elapsed_seconds"] >= 0


@pytest.mark.parametrize("target,top_k", [("bad smiles", 5), ("CCO", 0), ("CCO", True), ("CCO", 101)])
def test_localretro_validates_before_running(tmp_path, target, top_k):
    result = LocalRetroAdapter(tmp_path).expand(target, top_k=top_k)
    assert result["status"] == "error"


def test_localretro_translates_existing_model_contract(tmp_path, monkeypatch):
    for relative in ["req_data/LocalRetro_boltz_USPTO_MIT.pth", "req_data/USPTO_MIT/atom_templates.csv",
                     "req_data/USPTO_MIT/bond_templates.csv", "req_data/USPTO_MIT/template_infos.csv",
                     "rebolt_update_opt/localretro/LocalRetro/default_config.json",
                     "rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py"]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    seen = []

    def fake_worker(python, payload, timeout_seconds):
        seen.append(payload)
        return {"status": "ok", "predictions": [{"reactants": ["CCO"], "product": "CC=O", "score": 0.4}],
                "version": "sha256:test", "elapsed_seconds": 0.1, "diagnostic": ""}

    monkeypatch.setattr("synthesis_route_gym.adapters.localretro.run_worker", fake_worker)
    result = LocalRetroAdapter(tmp_path, python_executable=sys.executable).expand("CC=O", top_k=3)
    assert result["status"] == "ok"
    assert result["predictions"][0]["source"]["tool"] == "LocalRetro"
    assert result["predictions"][0]["evidence_status"] == "predicted"
    assert seen[0]["top_k"] == 3


def test_worker_timeout_is_bounded(monkeypatch):
    import subprocess

    class TimedOut:
        pid = 1000000000
        returncode = -9

        def communicate(self, *args, **kwargs):
            if kwargs.get("timeout"):
                raise subprocess.TimeoutExpired("worker", 0.01)
            return "", ""

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: TimedOut())
    monkeypatch.setattr("os.killpg", lambda *args: None)
    result = run_worker(sys.executable, {"backend": "test"}, 0.01)
    assert result["status"] == "error"
    assert result["diagnostic"] == "Inference timed out."


def test_worker_errors_do_not_leak_stderr(monkeypatch):
    import subprocess

    class Failed:
        returncode = 1

        def communicate(self, *args, **kwargs):
            return "", "Authorization: Bearer secret-token"

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: Failed())
    result = run_worker(sys.executable, {"backend": "test"}, 1)
    assert result["status"] == "error"
    assert "secret" not in json.dumps(result)


def test_worker_unknown_backend_is_explicit():
    result = run_worker(sys.executable, {"backend": "unknown"}, 5)
    assert result["status"] == "error"
    assert result["predictions"] == []


def test_aizynth_missing_config_returns_unavailable(tmp_path):
    result = AiZynthFinderAdapter(config_path=tmp_path / "missing.yml").expand("CCO")
    assert result["status"] == "unavailable"
    assert result["predictions"] == []


def test_aizynth_search_rejects_invalid_limits(tmp_path):
    result = AiZynthFinderAdapter(config_path=tmp_path / "config.yml").search("CCO", max_iterations=0)
    assert result["status"] == "error"


def test_aizynth_search_preserves_routes_without_claiming_feasibility(tmp_path, monkeypatch):
    config = tmp_path / "config.yml"
    config.write_text("{}")
    routes = [{"type": "mol", "smiles": "CCO", "in_stock": True}]
    monkeypatch.setattr("synthesis_route_gym.adapters.aizynthfinder.run_worker", lambda *a, **k: {
        "status": "ok", "predictions": [], "routes": routes, "version": "4.4.1",
        "elapsed_seconds": 0.1, "diagnostic": "",
    })
    result = AiZynthFinderAdapter(config_path=config).search("CCO")
    assert result["routes"] == routes
    assert "feasible" not in result


def test_platform_requires_registered_dispatcher():
    result = RegisteredPlatformAdapter().submit("CCO", experiment_name="test")
    assert result["status"] == "unavailable"


def test_platform_submit_uses_existing_tool_only():
    calls = []

    def dispatch(name, arguments):
        calls.append((name, arguments))
        return json.dumps({"doc_id": "job-123", "status": "accepted", "job_name": "retrosynthesis"})

    result = RegisteredPlatformAdapter(dispatch).submit("CCO", experiment_name="test")
    assert calls == [("boltzmann_submit", {
        "job_name": "retrosynthesis", "experiment_name": "test",
        "experiment_data": {"target_mol": "CCO", "outname": "test"},
    })]
    assert result["status"] == "ok"
    assert result["job"]["doc_id"] == "job-123"
    assert result["predictions"] == []
    assert result["complete"] is False


def test_platform_error_is_sanitized():
    def dispatch(*args):
        raise RuntimeError("secret-token private-url")

    result = RegisteredPlatformAdapter(dispatch).submit("CCO", experiment_name="test")
    assert result["status"] == "error"
    assert "secret-token" not in json.dumps(result)


def test_platform_status_does_not_interpret_completed_as_valid_route():
    adapter = RegisteredPlatformAdapter(lambda *args: {"status": "completed"})
    result = adapter.status("job-123")
    assert result["job"]["status"] == "completed"
    assert result["complete"] is False
    assert result["predictions"] == []
    assert result["job"]["doc_id"] == "job-123"


def test_failed_platform_job_is_an_error():
    adapter = RegisteredPlatformAdapter(lambda *args: {"status": "failed"})
    assert adapter.status("job-123")["status"] == "error"


def test_platform_refuses_unverified_submission_receipt():
    adapter = RegisteredPlatformAdapter(lambda *args: {"status": "accepted"})
    result = adapter.submit("CCO", experiment_name="test")
    assert result["status"] == "error"


def test_platform_invalid_inputs_never_dispatch():
    adapter = RegisteredPlatformAdapter(lambda *args: pytest.fail("Must not dispatch"))
    assert adapter.submit("CCO", "")["status"] == "error"
    assert adapter.status("")["status"] == "error"


def test_common_rejects_malformed_response_and_input():
    from synthesis_route_gym.adapters.common import canonical_smiles, normalise_result

    with pytest.raises(ValueError):
        canonical_smiles("")
    assert normalise_result({"status": "ok", "predictions": "bad"}, "m", 1)["status"] == "error"
    assert normalise_result({"status": "ok", "predictions": [{}]}, "m", 1)["status"] == "error"
    assert normalise_prediction({"reactants": ["CCO"], "product": "CC=O"}, "m", "1")["score"] is None
    assert run_worker(sys.executable, {}, -1)["status"] == "error"
    assert run_worker("/nonexistent/python", {}, 1)["status"] == "unavailable"


def test_worker_malformed_output_is_rejected(monkeypatch):
    class BadOutput:
        returncode = 0

        def communicate(self, *args, **kwargs):
            return "not json", ""

    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: BadOutput())
    assert run_worker(sys.executable, {}, 1)["status"] == "error"


@pytest.mark.parametrize("error,status", [(ModuleNotFoundError(), "unavailable"),
                                          (FileNotFoundError(), "unavailable"),
                                          (RuntimeError("private token"), "error")])
def test_worker_main_reports_sanitized_errors(monkeypatch, capsys, error, status):
    import io
    from synthesis_route_gym.adapters import _worker

    def fail(request):
        raise error

    monkeypatch.setattr(sys, "stdin", io.StringIO('{"backend":"localretro"}'))
    monkeypatch.setattr(_worker, "localretro", fail)
    _worker.main()
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == status
    assert "private token" not in result["diagnostic"]


def test_worker_main_rejects_unknown_backend(monkeypatch, capsys):
    import io
    from synthesis_route_gym.adapters import _worker

    monkeypatch.setattr(sys, "stdin", io.StringIO('{"backend":"unknown"}'))
    _worker.main()
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def test_localretro_worker_extracts_predictions_and_pins_weights(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import hashlib
    from synthesis_route_gym.adapters import _worker

    checkpoint = tmp_path / "req_data/LocalRetro_boltz_USPTO_MIT.pth"
    checkpoint.parent.mkdir()
    checkpoint.write_bytes(b"test-weight-artifact")
    class Frame:
        """Only the dataframe protocol the adapter consumes; no model dependencies."""
        def __init__(self, rows):
            self.rows = rows
            self.iloc = self

        def __getitem__(self, selection):
            return Frame(self.rows[selection])

        def to_dict(self, orient):
            assert orient == 'records'
            return self.rows

    model_output = Frame([{"SMILES": "CC=O", "Score": None},
                          {"SMILES": "CCO", "Score": 0.2}])
    fake = SimpleNamespace(init_LocalRetro=lambda args: (None,) * 5,
                           retrosnythesis=lambda *args, **kwargs: model_output)
    monkeypatch.setitem(sys.modules, "LocalRetro", SimpleNamespace(Retrosynthesis=fake))
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(device=lambda value: value,
                                                             set_num_threads=lambda value: None))
    result = _worker.localretro({"repo_root": str(tmp_path), "source_dir": str(tmp_path),
                                "target_smiles": "CC=O", "top_k": 3})
    assert result["predictions"] == [{"reactants": ["CCO"], "product": "CC=O", "score": 0.2}]
    assert result["checkpoint_sha256"] == hashlib.sha256(b"test-weight-artifact").hexdigest()


@pytest.mark.parametrize("operation", ["expand", "search"])
def test_aizynth_worker_respects_configured_stock_and_search_limits(monkeypatch, operation):
    from types import SimpleNamespace
    from synthesis_route_gym.adapters import _worker

    selected = []
    search = SimpleNamespace()
    reaction = SimpleNamespace(metadata={"policy_probability": 0.3},
                               reactants=[[SimpleNamespace(smiles="CCO")]])
    finder = SimpleNamespace(
        expansion_policy=SimpleNamespace(select=lambda v: selected.append(("expansion", v))),
        filter_policy=SimpleNamespace(select=lambda v: selected.append(("filter", v))),
        stock=SimpleNamespace(select=lambda v: selected.append(("stock", v)),
                              select_all=lambda: selected.append(("stock", "all"))),
        config=SimpleNamespace(search=search),
        do_expansion=lambda *args, **kwargs: [(reaction,)], prepare_tree=lambda: None,
        tree_search=lambda: None, build_routes=lambda: None,
        routes=SimpleNamespace(dicts=[{"type": "mol", "smiles": "CC=O"}]),
    )
    fake = SimpleNamespace(AiZynthFinder=lambda **kwargs: finder, AiZynthExpander=lambda **kwargs: finder)
    monkeypatch.setitem(sys.modules, "aizynthfinder.aizynthfinder", fake)
    monkeypatch.setattr(_worker.importlib.metadata, "version", lambda name: "test-version")
    result = _worker.aizynthfinder({"operation": operation, "config_path": "/test.yml",
                                   "expansion_policy": "uspto", "filter_policy": "filter",
                                   "stock_names": ["frozen-inventory"], "target_smiles": "CC=O",
                                   "top_k": 5, "max_iterations": 7, "max_transforms": 3})
    assert result["status"] == "ok"
    if operation == "search":
        assert ("stock", ["frozen-inventory"]) in selected
        assert search.iteration_limit == 7
        assert search.max_transforms == 3
        assert result["routes"][0]["smiles"] == "CC=O"
    else:
        assert result["predictions"][0]["reactants"] == ["CCO"]


def test_smoke_cli_reports_adapter_json(monkeypatch, capsys):
    from synthesis_route_gym.adapters import __main__

    class Fake:
        def __init__(self, *args, **kwargs):
            pass

        def expand(self, target, top_k):
            return {"status": "ok", "predictions": [], "target": target}

    monkeypatch.setattr(__main__, "LocalRetroAdapter", Fake)
    monkeypatch.setattr(sys, "argv", ["adapter", "localretro", "CCO"])
    assert __main__.main() == 0
    assert json.loads(capsys.readouterr().out)["target"] == "CCO"


def test_aizynth_cli_requires_config(monkeypatch):
    from synthesis_route_gym.adapters import __main__

    monkeypatch.setattr(sys, "argv", ["adapter", "aizynthfinder", "CCO"])
    with pytest.raises(SystemExit):
        __main__.main()


def test_aizynth_tree_normalizes_to_route_candidate():
    from synthesis_route_gym.adapters.aizynthfinder import normalise_aizynth_route
    from synthesis_route_gym.schemas import RouteCandidate

    tree = {"type": "mol", "smiles": "CC(=O)Oc1ccccc1C(=O)O", "children": [{
        "type": "reaction", "metadata": {"policy_probability": 0.4}, "children": [
            {"type": "mol", "smiles": "CC(=O)OC(C)=O", "in_stock": True},
            {"type": "mol", "smiles": "O=C(O)c1ccccc1O", "in_stock": True},
        ],
    }]}
    route = RouteCandidate.model_validate(normalise_aizynth_route(tree, "aspirin-1", "4.4.1"))
    assert len(route.steps) == 1
    assert route.steps[0].reactants[0].amount_mmol is None
    assert route.steps[0].proposal_score == 0.4
    assert route.steps[0].source_tool == "AiZynthFinder"
    assert route.steps[0].evidence_ids == ()
    assert route.steps[0].conditions_complete is False


def test_aizynth_stock_flag_does_not_override_gym_inventory():
    from synthesis_route_gym.adapters.aizynthfinder import normalise_aizynth_route
    from synthesis_route_gym.schemas import RouteCandidate, Task
    from synthesis_route_gym.validation import assess_route

    tree = {"type": "mol", "smiles": "CCO", "in_stock": True}
    route = RouteCandidate.model_validate(normalise_aizynth_route(tree, "stock-lie", "4.4.1"))
    assessment = assess_route(Task(task_id="empty", target="CCO", inventory=()), route)
    assert assessment.inventory_complete is False
    assert assessment.solved is False


@pytest.mark.parametrize("tree", [
    {"type": "reaction", "smiles": "CCO"},
    {"type": "mol", "smiles": "CCO", "children": [{"type": "reaction", "children": []}]},
    {"type": "mol", "smiles": "CCO", "children": [{"type": "mol", "smiles": "CC"}]},
    {"type": "mol", "smiles": "CCO", "children": [{"type": "reaction"}, {"type": "reaction"}]},
])
def test_aizynth_malformed_tree_is_rejected(tree):
    from synthesis_route_gym.adapters.aizynthfinder import normalise_aizynth_route

    with pytest.raises(ValueError):
        normalise_aizynth_route(tree, "bad-tree", "4.4.1")


def test_aizynth_route_cycle_is_rejected():
    from synthesis_route_gym.adapters.aizynthfinder import normalise_aizynth_route

    tree = {"type": "mol", "smiles": "CCO", "children": [{"type": "reaction", "children": [
        {"type": "mol", "smiles": "OCC"}]}]}
    with pytest.raises(ValueError, match="cycle"):
        normalise_aizynth_route(tree, "cycle", "4.4.1")


def test_aizynth_tree_rejects_nonfinite_policy_score():
    from synthesis_route_gym.adapters.aizynthfinder import normalise_aizynth_route

    tree = {"type": "mol", "smiles": "CCO", "children": [{"type": "reaction",
        "metadata": {"policy_probability": float("nan")},
        "children": [{"type": "mol", "smiles": "CC=O"}]}]}
    with pytest.raises(ValueError):
        normalise_aizynth_route(tree, "nan-score", "4.4.1")


def _baseline_script():
    import importlib.util

    path = Path(__file__).parents[1] / "scripts/run_aizynth_baseline.py"
    spec = importlib.util.spec_from_file_location("aizynth_baseline_test_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_baseline_uses_frozen_inventory_and_shared_one_step_budget(tmp_path):
    import yaml

    script = _baseline_script()
    task = script.make_task()
    config = yaml.safe_load(script.make_config(tmp_path, task).read_text())
    assert task.target not in {item.smiles for item in task.inventory}
    assert task.constraints.max_steps == config["search"]["max_transforms"] == 1
    assert task.budget.max_expansions == config["search"]["iteration_limit"] == 1
    assert config["expansion"]["uspto"]["cutoff_number"] == task.budget.top_k == 5
    assert len((tmp_path / "inventory.txt").read_text().splitlines()) == len(task.inventory)


def test_baseline_asset_download_requires_published_size_and_checksum(tmp_path, monkeypatch):
    import hashlib
    import io

    script = _baseline_script()
    monkeypatch.setattr(script, "PUBLIC_ASSETS", (("test.bin", "https://example.invalid/test",
                                                 3, hashlib.md5(b"abc").hexdigest()),))
    with pytest.raises(FileNotFoundError):
        script.provision_assets(tmp_path, False)
    monkeypatch.setattr(script, "urlopen", lambda *args, **kwargs: io.BytesIO(b"abc"))
    result = script.provision_assets(tmp_path, True)
    assert result[0]["sha256"] == hashlib.sha256(b"abc").hexdigest()
    monkeypatch.setattr(script, "urlopen", lambda *args, **kwargs: pytest.fail("Must use verified cache"))
    assert script.provision_assets(tmp_path, False) == result


def test_baseline_asset_download_rejects_excess_bytes(tmp_path, monkeypatch):
    import io

    script = _baseline_script()
    monkeypatch.setattr(script, "PUBLIC_ASSETS", (("test.bin", "https://example.invalid/test", 3, "unused"),))
    monkeypatch.setattr(script, "urlopen", lambda *args, **kwargs: io.BytesIO(b"abcd"))
    with pytest.raises(ValueError, match="published artifact size"):
        script.provision_assets(tmp_path, True)
    assert not (tmp_path / "test.bin").exists()
    assert not (tmp_path / "test.bin.part").exists()


def test_baseline_preserves_virtualenv_interpreter_symlink(tmp_path, monkeypatch):
    from types import SimpleNamespace

    script = _baseline_script()
    interpreter = tmp_path / "venv-python"
    interpreter.symlink_to(sys.executable)
    output = tmp_path / "output"
    output.mkdir()
    selected = []

    def fake_aizynth(**kwargs):
        selected.append(kwargs["python_executable"])
        return SimpleNamespace(search=lambda *a, **k: {"status": "ok", "routes": []})

    monkeypatch.setattr(script, "provision_assets", lambda *args: [])
    monkeypatch.setattr(script, "AiZynthFinderAdapter", fake_aizynth)
    monkeypatch.setattr(script, "LocalRetroAdapter", lambda **kwargs: SimpleNamespace(
        expand=lambda *a, **k: {"status": "ok", "predictions": []}))
    monkeypatch.setattr(sys, "argv", ["baseline", "--aizynth-python", str(interpreter),
                                     "--output", str(output)])
    assert script.main() == 0
    assert selected == [interpreter.absolute()]
    assert selected[0] != interpreter.resolve()
