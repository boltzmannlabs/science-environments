"""Outcome-blind, connected-group allocation for versioned benchmark cohorts.

Only documented relations are audited. Scaffold grouping is not a guarantee that
all chemical analogues or unresolved patent families have been identified.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from functools import lru_cache
import json
from typing import Iterable, Mapping

from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

from .chemistry import canonical_smiles

PARTITIONS = frozenset({"smoke", "development", "sealed_final", "unused", "excluded"})
SELECTABLE = PARTITIONS - {"unused", "excluded"}
GROUPING_VERSION = "source-reaction-target-murcko-v1"


def _hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=100000)
def chemical_keys(target: str) -> tuple[str, str | None]:
    """Coarse target identity and nonchiral Murcko scaffold; acyclic is explicit."""
    canonical = canonical_smiles(target)
    molecule = Chem.MolFromSmiles(canonical)
    identity = Chem.MolToSmiles(molecule, isomericSmiles=False)
    scaffold = MurckoScaffold.MurckoScaffoldSmiles(mol=molecule, includeChirality=False)
    return identity, scaffold or None


def _string_keys(record: Mapping, field: str) -> tuple[str, ...]:
    values = record.get(field, ())
    if not isinstance(values, (list, tuple)) or any(not isinstance(x, str) or not x for x in values):
        raise ValueError(f"{field} must contain nonempty string keys")
    return tuple(sorted(set(values)))


def record_keys(record: Mapping) -> tuple[tuple[str, str], ...]:
    target, scaffold = chemical_keys(record["target"])
    sources = _string_keys(record, "source_keys")
    if not sources:
        # Missing sources cannot silently become independent observations.
        sources = ("unknown:" + str(record.get("source_id", "unspecified")),)
    return tuple(sorted({("target", target), ("molecule", target),
                         *((("scaffold", scaffold),) if scaffold else ()),
                         *(("source", key) for key in sources),
                         *(("reaction", key) for key in _string_keys(record, "reaction_keys")),
                         *(("molecule", chemical_keys(key)[0]) for key in _string_keys(record, "molecule_keys")),
                         *((("route", record["route_fingerprint"]),) if record.get("route_fingerprint") else ())}))


def _records(records: Iterable[Mapping]) -> tuple[Mapping, ...]:
    result = tuple(sorted(records, key=lambda r: str(r.get("record_id", ""))))
    identifiers = [r.get("record_id") for r in result]
    if any(not isinstance(x, str) or not x for x in identifiers):
        raise ValueError("Records require nonempty record_id")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Duplicate record_id")
    return result


def leakage_components(records: Iterable[Mapping]) -> dict:
    """Link all known relations before sampling; caller records remain unchanged."""
    rows = _records(records)
    parents = {r["record_id"]: r["record_id"] for r in rows}
    first: dict[tuple[str, str], str] = {}
    links = []

    def root(key):
        while parents[key] != key:
            key = parents[key]
        return key

    for row in rows:
        identity = row["record_id"]
        for kind, key in record_keys(row):
            other = first.get((kind, key))
            if other is None:
                first[(kind, key)] = identity
                continue
            left, right = root(identity), root(other)
            if left != right:
                parents[max(left, right)] = min(left, right)
            links.append({"left": other, "right": identity, "kind": kind, "key_sha256": _hash(key)})
    groups: dict[str, list[str]] = defaultdict(list)
    for identity in parents:
        groups[root(identity)].append(identity)
    components = [{"group_id": "g-" + _hash(sorted(ids))[:24], "record_ids": sorted(ids)}
                  for ids in groups.values()]
    return {"version": GROUPING_VERSION, "groups": sorted(components, key=lambda g: g["group_id"]),
            "links": links, "record_count": len(rows)}


def _check_quotas(quotas: Mapping[str, int]) -> None:
    if not quotas or not set(quotas) <= SELECTABLE:
        raise ValueError("Quotas require known selectable partitions")
    if any(type(n) is not int or n < 0 for n in quotas.values()) or sum(quotas.values()) == 0:
        raise ValueError("Quotas must be nonnegative integers with a positive total")


def select_grouped_records(
    records: Iterable[Mapping], quotas: Mapping[str, int], *, seed: str,
    excluded_record_ids: Iterable[str] = (),
) -> dict:
    """Select one representative per component without reading outcomes or scores."""
    _check_quotas(quotas)
    if not isinstance(seed, str) or not seed:
        raise ValueError("An explicit nonempty allocation seed is required")
    rows = _records(records)
    components = leakage_components(rows)
    excluded = frozenset(excluded_record_ids)
    if not excluded <= {r["record_id"] for r in rows}:
        raise ValueError("Unknown excluded record IDs")
    eligible = [g for g in components["groups"] if not excluded.intersection(g["record_ids"])]
    if len(eligible) < sum(quotas.values()):
        raise ValueError(f"Only {len(eligible)} eligible connected groups for {sum(quotas.values())} requested tasks")
    ordered = sorted(eligible, key=lambda g: _hash([seed, g["group_id"]]))
    slots = [part for part in ("smoke", "development", "sealed_final") for _ in range(quotas.get(part, 0))]
    chosen = {g["group_id"]: (part, min(g["record_ids"], key=lambda x: _hash([seed, x])))
              for g, part in zip(ordered, slots)}
    assignment = _assign_groups(components["groups"], chosen, excluded)
    by_id = {row["record_id"]: row for row in rows}
    selected = [{**by_id[a["record_id"]], "partition": a["partition"], "group_id": a["group_id"]}
                for a in assignment if a["selected"]]
    audit = audit_assignments(rows, assignment, components=components)
    return {"selected": selected, "assignments": assignment, "links": components["links"],
            "audit": {**audit, "seed": seed, "requested": dict(quotas),
                      "excluded_groups": len(components["groups"]) - len(eligible),
                      "grouping_version": GROUPING_VERSION}}


def _assign_groups(groups, chosen, excluded):
    assignments = []
    for group in groups:
        default = "excluded" if excluded.intersection(group["record_ids"]) else "unused"
        partition, selected_id = chosen.get(group["group_id"], (default, None))
        assignments.extend({"record_id": identity, "group_id": group["group_id"],
                            "partition": partition, "selected": identity == selected_id}
                           for identity in group["record_ids"])
    return sorted(assignments, key=lambda a: a["record_id"])


def audit_assignments(records, assignments, *, components=None) -> dict:
    """Fail on a cross-partition link, even through records not selected as tasks."""
    rows = _records(records)
    expected = {r["record_id"] for r in rows}
    by_id = {a["record_id"]: a for a in assignments}
    if len(by_id) != len(assignments) or set(by_id) != expected:
        raise ValueError("Assignments must cover every unique record exactly once")
    if any(a.get("partition") not in PARTITIONS for a in assignments):
        raise ValueError("Unknown partition")
    components = components or leakage_components(rows)
    for group in components["groups"]:
        partitions = {by_id[i]["partition"] for i in group["record_ids"]} & SELECTABLE
        if len(partitions) > 1:
            raise ValueError("Detected cross-partition connected-group leakage")
    return {"records": len(rows), "connected_groups": len(components["groups"]),
            "cross_partition_groups": 0,
            "selected_tasks": sum(bool(a.get("selected")) for a in assignments),
            "limitations": ["Unresolved patent-family relationships are not certified disjoint",
                            "Murcko grouping is not exhaustive analogue detection",
                            "Checkpoint training overlap requires a separate audit"]}
