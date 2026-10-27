"""Synthetic feedback/revision demonstration running actual upstream code."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .contracts import canonical
from .discovery import DiscoveryCoordinator
from .store import Store


def fixture_task(directory):
    directory = Path(directory)
    structure = directory / "synthetic_parent.pdb"
    lines = []
    # The coordinates are a parser fixture, not a physically valid fold. Keep
    # sequence and residue numbering consistent even in synthetic checks.
    for position, aa in enumerate("AGAAAAAAAA", 1):
        residue = "GLY" if aa == "G" else "ALA"
        atoms = ["N", "CA", "C", "O"] + ([] if aa == "G" else ["CB"])
        for offset, atom in enumerate(atoms):
            lines.append(f"ATOM  {len(lines) + 1:5d} {atom:>4} {residue} A{position:4d}    "
                         f"{position * 3.8 + offset * 0.2:8.3f}{0.0:8.3f}{0.0:8.3f}  1.00 20.00          {atom[0]:>2}")
    structure.write_text("\n".join(lines) + "\nEND\n")
    return {"schema_version": "enzyme-research-task/1", "task_id": "synthetic_feedback_fixture",
            "objective": "Test feedback-driven revision only; no activity claim",
            "parent": {"candidate_id": "parent", "sequence": "AGAAAAAAAA",
                "structure": {"path": str(structure), "sha256": hashlib.sha256(structure.read_bytes()).hexdigest()},
                "catalytic_residues": [{"chain": "A", "residue": "2", "sequence_position": 2, "amino_acid": "G"}]},
            "substrate": {"name": "synthetic substrate", "smiles": "CCO"},
            "allowed_jobs": ["FixtureActivity", "FixtureStability"],
            "budget": {"max_rounds": 2, "max_unique_candidates": 6, "max_outstanding_jobs": 1, "max_scientific_submissions": 8},
            "evidence_sources": ["Explicitly synthetic engineering fixture, not a molecular tool calculation"],
            "evidence_track": "synthetic"}


def demo(output, upstream):
    output = Path(output).absolute()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    store = Store(output / "state")
    task = fixture_task(output)
    (output / "task.json").write_text(canonical(task) + "\n")
    campaign = store.start(task, "specialist")
    store.add_candidates(campaign, [{"candidate_id": "candidate_1", "parent_id": "parent", "sequence": "AGCAAAAAAA"}])

    def propose(context):
        revised = bool(context["observations"])
        if revised:
            assert context["observations"][-1]["metrics"]["candidate_1"]["stability_proxy"] < 0
        return [{"claim": "Inspect a conservative repair after the observed stability defect" if revised else "Check the first proposed variant",
                 "plan": "Request a stability check" if revised else "Request an activity screen",
                 "alternatives": ["Higher predicted activity need not preserve stability or measured function"],
                 "evidence_refs": [o["observation_id"] for o in context["observations"]],
                 "revision_reason": "Prior result showed a stability defect; change investigation" if revised else "Initial bounded investigation",
                 "action": {"kind": "stability" if revised else "activity",
                    "job_name": "FixtureStability" if revised else "FixtureActivity",
                    "experiment_data": {"fixture_only": True}, "candidate_ids": ["candidate_1"]}}]

    def critique(hypothesis, context):
        return {"score": 7, "critique": "Bounded test with an explicit alternative; no experimental evidence", "decision": "test"}

    coordinator = DiscoveryCoordinator(store, upstream)
    first = coordinator.advance(campaign, propose, critique)
    call = store.prepare_call(campaign, "synthetic_observation", {"fixture": "low_stability",
                              "job_name": first["action"]["job_name"], "experiment_data": first["action"]["experiment_data"]})
    store.call_transition(campaign, call, "sending")
    store.call_transition(campaign, call, "completed", {"synthetic_only": True})
    store.add_observation(campaign, {"observation_id": "observation-1", "kind": "stability", "candidate_ids": ["candidate_1"],
        "evidence_level": "synthetic_fixture", "metrics": {"candidate_1": {"activity_proxy": 1.2, "stability_proxy": -0.8}},
        "artifacts": [], "source_call_id": call})
    store.decision_observed(campaign, 1, ["observation-1"])
    # A fresh instance reads previous decisions/observations, not an in-memory shortcut.
    reopened = Store(output / "state")
    second = DiscoveryCoordinator(reopened, upstream).advance(campaign, propose, critique)
    report = {"success": first["action"]["job_name"] != second["action"]["job_name"],
              "campaign_id": campaign, "synthetic_only": True, "actual_upstream_code_executed": True,
              "upstream_revision": first["upstream_revision"], "restart_recovered": True,
              "first_action": first["action"]["job_name"], "revised_action": second["action"]["job_name"],
              "observations_used_for_revision": second["hypotheses"][0]["evidence"],
              "real_model_requests": 0, "scientific_platform_jobs": 0, "gpu_used": False,
              "scientific_improvement_established": False,
              "remaining": "Second decision awaits real execution; this fixture is not live completion"}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
