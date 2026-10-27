import json
from pathlib import Path
from types import SimpleNamespace


def test_authorization_failure_saves_redacted_report_and_audit(store, campaign, tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "src"))
    from enzyme_environment import connection
    from enzyme_environment.policy import verify_audit
    from enzyme_research.native_episode import run_native_step

    def unavailable(profile):
        raise RuntimeError("private-provider-diagnostic-not-for-report")

    monkeypatch.setattr(connection, "authorize_read_only", unavailable)
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()
    (catalogue / "tool-contracts.v1.json").write_text('{"tools":{}}')
    service = SimpleNamespace(store=store, settings={"catalogue_root": str(catalogue)})
    runtime = SimpleNamespace(check=lambda: None, source_snapshot=lambda: {"fixture": "unchanged"},
                              export_source=lambda target, before: target.mkdir(), profile=tmp_path / "unused-profile")
    output = tmp_path / "failed-native-step"
    result = run_native_step(service, campaign, runtime, output, backend="live")
    assert not result["success"] and result["real_model_requests"] == 0
    assert result["execution_failure"]["stage"] == "model_authorization"
    assert result["source_unchanged"] and not result["local_gpu_used"]
    assert "private-provider-diagnostic" not in (output / "report.json").read_text()
    assert verify_audit(output / "host_only/audit.jsonl")
    assert not hasattr(service, "model_roles")
    assert store.status(campaign)["events"][-1]["payload"]["event"] == "native_step_finished"
