"""Private measured-condition loader and outcome-free public projection.

This adapter is for the Perera Suzuki screen, not the Doyle C–N predictor.
Loading validates syntax and source-field consistency, not chemical feasibility.
"""
from collections import Counter
from copy import deepcopy
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping, Sequence

from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

from .chemistry import canonical_smiles

SOURCE_ID = "gauche_suzuki_miyaura"
SOURCE_REVISION = "2bf761afb3b2cc7ba2bfc55dc98fec76a4d102bb"
SOURCE_URL = (
    "https://raw.githubusercontent.com/leojklarner/gauche/"
    f"{SOURCE_REVISION}/gauche/datasets/reactions/SuzukiMiyaura.csv"
)
_ROLE_COLUMNS = (
    ("catalyst", "catalyst_smiles", True),
    ("ligand", "ligand_smiles", False),
    ("reagent_1", "reagent_1_smiles", False),
    ("solvent_1", "solvent_1_smiles", True),
)
_COLUMNS = (
    "reactant_1_smiles", "reactant_2_smiles", "catalyst_smiles",
    "ligand_smiles", "reagent_1_smiles", "solvent_1_smiles", "rxn", "yield",
)
_PUBLIC_FIELDS = (
    "record_id", "target", "reactants", "conditions", "source_family",
    "doyle_predictor_applicability", "source_input_roles",
    "unspecified_condition_roles", "missingness_scope",
)


def condition_source_metadata(source_id: str) -> dict:
    """Return source facts; the repository license is not a data-rights warranty."""
    if source_id != SOURCE_ID:
        raise ValueError("Unsupported condition-data source")
    return {
        "source_id": SOURCE_ID,
        "source_family": "doi:10.1126/science.aap9112",
        "publication_url": "https://doi.org/10.1126/science.aap9112",
        "source_revision": SOURCE_REVISION,
        "source_url": SOURCE_URL,
        "repository_license": "MIT",
        "original_dataset_redistribution_terms": "not_independently_established",
        "upstream_sha256": "0595c7956128cb3b4998c543204a3650c57d0432d6871c3f7195cf532d8b3172",
        "local_crlf_sha256": "1908fc8ea3e5d8103c1d4cf40377a7554fe6bb1df568aa7352c2e1d13fd7153a",
        "doyle_predictor_applicability": "outside_model_domain",
        "recommended_partition": "whole_publication_reserved_condition_final",
    }


def _structure(value: str, row_number: int, field: str) -> str:
    try:
        return canonical_smiles(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f"Invalid input structure at data row {row_number}, field {field}") from error


def _fragments(value: str) -> list[str]:
    # Canonicalize each fragment independently: salts/standards are not discarded.
    return [canonical_smiles(fragment) for fragment in value.split(".") if fragment]


def _outcome(value, row_number: int) -> float:
    try:
        number = float(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid outcome at data row {row_number}") from None
    if not math.isfinite(number) or not 0 <= number <= 100:
        raise ValueError(f"Invalid outcome percentage at data row {row_number}")
    return number


def _record(row: Mapping, row_number: int, metadata: Mapping) -> dict:
    reactants = [fragment for column in _COLUMNS[:2]
                 for fragment in _fragments(_structure(row[column], row_number, column))]
    conditions = {
        role: _structure(row[column], row_number, column)
        for role, column, required in _ROLE_COLUMNS if required or row[column].strip()
    }
    parts = row["rxn"].split(">")
    if len(parts) != 3:
        raise ValueError(f"Invalid reaction input at data row {row_number}")
    target = _structure(parts[2], row_number, "rxn product")
    if len(_fragments(target)) != 1:
        raise ValueError(f"Ambiguous multi-product reaction at data row {row_number}")
    reported = reactants + [item for value in conditions.values() for item in _fragments(value)]
    try:
        reaction_inputs = _fragments(parts[0]) + _fragments(parts[1])
    except ValueError as error:
        raise ValueError(f"Invalid reaction input at data row {row_number}") from error
    if Counter(reported) != Counter(reaction_inputs):
        raise ValueError(f"Reaction input fields disagree at data row {row_number}")
    identity = json.dumps([SOURCE_ID, row_number, target, reactants, conditions], sort_keys=True)
    return {
        "record_id": SOURCE_ID + ":" + hashlib.sha256(identity.encode()).hexdigest()[:24],
        "target": target, "reactants": reactants, "conditions": conditions,
        "outcome_yield_percent": _outcome(row["yield"], row_number),
        "source_family": metadata["source_family"],
        "source_locator": f"{metadata['source_url']}#data-row={row_number}",
        "doyle_predictor_applicability": "outside_model_domain",
        "source_input_roles": "reported_input_fields_not_atom_contribution_assignment",
        "unspecified_condition_roles": [role for role, _, _ in _ROLE_COLUMNS if role not in conditions],
        "missingness_scope": "empty_source_cell_does_not_distinguish_absent_from_unreported",
    }


def load_condition_records(path: str | Path, source_id: str) -> list[dict]:
    """Load private labels. Source attribution is caller-supplied, not attested.

    Callers must compare file hashes against ``condition_source_metadata`` for
    provenance attestation; custom fixtures/subsets can use the same adapter.
    Never give the returned private records to a candidate-generating agent.
    """
    metadata = condition_source_metadata(source_id)
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or set(reader.fieldnames) != set(_COLUMNS) or len(reader.fieldnames) != len(_COLUMNS):
            raise ValueError("Condition dataset columns do not match the declared source schema")
        records = []
        for number, row in enumerate(reader, start=1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Malformed dataset columns at data row {number}")
            records.append(_record(row, number, metadata))
    if not records:
        raise ValueError("Condition dataset is empty")
    return records


def public_condition_records(records: Sequence[Mapping]) -> list[dict]:
    """Drop outcomes, exact source-row lookups and unrecognized fields.

    This projection is not a network/filesystem access-control boundary.
    """
    return [{key: deepcopy(record[key]) for key in _PUBLIC_FIELDS if key in record}
            for record in records]


def summarize_condition_records(records: Sequence[Mapping]) -> dict:
    """Eligibility/group counts only: no yield values or condition rankings."""
    if not records:
        raise ValueError("A nonempty collection of condition records is required")
    targets = {canonical_smiles(record["target"]) for record in records}
    scaffolds = {
        MurckoScaffold.MurckoScaffoldSmiles(mol=Chem.MolFromSmiles(target), includeChirality=True)
        for target in targets
    }
    families = Counter(record["source_family"] for record in records)
    identities = {
        json.dumps([record["target"], sorted(record["reactants"]), record["conditions"]], sort_keys=True)
        for record in records
    }
    valid = 0
    for record in records:
        try:
            _outcome(record.get("outcome_yield_percent"), 0)
            valid += 1
        except ValueError:
            pass
    return {
        "record_count": len(records), "target_count": len(targets),
        "product_scaffold_count": len(scaffolds), "source_family_count": len(families),
        "source_family_record_counts": dict(sorted(families.items())),
        "source_group_inference_supported": False,
        "inference_scope": "counts_only_no_inferential_analysis",
        "duplicate_chemical_record_count": len(records) - len(identities),
        "unspecified_condition_role_counts": dict(Counter(
            role for record in records for role in record.get("unspecified_condition_roles", [])
        )),
        "outcome_validity": {"valid_percent_count": valid, "invalid_percent_count": len(records) - valid},
    }
