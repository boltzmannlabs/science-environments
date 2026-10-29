import json
from pathlib import Path

from enzyme_research.service import ResearchService


def test_role_context_uses_actual_catalogue_and_upload_receipts(store, campaign, tmp_path):
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()
    (catalogue / "tool-contracts.v1.json").write_text(json.dumps({"tools": {"FixtureActivity": {"status": "active", "job_name": "FixtureActivity", "source": "canonical_fixture"}}}))
    service = object.__new__(ResearchService)
    service.store = store
    service.settings = {"catalogue_root": str(catalogue)}
    context = service.tool_context(store.status(campaign))
    assert context["tool_contracts"]["FixtureActivity"]["source"] == "canonical_fixture"
    assert context["confirmed_uploads"] == []
    assert context["prepared_inputs"] == []
