"""Source claims and host attestations are separate, content-bound contracts.

A hash establishes identity, not truth. Only a trusted host may supply reviewed
attestations; a tool-provided reviewer string never creates such authority.
"""
from datetime import datetime, timezone
import hashlib
import json
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from .chemistry import reaction_identity
from .schemas import Identifier, Record, Smiles

Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
Text = Annotated[str, Field(min_length=1, max_length=2000)]
ClaimKind = Literal['literature_exact', 'literature_analogue', 'measured', 'proxy', 'predicted', 'unresolved']


def aware_datetime(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError as exc:
            raise ValueError('Expected an ISO timestamp with timezone') from exc
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError('Expected a timezone-aware timestamp')
    return value.astimezone(timezone.utc)


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def reaction_digest(reactants, product):
    return digest(reaction_identity(reactants, product))


class SourceRecord(Record):
    """Allowed corpus row; no outcome labels, arbitrary metadata or file locations."""
    record_id: Identifier
    document_id: Text
    source_url: Annotated[str, Field(min_length=1, max_length=2000)]
    locator: Text
    reactants: Annotated[tuple[Smiles, ...], Field(min_length=1, max_length=100)]
    product: Smiles
    claim_kind: ClaimKind
    conditions_scope: Literal['unknown', 'same', 'different'] = 'unknown'
    conditions: Annotated[tuple[Text, ...], Field(max_length=50)] = ()
    retrieved_at: datetime
    source_content_sha256: Digest
    visibility: Literal['public_source'] = 'public_source'
    stereochemistry_scope: Literal['as_encoded', 'not_reported'] = 'as_encoded'

    _retrieved = field_validator('retrieved_at', mode='before')(aware_datetime)

    @field_validator('document_id', 'locator')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('Source identity and location cannot be blank')
        return value

    @field_validator('conditions')
    @classmethod
    def nonblank_conditions(cls, values):
        if any(not value.strip() for value in values):
            raise ValueError('Condition descriptions cannot be blank')
        return values

    @field_validator('source_url')
    @classmethod
    def http_source(cls, value):
        if any(char.isspace() or ord(char) < 32 for char in value):
            raise ValueError('Source URL contains whitespace or controls')
        parsed = urlsplit(value)
        if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username is not None or parsed.password is not None:
            raise ValueError('Source URL must be HTTP(S), without credentials')
        try:
            parsed.port
        except ValueError as exc:
            raise ValueError('Invalid source URL port') from exc
        return value


class SourceProjection(SourceRecord):
    """Model-visible projection deliberately excludes host review outcomes."""
    record_sha256: Digest
    reaction_sha256: Digest
    evidence_status: Literal['source_claim'] = 'source_claim'
    verification_status: Literal['not_attested'] = 'not_attested'
    atom_balance_status: Literal['unknown'] = 'unknown'


class HostAttestation(Record):
    """Host-only source review record; not a signature or experimental validation."""
    attestation_id: Identifier
    record_id: Identifier
    record_sha256: Digest
    reaction_sha256: Digest
    source_content_sha256: Digest
    checked_at: datetime
    expires_at: datetime
    reviewer: Text
    decision: Literal['supported', 'contradicted', 'unresolved']

    _times = field_validator('checked_at', 'expires_at', mode='before')(aware_datetime)

    @field_validator('reviewer')
    @classmethod
    def reviewer_nonblank(cls, value):
        if not value.strip():
            raise ValueError('Host reviewer identity cannot be blank')
        return value

    @model_validator(mode='after')
    def ordered_times(self):
        if self.expires_at <= self.checked_at:
            raise ValueError('Attestation expiry must follow review time')
        return self


def record_digest(record):
    source = SourceRecord.model_validate(record.model_dump() if isinstance(record, SourceRecord) else record)
    return digest(source.model_dump(mode='json'))


def public_projection(record):
    return SourceProjection(**record.model_dump(), record_sha256=record_digest(record),
        reaction_sha256=reaction_digest(record.reactants, record.product)).model_dump(mode='json')
