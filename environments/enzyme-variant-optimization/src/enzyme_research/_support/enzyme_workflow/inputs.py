"""Build portable, candidate-labelled inputs from verified workflow artifacts."""

import csv
import json
import zipfile
from pathlib import Path

from .artifacts import read_members
from .common import WorkflowError, atomic_json, file_hash, identifier


def build_input(root, workflow_id, step_id, field, reference, state, candidate_ids, *, catpred_pairs=None):
    dep = reference["from_step"]
    upstream = state["steps"][dep]
    artifact = reference["artifact"]
    source = upstream.get("artifact_path")
    if not source or file_hash(source) != upstream["artifact_sha256"]:
        raise WorkflowError("Upstream artifact is missing or changed; revalidate it")
    destination = Path(root) / workflow_id / "inputs" / step_id
    destination.mkdir(parents=True, exist_ok=True)
    identifier(field, "input field")
    upload_as = reference["upload_as"]
    if upload_as not in {"zip", "csv", "fasta", "json", "artifact", "array", "string"}:
        raise WorkflowError("Unsupported artifact conversion")
    if artifact == "artifact":
        if set(candidate_ids) != set(upstream.get("candidate_ids", [])):
            raise WorkflowError("Whole artifact includes unselected candidates; use structures/sequences export")
        return Path(source)
    selected = [state["candidates"][cid] for cid in candidate_ids]
    if not selected:
        raise WorkflowError("Cannot build an input for an empty candidate set")
    if artifact == "sequences" and upload_as in {"array", "string"}:
        if len(selected) != 1 or not selected[0].get("sequence"):
            raise WorkflowError("A direct sequence request represents exactly one candidate, not a multi-parent batch")
        sequence = selected[0]["sequence"]
        return sequence.split(":") if upload_as == "array" else sequence
    target = destination / f"{field}.{upload_as}"
    if artifact == "structures" and upload_as == "zip":
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for candidate in selected:
                structure = candidate.get("structure")
                if not structure:
                    raise WorkflowError("Candidate has no prepared structure")
                if file_hash(structure["artifact_path"]) != structure["sha256"]:
                    raise WorkflowError("Candidate structure artifact changed")
                content = read_members(structure["artifact_path"])[structure["member"]]
                archive.writestr(candidate["candidate_id"] + Path(structure["member"]).suffix, content)
            if all(c.get("mapping") for c in selected):
                archive.writestr("entity_mapping.json", json.dumps({c["candidate_id"]: c["mapping"] for c in selected}))
                complete = all({"all_atom", "ligand"} <= set(c["capabilities"]) for c in selected)
                archive.writestr("manifest.json", json.dumps({"tool": "enzyme_workflow", "output_kind": "all_atom_complex" if complete else "backbone_only"}))
    elif artifact == "sequences" and upload_as in {"csv", "fasta"}:
        for c in selected:
            if not c.get("sequence"):
                raise WorkflowError("Candidate has no designed sequence")
        if upload_as == "csv":
            if catpred_pairs is not None:
                from .catpred import write_input
                if {p["candidate_id"] for p in catpred_pairs} != set(candidate_ids):
                    raise WorkflowError("CatPred export differs from the selected candidates")
                write_input(target, catpred_pairs)
            else:
                with target.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["seq_id", "sequences"])
                    writer.writeheader()
                    writer.writerows({"seq_id": c["candidate_id"], "sequences": c["sequence"]} for c in selected)
        else:
            target.write_text("".join(f">{c['candidate_id']}\n{c['sequence']}\n" for c in selected), encoding="utf-8")
    elif artifact == "mapping" and upload_as == "json":
        if not all(c.get("mapping") for c in selected):
            raise WorkflowError("Mapping export requires explicit mappings for every selected candidate")
        atomic_json(target, {c["candidate_id"]: c["mapping"] for c in selected})
    else:
        raise WorkflowError("Unsupported input conversion; use an audited preparation step, not an improvised conversion")
    return target
