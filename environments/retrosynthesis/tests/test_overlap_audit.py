"""Corpus-overlap audit separates actual matches from checkpoint provenance."""
import csv
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_localretro_overlap.py"
spec = importlib.util.spec_from_file_location("localretro_overlap_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture_files(tmp_path, rows=None):
    records = [
        {"record_id": "private-route-one", "source_documents": ["US00012345A1"],
         "reaction_keys": ["CCO.O>>CC=O"]},
        {"record_id": "private-route-two", "source_documents": ["US99999999B2"],
         "reaction_keys": ["CN>>C=N"]},
    ]
    ref = tmp_path / "references.json"
    ref.write_text(json.dumps(records))
    corpus = tmp_path / "raw_train.csv"
    with corpus.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["", "id", "reactants>reagents>production"])
        writer.writeheader()
        for i, (identifier, reaction) in enumerate(rows or [
            ("US12345;paragraph", "[CH3:1][CH2:2][OH:3].O>>CC=O"),
            ("US88888888", "CN>>C=N"),
            ("unknown", "malformed"),
        ]):
            writer.writerow({"": i, "id": identifier, "reactants>reagents>production": reaction})
    checkpoint = tmp_path / "checkpoint.pth"
    checkpoint.write_bytes(b"not loaded by the audit")
    return ref, corpus, checkpoint


def test_publication_key_is_not_patent_family():
    assert audit.publication_key("US00012345A1;7;0") == "US12345"
    assert audit.publication_key("US12345B2") == "US12345"
    assert audit.publication_key("unresolved") is None
    assert audit.publication_key(None) is None


def test_reaction_identity_retains_stereo_and_ignores_atom_maps_and_reagent_field():
    assert audit.reaction_key("O.[CH3:1][CH2:2][OH:3]>Cl>CC=O") == "CCO.O>>CC=O"
    assert audit.reaction_key("N[C@@H](C)O>>C") != audit.reaction_key("N[C@H](C)O>>C")
    with pytest.raises(ValueError, match="Invalid reaction"):
        audit.reaction_key("bad")


def test_full_stream_counts_cross_document_reactions_and_keeps_details_private(tmp_path):
    report, private = audit.audit_overlap(*fixture_files(tmp_path), reaction_seconds=60)
    assert report["corpus"]["rows"] == 3
    assert report["document_overlap"]["reference_records_with_publication_number_match"] == 1
    assert report["reaction_overlap"]["reference_records_with_exact_reaction_match"] == 2
    assert report["reaction_overlap"]["malformed_rows"] == 1
    assert report["reaction_overlap"]["scan_complete"] is True
    assert report["checkpoint"]["corpus_linkage"] == "unknown"
    assert report["checkpoint"]["definitive_training_membership_claim"] is False
    assert len(report["corpus"]["sha256"]) == 64
    assert set(private["reference_records_with_exact_reaction_match"]) == {"private-route-one", "private-route-two"}
    public = json.dumps(report)
    assert "private-route-one" not in public
    assert "US00012345" not in public
    assert "CCO.O" not in public


def test_document_scan_finishes_when_reaction_budget_is_disabled(tmp_path):
    report, private = audit.audit_overlap(*fixture_files(tmp_path), reaction_seconds=0)
    assert report["corpus"]["rows"] == 3
    assert report["reaction_overlap"]["rows_attempted"] == 0
    assert report["reaction_overlap"]["scan_complete"] is False
    assert report["document_overlap"]["reference_records_with_publication_number_match"] == 1
    assert private["reference_records_with_exact_reaction_match"] == []


def test_duplicate_reference_ids_rejected(tmp_path):
    ref, corpus, checkpoint = fixture_files(tmp_path)
    data = json.loads(ref.read_text())
    ref.write_text(json.dumps(data + [data[0]]))
    with pytest.raises(ValueError, match="Duplicate"):
        audit.audit_overlap(ref, corpus, checkpoint)


def test_malformed_corpus_header_rejected(tmp_path):
    ref, corpus, checkpoint = fixture_files(tmp_path)
    corpus.write_text("other\nvalue\n")
    with pytest.raises(ValueError, match="columns"):
        audit.audit_overlap(ref, corpus, checkpoint)


def test_reference_shape_and_reaction_budget_are_validated(tmp_path):
    ref, corpus, checkpoint = fixture_files(tmp_path)
    with pytest.raises(ValueError, match="budget"):
        audit.audit_overlap(ref, corpus, checkpoint, reaction_seconds=-1)
    ref.write_text(json.dumps([{"record_id": "a", "source_documents": "not a list", "reaction_keys": []}]))
    with pytest.raises(ValueError, match="reference"):
        audit.audit_overlap(ref, corpus, checkpoint)
