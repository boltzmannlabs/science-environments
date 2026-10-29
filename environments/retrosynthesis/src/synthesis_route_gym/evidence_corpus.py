"""Frozen, host-supplied source retrieval; no filesystem or network reader API.

The host must curate source visibility honestly. Schemas reject labeled private
rows and unknown fields, but cannot infer whether a falsely labeled public source
is a hidden answer. This is an application boundary, not an adversarial sandbox.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from .chemistry import canonical_smiles, reaction_identity
from .evidence_contracts import (
    SourceRecord, HostAttestation, aware_datetime, digest, public_projection,
    reaction_digest, record_digest,
)
from .schemas import EvidenceRecord


def _query(query, product, reactants, limit):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError('Retrieval limit must be 1..20')
    if query is not None and (not isinstance(query, str) or not 1 <= len(query) <= 500):
        raise ValueError('Query must contain 1..500 characters')
    product = canonical_smiles(product) if product is not None else None
    if reactants is not None:
        if not isinstance(reactants, (list, tuple)) or not 1 <= len(reactants) <= 100:
            raise ValueError('Reactants must contain 1..100 structures')
        reactants = tuple(canonical_smiles(value) for value in reactants)
    return (query.casefold() if query else None), product, reactants


@dataclass(frozen=True, init=False)
class FrozenEvidenceCorpus:
    _records: tuple[SourceRecord, ...]
    _attestations: tuple[HostAttestation, ...]
    mode: str
    fingerprint: str

    def __init__(self, records=(), *, mode='closed_information', attestations=(), now=None):
        if mode not in {'closed_information', 'evidence_retrieval'}:
            raise ValueError('Unsupported source-access mode')
        now = aware_datetime(now if now is not None else datetime.now(timezone.utc))
        rows = tuple(sorted((SourceRecord.model_validate(r.model_dump() if isinstance(r, SourceRecord) else r)
                             for r in records), key=lambda r: r.record_id))
        reviews = tuple(sorted((HostAttestation.model_validate(r.model_dump() if isinstance(r, HostAttestation) else r)
                                for r in attestations), key=lambda r: r.attestation_id))
        if len(rows) > 100000 or len({r.record_id for r in rows}) != len(rows):
            raise ValueError('Corpus size exceeded or duplicate source IDs')
        if len({r.attestation_id for r in reviews}) != len(reviews) or len({r.record_id for r in reviews}) != len(reviews):
            raise ValueError('A corpus accepts one current host attestation per source')
        if any(r.retrieved_at > now for r in rows) or any(r.checked_at > now for r in reviews):
            raise ValueError('Future retrieval or review timestamp')
        if {r.record_id for r in reviews} - {r.record_id for r in rows}:
            raise ValueError('Host attestation references an unknown source')
        object.__setattr__(self, '_records', rows)
        object.__setattr__(self, '_attestations', reviews)
        object.__setattr__(self, 'mode', mode)
        object.__setattr__(self, 'fingerprint', digest({
            'version': 'srg-evidence-corpus-v1', 'mode': mode,
            'records': [r.model_dump(mode='json') for r in rows],
            'attestations': [r.model_dump(mode='json') for r in reviews],
        }))

    def public_manifest(self):
        return {'schema_version': 'srg-evidence-corpus-v1', 'corpus_sha256': self.fingerprint,
                'access_mode': self.mode, 'record_count': len(self._records) if self.mode == 'evidence_retrieval' else 0,
                'review_scope': 'retrieved_claims_not_verified'}

    def retrieve(self, *, query=None, product=None, reactants=None, limit=10):
        query, product, reactants = _query(query, product, reactants, limit)
        base = {**self.public_manifest(), 'records': [], 'status': 'unavailable',
                'diagnostic': 'Source retrieval is disabled in the closed-information track'}
        if self.mode != 'evidence_retrieval':
            return base
        def matches(row):
            text = ' '.join((row.record_id, row.document_id, row.locator)).casefold()
            if query and query not in text:
                return False
            if product is not None and product != row.product:
                return False
            if reactants is not None and Counter(reactants) != Counter(row.reactants):
                return False
            return True
        selected = []
        for row in self._records:
            if matches(row):
                selected.append(public_projection(row))
                if len(selected) == limit:
                    break
        return {**base, 'status': 'ok', 'records': selected, 'diagnostic': ''}

    def _review_status(self, source, now):
        review = next((r for r in self._attestations if r.record_id == source.record_id), None)
        if review is None:
            return 'not_attested', None
        if (review.record_sha256 != record_digest(source)
                or review.source_content_sha256 != source.source_content_sha256
                or review.reaction_sha256 != reaction_digest(source.reactants, source.product)
                or review.checked_at < source.retrieved_at or review.checked_at > now
                or now >= review.expires_at):
            return 'stale', review
        if source.claim_kind not in {'literature_exact', 'literature_analogue', 'measured'}:
            return 'unsupported_claim_kind', review
        return ('host_attested' if review.decision == 'supported' else review.decision), review

    def verify(self, record_id, *, reactants, product, conditions=None, now=None):
        """Host-only check; never expose as a research-agent tool or hidden label."""
        now = aware_datetime(now if now is not None else datetime.now(timezone.utc))
        if product is None or reactants is None:
            raise ValueError('Verification requires declared reaction participants')
        _, product, reactants = _query(None, product, reactants, 1)
        if not isinstance(record_id, str) or not record_id:
            raise ValueError('Source ID is required')
        if conditions is not None and (not isinstance(conditions, (list, tuple))
                or len(conditions) > 50 or any(not isinstance(v, str) or not v.strip() or len(v) > 2000 for v in conditions)):
            raise ValueError('Conditions must be a bounded string list')
        result = {'record_id': record_id, 'supported': False, 'verification_status': 'not_found',
                  'conditions_scope': 'unknown', 'atom_balance_status': 'unknown',
                  'experimental_validation_performed': False, 'support_scope': 'host_source_review_only'}
        if self.mode != 'evidence_retrieval':
            return {**result, 'verification_status': 'closed_information'}
        source = next((row for row in self._records if row.record_id == record_id), None)
        if source is None:
            return result
        if reaction_identity(reactants, product) != reaction_identity(source.reactants, source.product):
            return {**result, 'verification_status': 'reaction_mismatch'}
        status, review = self._review_status(source, now)
        scope = ('same' if tuple(conditions) == source.conditions else 'different') if conditions and source.conditions else 'unknown'
        return {**result, 'verification_status': status, 'supported': status == 'host_attested',
                'claim_kind': source.claim_kind, 'conditions_scope': scope if status == 'host_attested' else 'unknown',
                'record_sha256': record_digest(source),
                'attestation_id': review.attestation_id if review else None}

    def trusted_legacy_records(self, *, now=None):
        """Explicit host bridge for existing assess_route trusted_evidence argument.

        Does not insert records into a task. Condition equivalence requires query
        conditions and therefore remains unknown in this legacy projection.
        """
        if self.mode != 'evidence_retrieval':
            return ()
        now = aware_datetime(now if now is not None else datetime.now(timezone.utc))
        accepted = []
        for source in self._records:
            status, review = self._review_status(source, now)
            if status == 'host_attested':
                accepted.append(EvidenceRecord(evidence_id=source.record_id, kind=source.claim_kind,
                    source=source.source_url, locator=source.locator, reactants=source.reactants,
                    product=source.product, verified_by=review.reviewer, conditions_scope='unknown',
                    notes='Host attestation bound to source content; not experimental reproduction'))
        return tuple(accepted)
