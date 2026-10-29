"""Local benchmark bundles with explicit public/private data boundaries.

The model-facing interface is load_public_task; it exposes no label-read action.
Private scoring is a host operation after decision commitment. File permissions
and path checks protect ordinary local use, not an adversarial process running
as the same Unix user. Callers must isolate runtime mounts/identities themselves
if they require OS-enforced confidentiality. A trusted manifest hash can anchor
integrity; unanchored hashes do not authenticate a maliciously rewritten bundle.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator

from .chemistry import canonical_smiles
from .schemas import Budget, Constraints, InventoryItem, Record, RouteCandidate, Smiles, Task
from .validation import assess_route

SCHEMA_VERSION = "1.0"
SCORE_SCOPE = "retrospective_reference_comparison_not_new_experimental_validation"
ROLES = frozenset({"aryl halide", "ligand", "additive", "base", "catalyst", "solvent", "reagent", "reagent_1", "solvent_1"})
HASH = re.compile(r"^[a-f0-9]{64}$")
MAX_FILE_BYTES = 100_000_000


def _identifier(value):
    if (not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value)
            or ".." in value):
        raise ValueError("Invalid task or candidate identifier")
    return value


def _digest(value):
    if not isinstance(value, str) or not HASH.fullmatch(value):
        raise ValueError("Expected a lowercase SHA-256 digest")
    return value


def _json_bytes(value):
    try:
        return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("Data must contain finite, acyclic JSON values") from exc


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _json_load(data):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON object keys")
            result = {**result, key: value}
        return result
    try:
        return json.loads(data, object_pairs_hook=unique_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON value")))
    except (TypeError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("Malformed JSON document") from exc


class _Candidate(Record):
    candidate_id: str
    reactants: Annotated[tuple[Smiles, ...], Field(min_length=1, max_length=100)]
    conditions: dict[str, Smiles]

    _id = field_validator("candidate_id")(_identifier)

    @field_validator("conditions")
    @classmethod
    def allowed_roles(cls, value):
        if not value or not set(value) <= ROLES:
            raise ValueError("Conditions require supported SMILES-valued chemical roles")
        return value


class _PublicTask(Record):
    task_id: str
    track: Literal["reference_route", "measured_conditions"]
    partition: Literal["smoke", "development", "sealed_final"]
    target: Smiles
    candidates: Annotated[tuple[_Candidate, ...], Field(max_length=10000)] | None = None
    inventory_exclusions: tuple[Smiles, ...] = ()
    constraints: Constraints = Field(default_factory=Constraints)
    budget: Budget = Field(default_factory=Budget)

    _id = field_validator("task_id")(_identifier)

    @model_validator(mode="after")
    def track_fields(self):
        if self.track == "measured_conditions" and not self.candidates:
            raise ValueError("Measured-condition tasks require public candidates")
        if self.track == "reference_route" and self.candidates is not None:
            raise ValueError("Reference-route tasks cannot disclose candidate reference paths")
        ids = [row.candidate_id for row in self.candidates or ()]
        if len(ids) != len(set(ids)):
            raise ValueError("Candidate identifiers must be unique")
        if len(set(self.inventory_exclusions)) != len(self.inventory_exclusions):
            raise ValueError("Inventory exclusions must be unique")
        return self


class _Source(Record):
    source_id: str
    url: Annotated[str, Field(min_length=1, max_length=2000)]
    sha256: str
    license: Annotated[str, Field(min_length=1, max_length=200)]

    _id = field_validator("source_id")(_identifier)
    _hash = field_validator("sha256")(_digest)

    @field_validator("url")
    @classmethod
    def public_url(cls, value):
        parsed = urlsplit(value)
        if (parsed.scheme not in {"https", "http"} or not parsed.hostname
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or any(ord(char) < 33 for char in value)):
            raise ValueError("Source URLs must be public credential-free URLs without query parameters")
        return value


class _Provenance(Record):
    sources: Annotated[tuple[_Source, ...], Field(min_length=1, max_length=1000)]
    baseline_protocol_sha256: str | None = None
    baseline_manifest_sha256: str | None = None
    inventory_sha256: str | None = None
    protocol_id: str | None = None

    @field_validator("baseline_protocol_sha256", "baseline_manifest_sha256", "inventory_sha256")
    @classmethod
    def optional_hash(cls, value):
        return None if value is None else _digest(value)

    @field_validator("protocol_id")
    @classmethod
    def optional_id(cls, value):
        return None if value is None else _identifier(value)

    @model_validator(mode="after")
    def unique_sources(self):
        if len({source.source_id for source in self.sources}) != len(self.sources):
            raise ValueError("Source IDs must be unique")
        return self


def _path(path):
    path = Path(os.path.abspath(os.fspath(path)))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("Symlink paths are not allowed")
    return path


def _read(path):
    path = _path(path)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        with os.fdopen(os.open(path, flags), "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise ValueError("Bundle inputs must be regular files")
            data = handle.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("Bundle file exceeds the local size limit")
        return data
    except OSError as exc:
        raise ValueError("Required bundle file is missing or unreadable") from exc


def _write(path, data, private=False):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        with os.fdopen(os.open(_path(path), flags, 0o600 if private else 0o644), "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise ValueError("Write-once output already exists") from exc


def _labels(tasks, values):
    if not isinstance(values, list) or any(not isinstance(row, dict) for row in values):
        raise ValueError("Private labels must be records")
    result = {}
    for row in values:
        copied = _json_load(_json_bytes(row))
        task_id = _identifier(copied.get("task_id"))
        if task_id in result:
            raise ValueError("Duplicate private task labels")
        result = {**result, task_id: copied}
    if set(result) != {task.task_id for task in tasks}:
        raise ValueError("Exactly one private label record is required per task")
    for task in tasks:
        label = result[task.task_id]
        if task.track == "reference_route":
            route = RouteCandidate.model_validate(label.get("reference_route"))
            if route.target != task.target or "outcomes" in label:
                raise ValueError("Reference route does not match its public task")
            if "reference_inventory_closed" in label and type(label["reference_inventory_closed"]) is not bool:
                raise ValueError("Reference inventory closure must be an explicit boolean")
        else:
            outcomes = label.get("outcomes")
            ids = {candidate.candidate_id for candidate in task.candidates}
            if not isinstance(outcomes, dict) or set(outcomes) != ids or "reference_route" in label:
                raise ValueError("Measured labels must cover exactly the public candidates")
            if any(type(v) not in (float, int) or not math.isfinite(v) or not 0 <= v <= 100 for v in outcomes.values()):
                raise ValueError("Measured outcomes must be finite yield percentages in [0, 100]")
    return result


def _prepare(tasks, labels, provenance, inventory, assignments):
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("A bundle requires a nonempty public task list")
    normalized = tuple(_PublicTask.model_validate(task) for task in tasks)
    if len({task.task_id for task in normalized}) != len(normalized):
        raise ValueError("Task identifiers must be unique")
    if not isinstance(inventory, list) or any(not isinstance(s, str) for s in inventory):
        raise ValueError("Shared inventory must be a list of molecular identities")
    stock = tuple(sorted(set(canonical_smiles(smiles) for smiles in inventory)))
    if any(not set(task.inventory_exclusions) <= set(stock) for task in normalized):
        raise ValueError("Inventory exclusions must be a subset of shared stock")
    source = _Provenance.model_validate(provenance).model_dump(mode="json", exclude_none=True)
    private_labels = _labels(normalized, labels)
    if not isinstance(assignments, list) or any(not isinstance(row, dict) for row in assignments):
        raise ValueError("Private assignments must be a list of records")
    assignments = _json_load(_json_bytes(assignments))
    task_ids = {task.task_id for task in normalized}
    if any("task_id" in row and row["task_id"] not in task_ids for row in assignments):
        raise ValueError("Private assignment references an unknown task")
    if any("task_id" not in row and (not isinstance(row.get("record_id"), str)
                                    or not 1 <= len(row["record_id"].strip()) <= 1000) for row in assignments):
        raise ValueError("Private record assignment requires a nonempty record_id")
    public_files = {"inventory.json": _json_bytes(list(stock)), "provenance.json": _json_bytes(source),
                    **{f"tasks/{task.task_id}.json": _json_bytes(task.model_dump(mode="json", exclude_none=True))
                       for task in normalized}}
    private_files = {"assignments.json": _json_bytes(assignments),
                     **{f"labels/{key}.json": _json_bytes(value) for key, value in private_labels.items()}}
    records = [{"task_id": task.task_id, "track": task.track, "partition": task.partition} for task in normalized]
    return public_files, private_files, records


def build_bundle(public_dir: Path, private_dir: Path, *, tasks: list[dict], labels: list[dict],
                 provenance: dict, inventory: list[str], assignments: list[dict]) -> dict:
    """Write separate, immutable-by-contract inputs and host-only answer records.

    Shared stock is provided upstream; reference leaves never determine it here.
    Public bytes and observations depend only on public arguments, never labels.
    All validation completes before creating either output directory. The return
    value is a host-only receipt: retain both manifest hashes outside agent access.
    """
    public, private = _path(public_dir), _path(private_dir)
    if public == private or public in private.parents or private in public.parents:
        raise ValueError("Public and private directories must be disjoint")
    if public.exists() or private.exists():
        raise ValueError("Write-once bundle directories must not already exist")
    public_files, private_files, records = _prepare(tasks, labels, provenance, inventory, assignments)
    public_manifest = {"schema_version": SCHEMA_VERSION, "bundle_kind": "public", "tasks": records,
                       "files": {name: _hash(data) for name, data in public_files.items()}}
    public_data = _json_bytes(public_manifest)
    private_manifest = {"schema_version": SCHEMA_VERSION, "bundle_kind": "private",
                        "public_manifest_sha256": _hash(public_data),
                        "files": {name: _hash(data) for name, data in private_files.items()}}
    private_data = _json_bytes(private_manifest)
    created = ()
    try:
        for folder, files, manifest, confidential in (
                (public, public_files, public_data, False),
                (private, private_files, private_data, True)):
            folder.mkdir(mode=0o700 if confidential else 0o755)
            created += (folder,)
            (folder / ("labels" if confidential else "tasks")).mkdir(mode=0o700 if confidential else 0o755)
            for name, data in files.items():
                _write(folder / name, data, confidential)
            _write(folder / "manifest.json", manifest, confidential)
    except Exception:
        for folder in reversed(created):
            shutil.rmtree(folder)
        raise
    return {"schema_version": SCHEMA_VERSION, "task_count": len(records),
            "public_manifest_sha256": _hash(public_data), "private_manifest_sha256": _hash(private_data),
            "status": "created",
            "access_boundary": "public_loader_only; private_scoring_is_a_trusted_host_operation"}


def _manifest_names(kind, records):
    if kind == "public":
        return {"inventory.json", "provenance.json", *(f"tasks/{row['task_id']}.json" for row in records)}
    return {"assignments.json", *(f"labels/{row['task_id']}.json" for row in records)}


def _verify_tree(folder, kind, records=None, expected_hash=None):
    folder = _path(folder)
    data = _read(folder / "manifest.json")
    if expected_hash is not None and _hash(data) != _digest(expected_hash):
        raise ValueError("Bundle manifest hash mismatch")
    manifest = _json_load(data)
    expected_keys = {"schema_version", "bundle_kind", "files", "tasks" if kind == "public" else "public_manifest_sha256"}
    if (not isinstance(manifest, dict) or set(manifest) != expected_keys
            or manifest.get("schema_version") != SCHEMA_VERSION or manifest.get("bundle_kind") != kind):
        raise ValueError("Invalid bundle manifest")
    if kind == "public":
        records = manifest["tasks"]
        if not isinstance(records, list) or not records:
            raise ValueError("Manifest requires public task records")
        for record in records:
            if not isinstance(record, dict) or set(record) != {"task_id", "track", "partition"}:
                raise ValueError("Invalid manifest task metadata")
            _identifier(record["task_id"])
            if record["track"] not in {"reference_route", "measured_conditions"} or record["partition"] not in {"smoke", "development", "sealed_final"}:
                raise ValueError("Invalid task track or partition")
        if len({record["task_id"] for record in records}) != len(records):
            raise ValueError("Duplicate manifest task IDs")
    files = manifest["files"]
    if not isinstance(files, dict) or set(files) != _manifest_names(kind, records):
        raise ValueError("Manifest contains unexpected or missing files")
    allowed_dirs = {"tasks" if kind == "public" else "labels"}
    actual_files, actual_dirs = set(), set()
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlink bundle entries are forbidden")
        if path.is_dir():
            actual_dirs.add(path.relative_to(folder).as_posix())
        elif path.is_file():
            actual_files.add(path.relative_to(folder).as_posix())
        else:
            raise ValueError("Nonregular bundle entries are forbidden")
        if kind == "private" and path.stat().st_mode & 0o777 != (0o700 if path.is_dir() else 0o600):
            raise ValueError("Private bundle permissions must remain restrictive")
    if actual_files != {*files, "manifest.json"} or actual_dirs != allowed_dirs:
        raise ValueError("Bundle files are missing or unexpected files are present")
    if kind == "private" and folder.stat().st_mode & 0o777 != 0o700:
        raise ValueError("Private directory permissions must be 0700")
    for name, expected in files.items():
        if _hash(_read(folder / name)) != _digest(expected):
            raise ValueError("Bundle file hash mismatch")
    return manifest, _hash(data)


def verify_bundle(public_dir: Path, private_dir: Path | None = None, *, expected_manifest_sha256=None,
                  expected_private_manifest_sha256=None) -> dict:
    """Verify exact file sets and hashes; private integrity is a host-only option."""
    if expected_private_manifest_sha256 is not None and private_dir is None:
        raise ValueError("A private manifest anchor requires the private bundle directory")
    public, public_hash = _verify_tree(public_dir, "public", expected_hash=expected_manifest_sha256)
    stock = _json_load(_read(Path(public_dir) / "inventory.json"))
    if not isinstance(stock, list) or stock != sorted(set(canonical_smiles(s) for s in stock)):
        raise ValueError("Shared inventory must contain unique canonical identities")
    _Provenance.model_validate(_json_load(_read(Path(public_dir) / "provenance.json")))
    for record in public["tasks"]:
        task = _PublicTask.model_validate(_json_load(_read(Path(public_dir) / "tasks" / f"{record['task_id']}.json")))
        if any(getattr(task, key) != record[key] for key in ("task_id", "track", "partition")):
            raise ValueError("Public task disagrees with manifest metadata")
        if not set(task.inventory_exclusions) <= set(stock):
            raise ValueError("Inventory exclusions exceed shared inventory")
    if private_dir is not None:
        private, _ = _verify_tree(private_dir, "private", public["tasks"], expected_hash=expected_private_manifest_sha256)
        if private["public_manifest_sha256"] != public_hash:
            raise ValueError("Private labels belong to a different public bundle")
    return {"verified": True, "public_manifest_sha256": public_hash,
            "private_integrity_checked": private_dir is not None, "task_count": len(public["tasks"])}


def load_public_task(public_dir: Path, task_id: str, *, expected_manifest_sha256=None) -> dict:
    """Load public data, optionally pinned to a separately retained manifest digest."""
    _identifier(task_id)
    verify_bundle(public_dir, expected_manifest_sha256=expected_manifest_sha256)
    folder = _path(public_dir)
    task = _PublicTask.model_validate(_json_load(_read(folder / "tasks" / f"{task_id}.json")))
    data = task.model_dump(mode="json", exclude_none=True)
    stock = _json_load(_read(folder / "inventory.json"))
    inventory = tuple(InventoryItem(smiles=s) for s in stock if s not in task.inventory_exclusions)
    if task.track == "reference_route":
        materialized = Task(task_id=task.task_id, target=task.target, inventory=inventory,
                            constraints=task.constraints, budget=task.budget)
        data = {**data, **materialized.model_dump(mode="json")}
    else:
        data = {**data, "inventory": [item.model_dump(mode="json") for item in inventory]}
    return data


def _decision(value):
    if not isinstance(value, dict) or not set(value) <= {"task_id", "routes", "selected_candidate_id"}:
        raise ValueError("Decision contains unsupported fields")
    _identifier(value.get("task_id"))
    if ("routes" in value) == ("selected_candidate_id" in value):
        raise ValueError("Commit either routes or a selected candidate")
    if "selected_candidate_id" in value:
        _identifier(value["selected_candidate_id"])
        return dict(value)
    routes = value["routes"]
    if not isinstance(routes, list) or len(routes) > 100:
        raise ValueError("Decision routes must be a bounded list")
    normalized = [RouteCandidate.model_validate(route).model_dump(mode="json") for route in routes]
    if len({route["route_id"] for route in normalized}) != len(normalized):
        raise ValueError("Submitted route IDs must be unique")
    return {"task_id": value["task_id"], "routes": normalized}


def commit_decision(path: Path, decision: dict) -> str:
    """Write a decision once and return the SHA-256 of the committed bytes."""
    data = _json_bytes(_decision(decision))
    _write(path, data, private=True)
    return _hash(data)


def _core_signature(route):
    """Canonical, stereochemistry-preserving identity of target and reaction edges.

    This metric deliberately excludes condition, reagent, source and proposal
    metadata. It measures reference connectivity recovery, not full procedural
    reproduction or chemical feasibility. Repeated reactant identities do not
    manufacture distinct candidate routes.
    """
    parsed = RouteCandidate.model_validate(route)
    steps = tuple(sorted((step.product, tuple(sorted({use.smiles for use in step.reactants})))
                         for step in parsed.steps))
    return parsed.target, steps


def _score_reference(public, label, decision):
    task = Task.model_validate({key: public[key] for key in Task.model_fields if key in public})
    distinct = {}
    for route in decision["routes"]:
        core = _core_signature(route)
        if core not in distinct:
            distinct = {**distinct, core: route}
    selected = tuple(distinct.items())[:task.budget.top_k]
    reference = _core_signature(label["reference_route"])
    checks = []
    for core, route in selected:
        assessment = assess_route(task, RouteCandidate.model_validate(route)).model_dump(mode="json")
        recovered = core == reference and assessment["graph_valid"] and not assessment["acquisition_only"]
        qualified = (recovered and assessment["inventory_complete"] and assessment["constraint_compliant"]
                     and assessment["quantity_status"] in {"complete", "not_requested"})
        checks = [*checks, {**assessment, "reference_recovered": recovered,
                           "inventory_compliant_reference_recovered": qualified}]
    recovery = {"top1": checks[0]["reference_recovered"] if checks else False,
                "at_k": any(check["reference_recovered"] for check in checks)}
    qualified = {"top1": checks[0]["inventory_compliant_reference_recovered"] if checks else False,
                 "at_k": any(check["inventory_compliant_reference_recovered"] for check in checks)}
    return {"submitted_routes": len(decision["routes"]), "top_k": task.budget.top_k,
            "evaluated_unique_routes": len(selected), "duplicate_routes_ignored": len(decision["routes"]) - len(distinct),
            "reference_recovery": recovery, "inventory_compliant_reference_recovery": qualified,
            "reference_match_top1": recovery["top1"], "reference_match_at_k": recovery["at_k"],
            "reference_inventory_closed": label.get("reference_inventory_closed"), "route_checks": checks,
            "match_scope": "canonical_target_and_reaction_edges_ignoring_conditions_and_proposal_metadata",
            "inventory_scope": "shared_stock_identity_membership; no quantitative sufficiency claim when quantity_status is not_requested",
            "inventory_failure_interpretation": "Missing stock is a task constraint failure, not negative chemical evidence",
            "independent_chemical_review": "not_performed"}


def score_decision(public_dir: Path, private_dir: Path, decision_path: Path, expected_sha256: str,
                   *, expected_manifest_sha256=None, expected_private_manifest_sha256=None) -> dict:
    """Host-only smoke/development scoring; sealed-final evaluation is disabled.

    The expected decision digest must be retained independently by the caller.
    Neither the digest nor decision path is recovered from an agent-editable log.
    Real runs should also supply both independently retained manifest hashes.
    The public anchor prevents partition rewrites; the private anchor prevents
    rewritten labels from being accepted with a freshly rehashed private manifest.
    """
    raw = _read(decision_path)
    if _hash(raw) != _digest(expected_sha256):
        raise ValueError("Decision hash mismatch before private evaluation")
    decision = _decision(_json_load(raw))
    public = load_public_task(public_dir, decision["task_id"], expected_manifest_sha256=expected_manifest_sha256)
    if public["partition"] == "sealed_final":
        raise ValueError("sealed_final evaluation is unavailable until a separate final-seal implementation")
    if public["track"] == "measured_conditions":
        ids = {row["candidate_id"] for row in public["candidates"]}
        if decision.get("selected_candidate_id") not in ids:
            raise ValueError("Unknown or missing selected condition candidate")
    elif "routes" not in decision:
        raise ValueError("Reference task requires committed routes")
    verify_bundle(public_dir, private_dir, expected_manifest_sha256=expected_manifest_sha256,
                  expected_private_manifest_sha256=expected_private_manifest_sha256)
    label = _json_load(_read(_path(private_dir) / "labels" / f"{decision['task_id']}.json"))
    _labels((_PublicTask.model_validate({k: public[k] for k in _PublicTask.model_fields if k in public}),), [label])
    common = {"task_id": decision["task_id"], "track": public["track"], "partition": public["partition"],
              "decision_sha256": expected_sha256, "scope": SCORE_SCOPE}
    if public["track"] == "measured_conditions":
        observed = label["outcomes"][decision["selected_candidate_id"]]
        return {**common, "selected_candidate_id": decision["selected_candidate_id"],
                "selected_measured_yield_percent": observed,
                "simple_regret_percent": max(label["outcomes"].values()) - observed}
    return {**common, **_score_reference(public, label, decision)}
