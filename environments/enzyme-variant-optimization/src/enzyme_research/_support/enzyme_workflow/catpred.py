"""CatPred CSV preparation and exact, row-order-independent candidate joins.

This is a local workflow adapter, not a new scientific model or HTTP client.
Chemical validation remains with CatPred. SMILES case is never changed.
"""

import csv
import math

from .artifacts import csv_rows, read_members, validate_sequence
from .common import WorkflowError, file_hash, identifier, validate_data

MODES = ("kcat", "km", "ki")
UNCERTAINTY = ("Prediction_log10", "SD_total", "SD_aleatoric", "SD_epistemic")
RESULT_COLUMNS = MODES + tuple(f"{mode}_{metric}" for mode in MODES for metric in UNCERTAINTY)


def _smiles(value):
    if not isinstance(value, str) or not value.strip() or any(c.isspace() for c in value):
        raise WorkflowError("CatPred handoff SMILES must be nonempty text without whitespace; preserve chemical letter case")
    return value


def validate_handoff(value):
    if not isinstance(value, dict) or set(value) not in ({"smiles"}, {"smiles_by_candidate"}):
        raise WorkflowError("CatPred step needs handoff.smiles or handoff.smiles_by_candidate, not both; this stays local and is not an API field")
    if "smiles" in value:
        _smiles(value["smiles"])
    else:
        items = value["smiles_by_candidate"]
        if not isinstance(items, dict) or not items:
            raise WorkflowError("CatPred handoff.smiles_by_candidate must be a nonempty candidate-to-SMILES object")
        for cid, smiles in items.items():
            identifier(cid, "CatPred candidate_id")
            _smiles(smiles)


def requested_pairs(state, candidate_ids, handoff):
    validate_handoff(handoff)
    if not candidate_ids:
        raise WorkflowError("CatPred needs selected candidates with designed protein sequences")
    by_candidate = handoff.get("smiles_by_candidate")
    if by_candidate is not None and set(by_candidate) != set(candidate_ids):
        raise WorkflowError("CatPred smiles_by_candidate must cover exactly the selected candidate IDs")
    pairs = []
    for cid in candidate_ids:
        candidate = state["candidates"][cid]
        sequence = candidate.get("sequence")
        if not isinstance(sequence, str):
            raise WorkflowError("CatPred needs a designed sequence for every selected candidate")
        validate_sequence(sequence)
        if ":" in sequence:
            raise WorkflowError("CatPred accepts one protein chain per row; do not concatenate or silently split chains")
        smiles = by_candidate[cid] if by_candidate is not None else handoff["smiles"]
        pairs.append({"candidate_id": cid, "sequence": sequence, "smiles": smiles})
    _pair_index(pairs)
    return pairs


def _pair_index(pairs):
    if not isinstance(pairs, list) or not pairs:
        raise WorkflowError("CatPred result needs the persisted sequence-SMILES handoff; prepare the step first")
    result, ids = {}, set()
    for pair in pairs:
        if not isinstance(pair, dict) or set(pair) != {"candidate_id", "sequence", "smiles"}:
            raise WorkflowError("Malformed CatPred handoff provenance")
        cid = identifier(pair["candidate_id"], "CatPred candidate_id")
        if not isinstance(pair["sequence"], str) or ":" in pair["sequence"]:
            raise WorkflowError("CatPred handoff provenance needs one protein sequence per candidate")
        validate_sequence(pair["sequence"])
        key = (pair["sequence"], _smiles(pair["smiles"]))
        if cid in ids or key in result:
            raise WorkflowError("Duplicate CatPred sequence-SMILES pairs cannot be assigned safely after IDs are dropped; deduplicate candidates or use separate approved jobs")
        ids.add(cid)
        result[key] = cid
    validate_data(pairs)
    return result


def write_input(path, pairs):
    _pair_index(pairs)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["seq_id", "sequences", "smiles"])
        writer.writeheader()
        writer.writerows({"seq_id": p["candidate_id"], "sequences": p["sequence"], "smiles": p["smiles"]} for p in pairs)


def inspect_output(path, pairs):
    expected = _pair_index(pairs)
    members = read_members(path)
    tables = [(name, content) for name, content in members.items() if name.lower().endswith(".csv")]
    if len(tables) != 1:
        raise WorkflowError("CatPred needs one authoritative output CSV; select its member explicitly")
    name, content = tables[0]
    rows = csv_rows(content)
    headers = {key.strip().lower(): key for key in rows[0]}
    if len(headers) != len(rows[0]):
        raise WorkflowError("CatPred output has duplicate case-insensitive headers")
    sequence_columns = [headers[key] for key in ("sequence", "sequences") if key in headers]
    if len(sequence_columns) != 1 or "smiles" not in headers:
        raise WorkflowError("CatPred output needs one Sequence/Sequences column and SMILES for verified candidate matching")
    missing = [key for key in RESULT_COLUMNS if key.lower() not in headers]
    if missing:
        raise WorkflowError("CatPred output is not the updated all-three prediction schema; missing columns: " + ", ".join(missing))
    entries, seen = [], set()
    for row in rows:
        sequence = row[sequence_columns[0]]
        smiles = row[headers["smiles"]]
        cid = expected.get((sequence, smiles))
        if cid is None:
            raise WorkflowError("CatPred output sequence/SMILES does not match the prepared request; no row-order or chemical-equivalence guess is allowed")
        if cid in seen:
            raise WorkflowError("CatPred output contains a duplicate sequence-SMILES result")
        seen.add(cid)
        for key in ("candidate_id", "seq_id", "sequence_id"):
            if key in headers and row[headers[key]] and row[headers[key]] != cid:
                raise WorkflowError("CatPred output identifier conflicts with its verified sequence-SMILES pair")
        if "status" in headers and row[headers["status"]].strip().lower() in {"failed", "error", "invalid"}:
            raise WorkflowError("CatPred output reports a failed prediction; incomplete results cannot complete the step")
        metrics = {"candidate_id": cid, "Sequence": sequence, "SMILES": smiles}
        for key in RESULT_COLUMNS:
            try:
                value = float(row[headers[key.lower()]])
            except (ValueError, OverflowError) as exc:
                raise WorkflowError(f"CatPred output {key} must contain a finite number") from exc
            if not math.isfinite(value) or ((key in MODES or "_SD_" in key) and value < 0):
                raise WorkflowError(f"CatPred output {key} must be finite and nonnegative (log10 values may be negative)")
            metrics[key] = value
        entries.append({"label": cid, "metrics": metrics, "member": name})
    if seen != set(expected.values()):
        raise WorkflowError("CatPred output is incomplete: not every prepared candidate has a prediction")
    validate_data(entries)
    return {"sha256": file_hash(path), "entries": entries, "members": members}
