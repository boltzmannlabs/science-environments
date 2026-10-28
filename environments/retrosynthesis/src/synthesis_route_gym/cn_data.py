"""Private measured C–N screening data and outcome-independent inner splits.

The selected publication is development data. Its internal assessment partition is
not a final benchmark seal. CAD response is not isolated reaction yield.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold

from .chemistry import canonical_smiles
from .cn_model import CN_ROLES, cn_domain_matches

SOURCE = "JNJ HTE 2024"
SOURCE_VERSION = "BH_HTE_Curated_Dataset_v20260219"
ENDPOINT = "reported_source_response_greater_than_or_equal_to_10"
SPLIT_SEED = 20261027
MEASUREMENT = "source_reported_CAD_response_not_isolated_yield; values may exceed 100"
ROLE_HEADERS = dict(zip(CN_ROLES, (
    "Aryl SMILES", "Amine SMILES", "Catalyst SMILES", "Base SMILES",
    "Solvent SMILES", "Product SMILES",
)))
ADDITIVE_HEADERS = (
    "Additive_present", "Additive_aromatic_rings", "Additive_heteroatom_count",
    "Additive_coordination_flag", "Additive_steric_bulk_flag", "Additive_pi_rich_flag",
    "Additive_Pd_poisoning", "Additive_competes_with_amine",
)
SOURCE_HEADERS = (
    "", "Source", "Aryl SMILES", "Amine SMILES", "Catalyst Name", "Catalyst SMILES",
    "Base SMILES", "Base Name", "Solvent Name", "Solvent SMILES", "Product SMILES",
    "DRFP", "DRFP_subst_prod", "QM", "Yield", "labels",
    *(field for i in range(10) for field in (f"iteration_{i} cluster", f"iteration_{i} train_test")),
    *ADDITIVE_HEADERS,
)
PUBLIC_FIELDS = ("record_id", "group_id", *CN_ROLES)


def _hash(value) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=32768)
def _canonical(value: str) -> str:
    with rdBase.BlockLogs():
        return canonical_smiles(value)


@lru_cache(maxsize=8192)
def _group_id(product: str) -> str:
    mol = Chem.MolFromSmiles(product)
    Chem.RemoveStereochemistry(mol)
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    representation = Chem.MolToSmiles(scaffold if scaffold.GetNumAtoms() else mol,
                                      canonical=True, isomericSmiles=False)
    return "cn-group-" + _hash(representation)


def _outcome(row: dict) -> tuple[float, int]:
    try:
        response, label = float(row["Yield"]), float(row["labels"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid measured response or label in selected source") from exc
    if not math.isfinite(response) or response < 0:
        raise ValueError("Selected source requires finite nonnegative measured responses")
    if label not in (0, 1) or int(label) != int(response >= 10):
        raise ValueError("Selected source label is inconsistent with the audited >=10 endpoint")
    return response, int(label)


def _inputs(row: dict) -> tuple[dict | None, str | None]:
    values = {role: row[header] for role, header in ROLE_HEADERS.items()}
    missing = {"", "nan", "none", "null", "na", "n/a"}
    if any(not isinstance(v, str) or v.strip().lower() in missing for v in values.values()):
        return None, "missing_structure"
    try:
        canonical = {role: _canonical(value) for role, value in values.items()}
    except ValueError:
        return None, "invalid_structure"
    try:
        known_no_additive = all(float(row[key]) == 0 for key in ADDITIVE_HEADERS)
    except (TypeError, ValueError):
        known_no_additive = False
    if not known_no_additive:
        return None, "unknown_additive_composition"
    with rdBase.BlockLogs():
        if not cn_domain_matches(canonical):
            return None, "outside_cn_domain"
    return canonical, None


def _read_source(path, expected_sha256: str):
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("A lowercase SHA256 digest is required")
    with Path(path).open("rb") as handle:
        raw = handle.read(64 * 1024 * 1024 + 1)
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError("Source exceeds the 64 MiB input limit")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("Source digest mismatch")
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
        if tuple(reader.fieldnames or ()) != SOURCE_HEADERS:
            raise ValueError("Source schema does not match the pinned CSV contract")
    except UnicodeError as exc:
        raise ValueError("Source must be UTF-8 CSV") from exc
    return reader


def load_cn_records(path, expected_sha256: str) -> tuple[tuple[dict, ...], dict]:
    """Verify and load only JnJ rows; never silently filter invalid outcomes.

    Identity, exclusions, first-replicate retention and groups use inputs only.
    Audit output contains no individual outcomes or split hit prevalence.
    """
    records, seen = [], set()
    source_counts, exclusions = Counter(), Counter()
    selected = duplicates = above_100 = 0
    for source_index, row in enumerate(_read_source(path, expected_sha256)):
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Malformed CSV row does not match source schema")
        source_counts.update((row["Source"],))
        if row["Source"] != SOURCE:
            continue
        selected += 1
        response, label = _outcome(row)
        above_100 += int(response > 100)
        roles, exclusion = _inputs(row)
        if exclusion:
            exclusions.update((exclusion,))
            continue
        identity = tuple(roles[role] for role in CN_ROLES)
        if identity in seen:
            duplicates += 1
            continue
        seen.add(identity)
        records.append({"record_id": "cn-" + _hash([SOURCE_VERSION, SOURCE, identity]),
                        "source_index": source_index, **roles,
                        "label": label, "reported_response": response,
                        "group_id": _group_id(roles["product"])})
    if not selected:
        raise ValueError("Selected source is absent")
    audit = {
        "source": SOURCE, "source_version": SOURCE_VERSION, "sha256": expected_sha256,
        "source_counts": dict(source_counts), "selected_source_records": selected,
        "retained_records": len(records), "replicate_records_removed": duplicates,
        "input_exclusions": dict(exclusions), "responses_above_100": above_100,
        "group_count": len({record["group_id"] for record in records}),
        "endpoint": ENDPOINT, "measurement": MEASUREMENT,
        "data_role": "global_development", "additive_scope": "all eight source flags zero",
        "split_seed": SPLIT_SEED,
    }
    return tuple(records), audit


def public_cn_records(records) -> tuple[dict, ...]:
    """Copy an explicit outcome-free input allowlist for agent/model candidates."""
    return tuple({key: record[key] for key in PUBLIC_FIELDS} for record in records)


def frozen_split(records) -> dict[str, list[int]]:
    """Assign whole nonchiral product-scaffold groups to a fixed internal split."""
    ids = [record["record_id"] for record in records]
    groups = [record["group_id"] for record in records]
    if any(not isinstance(v, str) or not v for v in (*ids, *groups)):
        raise ValueError("Nonempty record and group identifiers are required")
    if len(set(ids)) != len(ids):
        raise ValueError("Record identifiers must be unique")
    product_groups = {}
    for record in records:
        chemical_group = _group_id(_canonical(record["product"]))
        previous = product_groups.get(chemical_group, record["group_id"])
        if previous != record["group_id"]:
            raise ValueError("A product scaffold cannot belong to contradictory groups")
        product_groups[chemical_group] = record["group_id"]
    ordered = sorted(set(groups), key=lambda group: _hash([SPLIT_SEED, group]))
    if len(ordered) < 20:
        raise ValueError("At least 20 independent product scaffold groups are required")
    n = len(ordered)
    boundaries = (0, int(n * .60), int(n * .60) + int(n * .15),
                  int(n * .60) + int(n * .15) + int(n * .10), n)
    names = ("train", "development", "calibration", "assessment")
    group_split = {group: name for name, lo, hi in zip(names, boundaries, boundaries[1:])
                   for group in ordered[lo:hi]}
    return {name: [index for index, group in enumerate(groups) if group_split[group] == name]
            for name in names}
