"""Stream an available corpus audit; never infer checkpoint provenance from its name.

Public output contains counts and artifact hashes only. Reference membership and
publication-number keys belong exclusively in the separate private output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import time

from rdkit import Chem, rdBase

DOCUMENT = re.compile(r"^([A-Z]{2})(RE|PP|D|H)?(\d{5,})(?:[A-Z]\d?)?$")
REACTION_COLUMN = "reactants>reagents>production"


def publication_key(identifier):
    """Coarse publication number: kind-code omission is NOT family resolution."""
    if not isinstance(identifier, str):
        return None
    first = identifier.split(";", 1)[0].strip().upper()
    match = DOCUMENT.fullmatch(first)
    if not match:
        return None
    country, prefix, digits = match.groups()
    return country + (prefix or "") + (digits.lstrip("0") or "0")


def _molecule(value):
    with rdBase.BlockLogs():
        molecule = Chem.MolFromSmiles(value)
    if molecule is None or molecule.GetNumAtoms() == 0:
        raise ValueError("Invalid reaction structure")
    for atom in molecule.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=True)


def reaction_key(value, *, eligible_products=None):
    """Exact directed reactant/product edge; reagent field excluded explicitly.

An optional canonical-product screen avoids unnecessary reactant parsing. It
cannot exclude an exact match because product equality is required for a match.
"""
    if not isinstance(value, str) or len(value) > 100000:
        raise ValueError("Invalid reaction text")
    fields = value.split(">")
    if len(fields) != 3 or not fields[0] or not fields[2]:
        raise ValueError("Invalid reaction syntax")
    product = _molecule(fields[2])
    if eligible_products is not None and product not in eligible_products:
        return None
    reactants = sorted(_molecule(part) for part in fields[0].split("."))
    return ".".join(reactants) + ">>" + product


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _references(path):
    records = json.loads(Path(path).read_text())
    if not isinstance(records, list) or not records:
        raise ValueError("Invalid reference array")
    seen = set()
    for record in records:
        if (not isinstance(record, dict) or not isinstance(record.get("record_id"), str)
                or not record["record_id"]
                or any(not isinstance(record.get(key), list)
                       or any(not isinstance(item, str) or not item for item in record[key])
                       for key in ("source_documents", "reaction_keys"))
                or any(key.count(">>") != 1 for key in record["reaction_keys"])):
            raise ValueError("Invalid reference record")
        if record["record_id"] in seen:
            raise ValueError("Duplicate reference identifier")
        seen.add(record["record_id"])
    return records


def _stream(corpus, reference_documents, reference_reactions, reaction_seconds):
    products = {key.split(">>", 1)[1] for key in reference_reactions}
    deadline = time.monotonic() + reaction_seconds
    rows = attempted = malformed = unknown_documents = exact_rows = 0
    corpus_documents, matched_documents, matched_reactions = set(), set(), set()
    with Path(corpus).open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"id", REACTION_COLUMN} <= set(reader.fieldnames or []):
            raise ValueError("Corpus requires id and reaction columns")
        for row in reader:
            rows += 1
            document = publication_key(row.get("id"))
            if document is None:
                unknown_documents += 1
            else:
                corpus_documents.add(document)
                if document in reference_documents:
                    matched_documents.add(document)
            if time.monotonic() >= deadline:
                continue
            attempted += 1
            try:
                key = reaction_key(row.get(REACTION_COLUMN), eligible_products=products)
            except ValueError:
                malformed += 1
                continue
            if key in reference_reactions:
                matched_reactions.add(key)
                exact_rows += 1
    return {
        "rows": rows, "rows_attempted": attempted, "malformed_rows": malformed,
        "rows_unresolved_document": unknown_documents,
        "unique_publication_numbers": len(corpus_documents),
        "matched_publication_numbers": matched_documents,
        "matched_reaction_keys": matched_reactions, "exact_reaction_rows": exact_rows,
    }


def audit_overlap(reference_path, corpus_path, checkpoint_path, reaction_seconds=120):
    if (isinstance(reaction_seconds, bool) or not isinstance(reaction_seconds, (float, int))
            or not math.isfinite(reaction_seconds) or reaction_seconds < 0):
        raise ValueError("Invalid reaction audit time budget")
    started = time.monotonic()
    records = _references(reference_path)
    documents = {key for record in records for raw in record["source_documents"]
                 if (key := publication_key(raw)) is not None}
    reactions = {key for record in records for key in record["reaction_keys"]}
    scanned = _stream(corpus_path, documents, reactions, reaction_seconds)
    document_records = sorted(record["record_id"] for record in records
                              if any(publication_key(raw) in scanned["matched_publication_numbers"]
                                     for raw in record["source_documents"]))
    reaction_records = sorted(record["record_id"] for record in records
                              if set(record["reaction_keys"]) & scanned["matched_reaction_keys"])
    report = {
        "schema_version": "srg-available-corpus-overlap.v1",
        "scope": "entire_normalized_n1_reference_array_not_selected_final_cohort",
        "reference": {"sha256": sha256_file(reference_path), "records": len(records),
                      "unique_publication_numbers": len(documents), "unique_reaction_keys": len(reactions)},
        "corpus": {"name": Path(corpus_path).name, "sha256": sha256_file(corpus_path),
                   "bytes": Path(corpus_path).stat().st_size, "rows": scanned["rows"],
                   "unique_publication_numbers": scanned["unique_publication_numbers"],
                   "rows_unresolved_document": scanned["rows_unresolved_document"]},
        "checkpoint": {"name": Path(checkpoint_path).name, "sha256": sha256_file(checkpoint_path),
                       "corpus_linkage": "unknown", "definitive_training_membership_claim": False},
        "document_overlap": {
            "scan_complete": True,
            "match_level": "publication_number_ignoring_kind_code_and_leading_zeroes_not_patent_family",
            "matched_unique_publication_numbers": len(scanned["matched_publication_numbers"]),
            "reference_records_with_publication_number_match": len(document_records)},
        "reaction_overlap": {
            "match_level": "canonical_isomeric_directed_reactant_product_edge_atom_maps_removed_reagent_field_excluded",
            "rows_attempted": scanned["rows_attempted"], "malformed_rows": scanned["malformed_rows"],
            "malformed_scope": "syntax_and_product_on_attempted_rows_reactants_only_for_reference_product_matches",
            "scan_complete": scanned["rows_attempted"] == scanned["rows"],
            "matching_corpus_rows": scanned["exact_reaction_rows"],
            "matched_unique_reference_reactions": len(scanned["matched_reaction_keys"]),
            "reference_records_with_exact_reaction_match": len(reaction_records),
            "time_budget_seconds": reaction_seconds,
            "partial_scan_interpretation": "observed_matches_are_lower_bounds_unmatched_records_are_not_cleared"},
        "interpretation": "Available corpus overlap only; checkpoint training linkage and patent families remain unknown.",
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    private = {
        "schema_version": "srg-private-corpus-overlap.v1",
        "reference_sha256": report["reference"]["sha256"],
        "corpus_sha256": report["corpus"]["sha256"],
        "reference_records_with_publication_number_match": document_records,
        "reference_records_with_exact_reaction_match": reaction_records,
        "matched_publication_numbers": sorted(scanned["matched_publication_numbers"]),
        "matched_reaction_keys": sorted(scanned["matched_reaction_keys"]),
    }
    return report, private


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--reaction-seconds", type=float, default=120)
    args = parser.parse_args()
    inputs = {path.resolve() for path in (args.references, args.corpus, args.checkpoint)}
    outputs = [args.public_output.resolve(), args.private_output.resolve()]
    if outputs[0] == outputs[1] or any(path in inputs for path in outputs):
        parser.error("Outputs must be distinct and must not overwrite audit inputs")
    report, private = audit_overlap(args.references, args.corpus, args.checkpoint, args.reaction_seconds)
    for path, content in ((args.private_output, private), (args.public_output, report)):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as handle:
            json.dump(content, handle, sort_keys=True, indent=2)
            handle.write("\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
