import pytest

from enzyme_research.connector import TrackedConnector
from enzyme_research.contracts import ResearchError, digest


class Connector:
    def __init__(self, warnings): self.warnings, self.calls = warnings, []
    def call(self, name, args):
        self.calls.append((name, args))
        if name.startswith("connector_validate_"):
            return {"level": "partial", "warnings": self.warnings, "errors": []}
        return {"s3_path": "users/owned/input.csv"}


def approval(store, campaign):
    return {"task_sha256": digest(store.status(campaign)["task"]),
            "allowed_warnings": ["known semantic caveat"], "source": "explicit_user_consent"}


def test_no_model_flag_without_consent(store, campaign):
    connector = Connector([])
    with pytest.raises(ResearchError):
        TrackedConnector(store, connector).execute(campaign, "boltzmann_upload", {
            "job_name": "FixtureActivity", "allow_partial_validation": True})
    assert not connector.calls


def test_consent_checks_exact_current_warnings(store, campaign):
    connector = Connector(["known semantic caveat"])
    result = TrackedConnector(store, connector, approval(store, campaign)).execute(campaign, "boltzmann_upload", {
        "job_name": "FixtureActivity", "input_field": "input_path", "local_path": "/fixture.csv"})
    assert result["status"] == "completed"
    assert connector.calls[0][0] == "connector_validate_upload"
    assert connector.calls[1][1]["allow_partial_validation"] is True


def test_new_warning_still_stops_before_upload(store, campaign):
    connector = Connector(["a different unapproved caveat"])
    with pytest.raises(ResearchError):
        TrackedConnector(store, connector, approval(store, campaign)).execute(campaign, "boltzmann_upload", {"job_name": "FixtureActivity"})
    assert [name for name, args in connector.calls] == ["connector_validate_upload"]
    assert not store.status(campaign)["calls"]


def test_approval_not_transferable_to_other_task(store, campaign):
    consent = approval(store, campaign)
    consent["task_sha256"] = "0" * 64
    connector = Connector([])
    with pytest.raises(ResearchError):
        TrackedConnector(store, connector, consent).execute(campaign, "boltzmann_upload", {"job_name": "FixtureActivity"})
    assert not connector.calls


@pytest.mark.parametrize("operation", ["boltzmann_upload", "boltzmann_submit"])
def test_validation_block_is_known_not_an_unknown_operation(store, campaign, operation):
    class Blocked:
        def call(self, name, args):
            return {"stage": "validation", "status": "approval_required", "error": "Explicit approval required"}
    result = TrackedConnector(store, Blocked()).execute(campaign, operation, {"job_name": "FixtureActivity"})
    assert result["status"] == "definite_failure"
