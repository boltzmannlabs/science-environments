"""Synthetic observer replay; NEVER a production API submission or scientific run."""
import argparse
import csv
import io
import json
from pathlib import Path
import zipfile

from enzyme_workflow.artifacts import QUALITY_METRICS
from enzyme_workflow.connector import before, after
from enzyme_workflow.contract_registry import load_registry, REGISTRY_PATH
from enzyme_workflow.harness import Harness
from enzyme_workflow.state import Store


class FixtureHarness(Harness):
    """Use the real tracker against explicit test routing, not a user's profile."""
    def __init__(self, root, catalogue, bindings):
        self.store = Store(root)
        self.registry = load_registry(bindings, catalog_root=catalogue)


def fixture_catalogue(root):
    tools = json.loads(REGISTRY_PATH.read_text())["tools"]
    entries = {}
    for metadata in tools.values():
        reference = metadata.get("contract_ref") or {}
        name = reference.get("entry")
        if name:
            entries[name] = {"job_name": name, "status": "active", "execution_blocked": False,
                             "submission": {"wire_job_name": name}, "diagnostics": [],
                             "notes": "SYNTHETIC fixture routing only; no scientific request schema"}
    bindings = {}
    for tool in ("mol_probity", "netsolp"):
        name = "OfflineFixture_" + tool
        entries[name] = {"job_name": name, "status": "active", "execution_blocked": False,
                         "submission": {"wire_job_name": name}, "diagnostics": []}
        bindings[tool] = {"backend_status": "active", "job_name": name, "collection_name": name,
                          "contract_ref": {"path": "tool-contracts.v1.json", "entry": name}}
    catalogue = root / "fixture_catalogue"
    catalogue.mkdir()
    (catalogue / "tool-contracts.v1.json").write_text(json.dumps({
        "schema": "boltzmann-tool-contracts.v1", "schema_version": 2, "status": "canonical",
        "warning": "Synthetic replay fixture; NEVER use as a production catalogue", "tools": entries}))
    return catalogue, bindings


def mock_structure():
    atoms = ["N", "CA", "C", "O", "CB"]
    lines = [f"ATOM  {i:5d} {name:>4} ALA A   1    {float(i):8.3f}{0.0:8.3f}{0.0:8.3f}  1.00 20.00           C"
             for i, name in enumerate(atoms, 1)]
    return "\n".join(lines) + "\nEND\n"


def replay_submission(harness, workflow, step):
    prepared = harness.next(workflow, "prepare", step)
    for upload in prepared.get("uploads", []):
        harness.next(workflow, "record_upload", step, field=upload["field"],
                     result={"s3_path": "fixtures/" + step + "/" + upload["field"] + ".csv"})
    prepared = harness.next(workflow, "prepare", step)
    args = prepared["call"]["args"]
    receipt = before("boltzmann_submit", args, harness.store.root)
    job = {"job_name": args["job_name"], "doc_id": "mock-job-" + step}
    after("boltzmann_submit", args, job, receipt)
    return job


def replay_download(harness, workflow, step, job, path, bindings=None):
    link = "https://offline.invalid/" + step + "/mock-output"
    after("boltzmann_status", job, {"status": "completed", "download_link": link}, root=harness.store.root)
    after("boltzmann_download", {"download_url": link}, {"output_paths": [str(path)]}, root=harness.store.root)
    return harness.next(workflow, "ingest", step, local_path=str(path), bindings=bindings)


def run(output):
    root = Path(output).absolute()
    root.mkdir(parents=True, exist_ok=False)
    catalogue, bindings = fixture_catalogue(root)
    h = FixtureHarness(root / "state", catalogue, bindings)
    initial = []
    for name in ("a", "b"):
        path = root / ("mock_" + name + ".pdb")
        path.write_text(mock_structure())
        initial.append({"candidate_id": "fixture_" + name, "local_path": str(path)})
    plan = {"objective": "SYNTHETIC tracker replay; no enzyme predictions", "approved": True,
            "initial_candidates": initial, "steps": [
        {"step_id": "quality", "tool": "mol_probity", "experiment_name": "Offline MOCK quality",
         "candidate_ids": ["fixture_a", "fixture_b"],
         "inputs": {"input_path": "fixtures/output.zip", "execution_mode": "validation",
                                                    "quality_thresholds": {"max_clashscore": 10}}},
        {"step_id": "properties", "tool": "netsolp", "experiment_name": "Offline MOCK property",
         "depends_on": ["quality"], "selection": "passed", "required_gates": ["quality"],
         "inputs": {"input_path": {"from_step": "quality", "artifact": "sequences", "upload_as": "csv"}}},
    ]}
    workflow = h.start(plan)["workflow_id"]
    h = FixtureHarness(root / "state", catalogue, bindings)
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=["candidate_id", "status", *QUALITY_METRICS])
    writer.writeheader()
    for label, status, score in (("mock_a", "passed", 1), ("mock_b", "rejected", 20)):
        row = {name: 0 for name in QUALITY_METRICS}
        row.update(candidate_id=label, status=status, clashscore=score, ramachandran_favored_percent=100)
        writer.writerow(row)
    quality = root / "mock_quality.zip"
    with zipfile.ZipFile(quality, "w") as zipped:
        zipped.writestr("candidate_summary.csv", stream.getvalue())
    replay_download(h, workflow, "quality", replay_submission(h, workflow, "quality"), quality,
                    {"mock_a": {"candidate_id": "fixture_a"}, "mock_b": {"candidate_id": "fixture_b"}})
    h = FixtureHarness(root / "state", catalogue, bindings)
    job = replay_submission(h, workflow, "properties")
    state = h.status(workflow)["state"]
    selected = state["steps"]["properties"]["input_candidate_ids"]
    if len(selected) != 1:
        raise ValueError("Quality gate did not retain exactly one fixture candidate")
    properties = root / "mock_properties.csv"
    properties.write_text("seq_id,mock_score\n" + selected[0] + ",0.75\n")
    replay_download(h, workflow, "properties", job, properties, {selected[0]: {"candidate_id": selected[0]}})
    h = FixtureHarness(root / "state", catalogue, bindings)
    report = h.report(workflow)
    result = {"success": report["status"] == "complete", "synthetic_only": True,
              "actual_remote_submissions": 0, "actual_scientific_model_runs": 0,
              "workflow_id": workflow, "steps": 2, "supplied_mock_candidates": 2,
              "forwarded_after_mock_quality": 1, "report_path": report["report_path"]}
    (root / "example_receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    print(json.dumps(run(parser.parse_args().output)))
