import pytest

from enzyme_research.contracts import ResearchError
from enzyme_research.results import sequence_report_bindings


def test_regenerated_ids_and_reversed_rows_join_by_full_sequence():
    entries = [{"label": "seq_1", "metrics": {"Sequence": "CCCCC"}},
               {"label": "seq_2", "metrics": {"Sequence": "AAAAA"}}]
    assert sequence_report_bindings(entries, {"parent": "AAAAA", "variant": "CCCCC"}) == {
        "seq_1": {"candidate_id": "variant"}, "seq_2": {"candidate_id": "parent"}}


def test_preserved_exact_ids_can_join_without_sequence_column():
    assert sequence_report_bindings([{"label": "parent", "metrics": {}}], {"parent": "AAAAA"}) == {
        "parent": {"candidate_id": "parent"}}


@pytest.mark.parametrize("entries", [[], [{"label": "seq_1", "metrics": {}}],
    [{"label": "seq_1", "metrics": {"Sequence": "AAAA"}}],
    [{"label": "seq_1", "metrics": {"Sequence": "AAAAA", "sequence": "CCCCC"}}],
    [{"label": "seq_1", "metrics": {"Sequence": None}}]])
def test_missing_or_mismatched_identity_cannot_be_inferred(entries):
    with pytest.raises(ResearchError): sequence_report_bindings(entries, {"parent": "AAAAA"})


def test_duplicate_sequence_rows_do_not_cover_missing_candidates():
    entries = [{"label": "seq_1", "metrics": {"Sequence": "AAAAA"}},
               {"label": "seq_2", "metrics": {"Sequence": "AAAAA"}}]
    with pytest.raises(ResearchError, match="Duplicate"):
        sequence_report_bindings(entries, {"parent": "AAAAA", "variant": "CCCCC"})


def test_ambiguous_expected_sequence_ids_are_refused():
    with pytest.raises(ResearchError, match="unique submitted"):
        sequence_report_bindings([{"label": "parent"}, {"label": "other"}], {"parent": "AAAAA", "other": "AAAAA"})
