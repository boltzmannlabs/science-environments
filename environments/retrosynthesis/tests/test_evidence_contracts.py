"""Frozen public-source contracts, distinct from model output and hidden labels."""
from datetime import datetime, timedelta, timezone
import pytest
from synthesis_route_gym.evidence_contracts import SourceRecord, HostAttestation, record_digest, reaction_digest
from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus

NOW = datetime(2026, 10, 27, 12, tzinfo=timezone.utc)


def record(**changes):
    fields = dict(record_id='source-1', document_id='document-1', source_url='https://example.org/paper',
                  locator='Table 1, reaction 2', reactants=['CCO'], product='CC=O',
                  claim_kind='literature_exact', conditions_scope='unknown',
                  retrieved_at=NOW-timedelta(days=1), source_content_sha256='a'*64)
    return SourceRecord(**{**fields, **changes})


def attestation(source, **changes):
    fields = dict(attestation_id='review-1', record_id=source.record_id,
                  record_sha256=record_digest(source), reaction_sha256=reaction_digest(source.reactants, source.product),
                  source_content_sha256=source.source_content_sha256, checked_at=NOW,
                  expires_at=NOW+timedelta(days=30), reviewer='host-source-review', decision='supported')
    return HostAttestation(**{**fields, **changes})


def test_source_aliases_are_canonical_without_losing_stereo_or_salts():
    source = record(reactants=['OCC', '[Na+].[Cl-]'], product='C[C@@H](O)C(=O)O')
    assert source.reactants == ('CCO', '[Cl-].[Na+]')
    assert source.product != record(product='C[C@H](O)C(=O)O').product
    assert reaction_digest(['OCC'], 'CC=O') == reaction_digest(['CCO'], 'O=CC')
    assert reaction_digest(['CCO', 'CCO'], 'CC=O') != reaction_digest(['CCO'], 'CC=O')
    with pytest.raises(ValueError): source.product = 'C'


@pytest.mark.parametrize('changes', [
    {'source_url':'file:///tmp/judge.json'}, {'source_url':'https://user:secret@example.org/paper'},
    {'source_url':'ftp://example.org/paper'}, {'source_url':'https://example.org/\nsecret'},
    {'retrieved_at':'2026-10-27T12:00:00'}, {'retrieved_at':True}, {'source_content_sha256':'bad'},
    {'reactants':['invalid smiles']}, {'visibility':'evaluator'}, {'visibility':'reference_answer'},
    {'yield_percent':90}, {'verified_by':'model'}, {'claim_kind':'measured', 'raw_rows':[{'yield':90}]},
    {'document_id':' '}, {'locator':' '}, {'reactants':[]},
])
def test_malformed_or_privileged_records_are_rejected(changes):
    with pytest.raises(ValueError): record(**changes)


def test_retrieved_claim_is_not_host_verified_until_separate_attestation():
    source = record()
    corpus = FrozenEvidenceCorpus([source], mode='evidence_retrieval', now=NOW)
    result = corpus.retrieve(product='O=CC', limit=1)
    assert result['status'] == 'ok'
    row = result['records'][0]
    assert row['claim_kind'] == 'literature_exact'
    assert row['evidence_status'] == 'source_claim'
    assert row['verification_status'] == 'not_attested'
    assert row['atom_balance_status'] == 'unknown'
    assert 'verified_by' not in row
    assert corpus.trusted_legacy_records(now=NOW) == ()
    assert not corpus.verify('source-1', reactants=['CCO'], product='CC=O', now=NOW)['supported']


def test_supported_attestation_binds_content_reaction_conditions_and_expiry():
    source = record(conditions=['reported condition'])
    corpus = FrozenEvidenceCorpus([source], mode='evidence_retrieval', attestations=[attestation(source)], now=NOW)
    verified = corpus.verify('source-1', reactants=['OCC'], product='O=CC', conditions=['reported condition'], now=NOW)
    assert verified['supported']
    assert verified['verification_status'] == 'host_attested'
    assert verified['conditions_scope'] == 'same'
    assert verified['experimental_validation_performed'] is False
    assert corpus.verify('source-1', reactants=['CCO'], product='CC=O', now=NOW)['conditions_scope'] == 'unknown'
    assert corpus.verify('source-1', reactants=['CCO'], product='CC=O', conditions=['different'], now=NOW)['conditions_scope'] == 'different'
    assert not corpus.verify('source-1', reactants=['C'], product='CC=O', now=NOW)['supported']
    assert not corpus.verify('source-1', reactants=['CCO'], product='CC=O', now=NOW+timedelta(days=31))['supported']
    assert corpus.trusted_legacy_records(now=NOW)[0].verified_by == 'host-source-review'
    assert corpus.retrieve()['records'][0]['verification_status'] == 'not_attested'


def test_stale_record_does_not_reuse_old_attestation():
    old, changed = record(), record(source_content_sha256='b'*64)
    corpus = FrozenEvidenceCorpus([changed], mode='evidence_retrieval', attestations=[attestation(old)], now=NOW)
    result = corpus.verify('source-1', reactants=['CCO'], product='CC=O', now=NOW)
    assert result['verification_status'] == 'stale'
    assert not result['supported']
    assert corpus.trusted_legacy_records(now=NOW) == ()


def test_model_or_proxy_cannot_be_promoted_by_host_attestation():
    source = record(claim_kind='predicted')
    corpus = FrozenEvidenceCorpus([source], mode='evidence_retrieval', attestations=[attestation(source)], now=NOW)
    assert not corpus.verify('source-1', reactants=['CCO'], product='CC=O', now=NOW)['supported']
    assert corpus.trusted_legacy_records(now=NOW) == ()


def test_closed_mode_withholds_all_records_and_no_paths_or_urls_can_be_queried():
    corpus = FrozenEvidenceCorpus([record()], now=NOW)
    assert corpus.retrieve(query='document')['status'] == 'unavailable'
    assert corpus.retrieve()['records'] == []
    assert not corpus.verify('source-1', reactants=['CCO'], product='CC=O', now=NOW)['supported']
    assert corpus.trusted_legacy_records(now=NOW) == ()
    with pytest.raises(TypeError): corpus.retrieve(path='/tmp/labels.json')


def test_corpus_is_order_independent_frozen_and_retrieval_is_bounded():
    first, second = record(), record(record_id='source-2', document_id='document-2', product='CCO')
    source_rows = [first, second]
    corpus = FrozenEvidenceCorpus(source_rows, mode='evidence_retrieval', now=NOW)
    digest = corpus.fingerprint
    source_rows.clear()
    assert corpus.fingerprint == FrozenEvidenceCorpus([second, first], mode='evidence_retrieval', now=NOW).fingerprint
    assert len(corpus.retrieve(limit=1)['records']) == 1
    assert corpus.retrieve(query='DOCUMENT-2')['records'][0]['record_id'] == 'source-2'
    assert len(corpus.retrieve(reactants=['OCC'])['records']) == 2
    returned = corpus.retrieve(); returned['records'][0]['product'] = 'C'
    assert corpus.fingerprint == digest
    assert corpus.retrieve()['records'][0]['product'] == first.product
    assert corpus.public_manifest()['corpus_sha256'] == digest


@pytest.mark.parametrize('kwargs', [{'limit':True}, {'limit':0}, {'limit':21}, {'query':'a'*501},
                                    {'reactants':'CCO'}, {'product':'invalid'}, {'query':12}])
def test_invalid_queries_fail_before_retrieval(kwargs):
    with pytest.raises(ValueError):
        FrozenEvidenceCorpus([record()], mode='evidence_retrieval', now=NOW).retrieve(**kwargs)


def test_duplicate_records_reviews_future_timestamps_and_unknown_review_reject():
    source = record()
    with pytest.raises(ValueError): FrozenEvidenceCorpus([source, source], now=NOW)
    with pytest.raises(ValueError): FrozenEvidenceCorpus([source], attestations=[attestation(source), attestation(source)], now=NOW)
    with pytest.raises(ValueError): FrozenEvidenceCorpus([record(retrieved_at=NOW+timedelta(days=1))], now=NOW)
    with pytest.raises(ValueError): FrozenEvidenceCorpus([source], attestations=[attestation(source, record_id='missing')], now=NOW)
    with pytest.raises(ValueError): attestation(source, expires_at=NOW-timedelta(days=1))


def test_changed_mode_and_attestation_change_fingerprint():
    source = record()
    closed = FrozenEvidenceCorpus([source], now=NOW)
    opened = FrozenEvidenceCorpus([source], mode='evidence_retrieval', now=NOW)
    reviewed = FrozenEvidenceCorpus([source], mode='evidence_retrieval', attestations=[attestation(source)], now=NOW)
    assert len({closed.fingerprint, opened.fingerprint, reviewed.fingerprint}) == 3


def test_bounded_retrieval_does_not_project_records_beyond_limit(monkeypatch):
    import synthesis_route_gym.evidence_corpus as module
    original = module.public_projection
    projected = []
    def counted(row):
        projected.append(row.record_id)
        return original(row)
    monkeypatch.setattr(module, 'public_projection', counted)
    corpus = FrozenEvidenceCorpus([record(record_id=f'source-{i}') for i in range(10)], mode='evidence_retrieval', now=NOW)
    assert len(corpus.retrieve(limit=1)['records']) == 1
    assert len(projected) == 1


def test_host_verification_rejects_absent_participants_and_oversize_conditions():
    corpus = FrozenEvidenceCorpus([record()], mode='evidence_retrieval', now=NOW)
    with pytest.raises(ValueError): corpus.verify('source-1', reactants=None, product='CC=O', now=NOW)
    with pytest.raises(ValueError): corpus.verify('source-1', reactants=['CCO'], product=None, now=NOW)
    with pytest.raises(ValueError): corpus.verify('source-1', reactants=['CCO'], product='CC=O', conditions=['x'*2001], now=NOW)


def test_unresolved_contradicted_or_stereomismatched_source_does_not_support_route():
    source = record(product='C[C@@H](O)C(=O)O')
    for decision in ('contradicted', 'unresolved'):
        corpus = FrozenEvidenceCorpus([source], mode='evidence_retrieval',
            attestations=[attestation(source, decision=decision)], now=NOW)
        assert corpus.verify('source-1', reactants=['CCO'], product=source.product, now=NOW)['verification_status'] == decision
        assert corpus.trusted_legacy_records(now=NOW) == ()
    reviewed = FrozenEvidenceCorpus([source], mode='evidence_retrieval', attestations=[attestation(source)], now=NOW)
    assert reviewed.verify('source-1', reactants=['CCO'], product='C[C@H](O)C(=O)O', now=NOW)['verification_status'] == 'reaction_mismatch'
    assert reviewed.verify('missing', reactants=['CCO'], product=source.product, now=NOW)['verification_status'] == 'not_found'


def test_source_conditions_urls_review_and_modes_require_complete_valid_values():
    for changes in ({'conditions':[' ']}, {'source_url':'https://example.org:bad/paper'}, {'retrieved_at':'bad'}):
        with pytest.raises(ValueError): record(**changes)
    with pytest.raises(ValueError): attestation(record(), reviewer=' ')
    with pytest.raises(ValueError): FrozenEvidenceCorpus([record()], mode='unknown', now=NOW)
    with pytest.raises(ValueError): FrozenEvidenceCorpus([record()], attestations=[attestation(record(), checked_at=NOW+timedelta(days=1))], now=NOW)
    assert FrozenEvidenceCorpus([record()], mode='evidence_retrieval', now=NOW).retrieve(product='C')['records'] == []
    assert FrozenEvidenceCorpus([record()], mode='evidence_retrieval', now=NOW).retrieve(reactants=['C'])['records'] == []
