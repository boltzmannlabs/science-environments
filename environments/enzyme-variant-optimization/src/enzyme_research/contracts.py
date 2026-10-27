"""Scientific task contracts, not copies of remote scientific tool schemas."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
ARMS = {"fixed", "base", "specialist"}
KINDS = {"sequence_design", "activity", "stability", "solubility", "folding",
         "quality", "geometry", "docking", "evidence"}
FORBIDDEN_KEYS = {"tokenid", "token", "api_key", "apikey", "access_token", "authorization", "password", "secret",
                  "experimental_score", "test_labels", "final_answers", "answers"}


class ResearchError(ValueError):
    pass


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ResearchError("Values must be finite JSON") from exc


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def identifier(value, name="identifier"):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value):
        raise ResearchError(name + " must be a simple nonempty identifier")
    return value


def safe_data(value):
    """No credentials, signed links, nonfinite values or final answer tables in state."""
    canonical(value)
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key.lower() in FORBIDDEN_KEYS:
                raise ResearchError("Credentials and experimental answers do not belong in research state")
            safe_data(item)
    elif isinstance(value, list):
        for item in value:
            safe_data(item)
    elif isinstance(value, str):
        lower = value.lower()
        if ("bearer " in lower or "-----begin private key" in lower
                or "x-goog-signature=" in lower or "x-amz-signature=" in lower
                or re.search(r"(?i)([?&](token|signature|sig)=|eyJ[\w-]+\.[\w-]+\.)", value)):
            raise ResearchError("Credential-bearing data cannot be persisted")


def strict_load(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 2 * 1024**2:
        raise ResearchError("JSON input must be a bounded nonempty regular file")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ResearchError("Duplicate JSON keys are not allowed")
            result[key] = value
        return result
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=pairs,
                           parse_constant=lambda x: (_ for _ in ()).throw(ResearchError("Nonfinite JSON")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ResearchError("Malformed JSON input") from exc
    safe_data(value)
    return value


def task_contract(value):
    safe_data(value)
    required = {"schema_version", "task_id", "objective", "parent", "substrate",
                "allowed_jobs", "budget", "evidence_sources", "evidence_track"}
    if not isinstance(value, dict) or not required <= set(value) or set(value) - required - {"candidate_library"}:
        raise ResearchError("Unexpected or missing research-task fields")
    if value["schema_version"] != "enzyme-research-task/1":
        raise ResearchError("Unsupported research-task version")
    identifier(value["task_id"], "task_id")
    if not isinstance(value["objective"], str) or not value["objective"].strip():
        raise ResearchError("A scientific objective is required")
    if value["evidence_track"] not in {"synthetic", "computational", "protected_measured_library"}:
        raise ResearchError("Unknown evidence track")
    parent = value["parent"]
    if not isinstance(parent, dict) or set(parent) != {"candidate_id", "sequence", "structure", "catalytic_residues"}:
        raise ResearchError("Parent needs sequence, structure and explicit catalytic mapping")
    identifier(parent["candidate_id"], "parent candidate_id")
    sequence = parent["sequence"]
    if not isinstance(sequence, str) or not 2 <= len(sequence) <= 2000 or set(sequence) - AMINO_ACIDS:
        raise ResearchError("Parent sequence must contain 2-2000 standard uppercase amino acids")
    structure = parent["structure"]
    if not isinstance(structure, dict) or set(structure) != {"path", "sha256"}:
        raise ResearchError("Parent structure requires a path and trusted SHA256")
    if not isinstance(structure["path"], str) or not structure["path"]:
        raise ResearchError("Parent structure path is required")
    if not isinstance(structure["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", structure["sha256"]):
        raise ResearchError("Parent structure SHA256 is invalid")
    residues = parent["catalytic_residues"]
    if not isinstance(residues, list) or not residues:
        raise ResearchError("Explicit catalytic residue mapping is required")
    seen = set()
    for item in residues:
        if not isinstance(item, dict) or set(item) != {"chain", "residue", "sequence_position", "amino_acid"}:
            raise ResearchError("Catalytic mappings require chain, residue, sequence_position and amino_acid")
        pos = item["sequence_position"]
        if type(pos) is not int or not 1 <= pos <= len(sequence) or pos in seen:
            raise ResearchError("Catalytic sequence positions must be valid and unique")
        if item["amino_acid"] != sequence[pos - 1]:
            raise ResearchError("Catalytic identity disagrees with the parent sequence")
        if not isinstance(item["chain"], str) or len(item["chain"]) != 1 or not isinstance(item["residue"], str) or not item["residue"]:
            raise ResearchError("Catalytic structural labels must be explicit")
        seen.add(pos)
    substrate = value["substrate"]
    if not isinstance(substrate, dict) or set(substrate) != {"name", "smiles"} or any(not isinstance(x, str) or not x.strip() for x in substrate.values()):
        raise ResearchError("Substrate name and case-preserved SMILES are required")
    jobs = value["allowed_jobs"]
    if not isinstance(jobs, list) or not jobs or len(set(jobs)) != len(jobs):
        raise ResearchError("Allowed jobs must be a nonempty unique list")
    for job in jobs:
        identifier(job, "allowed job")
    budget = value["budget"]
    caps = {"max_rounds": 3, "max_unique_candidates": 60, "max_outstanding_jobs": 1,
            "max_scientific_submissions": 200}
    if not isinstance(budget, dict) or set(budget) != set(caps):
        raise ResearchError("Explicit round, candidate and submission limits are required")
    for key, cap in caps.items():
        if type(budget[key]) is not int or not 1 <= budget[key] <= cap:
            raise ResearchError(key + " exceeds the declared first-environment envelope")
    if not isinstance(value["evidence_sources"], list) or not value["evidence_sources"]:
        raise ResearchError("Evidence provenance is required")
    if any(not isinstance(source, str) or not source.strip() for source in value["evidence_sources"]):
        raise ResearchError("Evidence sources must be nonempty strings")
    if value["evidence_track"] == "protected_measured_library":
        candidate_library(value)
    elif "candidate_library" in value:
        raise ResearchError("A measured candidate library belongs only to the protected-library track")
    return json.loads(canonical(value))


def candidate_library(task):
    """Validate public candidate identities, never protected assay labels.

    The operator curates the measured library separately. This manifest only
    limits which sequences may enter the retrospective research campaign; its
    existence does not establish that assay curation or independent scoring is
    complete. IDs are stable across generated tool row names and research arms.
    """
    library = task.get("candidate_library")
    if not isinstance(library, dict) or set(library) != {"library_id", "members", "members_sha256"}:
        raise ResearchError("Protected-library tasks require a frozen public candidate library")
    identifier(library["library_id"], "library_id")
    members = library["members"]
    if not isinstance(members, list) or not 1 <= len(members) <= 10000:
        raise ResearchError("Candidate library must contain 1-10000 explicit public members")
    sequences, ids = {}, set()
    parent = task["parent"]
    for member in members:
        if not isinstance(member, dict) or set(member) != {"member_id", "sequence"}:
            raise ResearchError("Public library members contain only member_id and sequence, not assay values")
        mid, sequence = member["member_id"], member["sequence"]
        identifier(mid, "library member_id")
        if mid in ids or not isinstance(sequence, str) or sequence in sequences:
            raise ResearchError("Candidate library IDs and sequences must be unique")
        if len(sequence) != len(parent["sequence"]) or set(sequence) - AMINO_ACIDS:
            raise ResearchError("Library sequences must be substitution-only standard amino acids")
        if any(sequence[site["sequence_position"] - 1] != site["amino_acid"] for site in parent["catalytic_residues"]):
            raise ResearchError("Library member changes a protected catalytic residue")
        ids.add(mid)
        sequences[sequence] = mid
    if digest(members) != library["members_sha256"]:
        raise ResearchError("Public candidate library does not match its frozen hash")
    if parent["sequence"] not in sequences:
        raise ResearchError("Protected evaluation requires the parent in the declared measured library")
    return sequences


def candidate_record(task, value):
    if not isinstance(value, dict) or set(value) != {"candidate_id", "parent_id", "sequence"}:
        raise ResearchError("Candidate requires candidate_id, parent_id and sequence")
    identifier(value["candidate_id"], "candidate_id")
    identifier(value["parent_id"], "parent_id")
    sequence = value["sequence"]
    parent = task["parent"]["sequence"]
    if not isinstance(sequence, str) or len(sequence) != len(parent) or set(sequence) - AMINO_ACIDS:
        raise ResearchError("This optimization version accepts substitution-only standard sequences")
    for site in task["parent"]["catalytic_residues"]:
        if sequence[site["sequence_position"] - 1] != site["amino_acid"]:
            raise ResearchError("Candidate changes a protected catalytic residue")
    membership = {}
    if task["evidence_track"] == "protected_measured_library":
        members = candidate_library(task)
        if sequence not in members:
            raise ResearchError("Novel sequences cannot enter a protected measured-library campaign")
        membership = {"library_id": task["candidate_library"]["library_id"],
                      "library_member_id": members[sequence],
                      "library_members_sha256": task["candidate_library"]["members_sha256"]}
    return {**value, **membership, "sequence_sha256": hashlib.sha256(sequence.encode()).hexdigest(),
            "mutations_from_reference": [f"{a}{i}{b}" for i, (a, b) in enumerate(zip(parent, sequence), 1) if a != b],
            "structure_status": "requires_new_structure", "status": "proposed"}


def observation_record(value):
    safe_data(value)
    fields = {"observation_id", "kind", "candidate_ids", "evidence_level", "metrics", "artifacts", "source_call_id"}
    if not isinstance(value, dict) or not fields <= set(value) or set(value) - fields - {"coordinate_scope"}:
        raise ResearchError("Unexpected or missing observation fields")
    identifier(value["observation_id"], "observation_id")
    identifier(value["source_call_id"], "source_call_id")
    if value["kind"] not in KINDS:
        raise ResearchError("Unknown scientific observation kind")
    if value["evidence_level"] not in {"synthetic_fixture", "computational_prediction", "structural_measurement", "literature_evidence"}:
        raise ResearchError("Agent-visible observations cannot contain experimental test answers")
    if not isinstance(value["candidate_ids"], list) or not value["candidate_ids"] or len(set(value["candidate_ids"])) != len(value["candidate_ids"]):
        raise ResearchError("Observation candidate IDs must be explicit and unique")
    for cid in value["candidate_ids"]:
        identifier(cid, "candidate_id")
    if not isinstance(value["metrics"], dict) or not value["metrics"]:
        raise ResearchError("Empty scientific results are not observations")
    if value["kind"] in {"quality", "geometry"}:
        scope = value.get("coordinate_scope")
        if not isinstance(scope, dict) or set(scope) != {"structure_candidates", "outcomes", "execution_mode"}:
            raise ResearchError("Quality/geometry observations require their exact coordinate scope")
        versions, outcomes = scope["structure_candidates"], scope["outcomes"]
        if (not isinstance(versions, dict) or not versions or not isinstance(outcomes, dict) or set(outcomes) != set(versions)
                or scope["execution_mode"] not in {"measurement_only", "validation"}):
            raise ResearchError("Coordinate scope needs explicit versions, matching outcomes and execution mode")
        for sid, cid in versions.items():
            identifier(sid, "structure_id")
            identifier(cid, "coordinate candidate_id")
        if set(versions.values()) != set(value["candidate_ids"]) or set(value["metrics"]) != set(value["candidate_ids"]):
            raise ResearchError("Structural measurement candidates must match their coordinate versions")
        for sid, cid in versions.items():
            identifier(sid, "structure_id")
            if outcomes[sid] not in {"measured", "passed", "rejected", "invalid"}:
                raise ResearchError("Unknown structural measurement outcome")
            if scope["execution_mode"] == "measurement_only" and outcomes[sid] not in {"measured", "invalid"}:
                raise ResearchError("A measurement-only structural result cannot claim a pass/reject decision")
            if scope["execution_mode"] == "validation" and outcomes[sid] == "measured":
                raise ResearchError("Validation requires actual pass/reject outcomes")
            grouped = value["metrics"][cid]
            expected = {key for key, candidate in versions.items() if candidate == cid}
            if not isinstance(grouped, dict) or set(grouped) != {"by_structure"} or not isinstance(grouped["by_structure"], dict) or set(grouped["by_structure"]) != expected:
                raise ResearchError("Structural metrics must be grouped by their exact coordinate version")
    elif "coordinate_scope" in value:
        raise ResearchError("Only explicit quality/geometry measurements use coordinate_scope")
    if not isinstance(value["artifacts"], list):
        raise ResearchError("Artifact receipts must be a list")
    for artifact in value["artifacts"]:
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
            raise ResearchError("Each artifact needs its verified path and hash")
        if not re.fullmatch(r"[0-9a-f]{64}", str(artifact["sha256"])):
            raise ResearchError("Invalid artifact SHA256")
    return json.loads(canonical(value))
