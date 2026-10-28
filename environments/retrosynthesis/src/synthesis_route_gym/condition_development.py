"""Outcome-independent Doyle selection and host-only measured replay preparation.

This source is already-used development data. Input extraction never parses
outcomes; a separate materializer reads only the selected private outcomes.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import csv
from functools import lru_cache
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold

from .chemistry import canonical_smiles
from .condition_domain import FIXED_PARTNER, FIXED_PRECATALYST

SOURCE_COLUMNS = ('ligand', 'additive', 'base', 'aryl halide', 'rxn', 'yield')
SOURCE_REVISION = '2bf761afb3b2cc7ba2bfc55dc98fec76a4d102bb'
SOURCE_URL = ('https://raw.githubusercontent.com/leojklarner/gauche/'
              f'{SOURCE_REVISION}/gauche/datasets/reactions/DreherDoyle.csv')
SOURCE_SHA256 = '5f385c2175e7a3e8bea53a3dae3923fd9cf2abaf76a14a2b6b8b24c2b5643bea'
SOURCE_DOI = '10.1126/science.aar5169'
ROLES = ('ligand', 'additive', 'base')
MAX_SOURCE_BYTES = 16 * 1024 * 1024


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def _digest(value):
    if not isinstance(value, str) or not re.fullmatch('[a-f0-9]{64}', value):
        raise ValueError('Expected a lowercase SHA256 source digest')
    return value


def _rows(path, expected_sha256):
    _digest(expected_sha256)
    with Path(path).open('rb') as handle:
        raw = handle.read(MAX_SOURCE_BYTES + 1)
    if len(raw) > MAX_SOURCE_BYTES:
        raise ValueError('Source exceeds bounded input size')
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('Source digest mismatch')
    try:
        reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
        if tuple(reader.fieldnames or ()) != SOURCE_COLUMNS:
            raise ValueError('Source columns differ from the Doyle contract')
        rows = tuple(reader)
    except UnicodeError as error:
        raise ValueError('Source must be UTF-8 CSV') from error
    if not rows:
        raise ValueError('Source is empty')
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError('Malformed source columns')
    return rows


@lru_cache(maxsize=8192)
def _structure(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 10000:
        raise ValueError('Invalid source input structure')
    with rdBase.BlockLogs():
        try:
            return canonical_smiles(value)
        except (ValueError, TypeError) as error:
            raise ValueError('Invalid source input structure') from error


def _fragments(value):
    return tuple(_structure(fragment) for fragment in value.split('.') if fragment)


@lru_cache(maxsize=1024)
def _group(product):
    molecule = Chem.MolFromSmiles(product)
    Chem.RemoveStereochemistry(molecule)
    scaffold = MurckoScaffold.GetScaffoldForMol(molecule)
    representation = Chem.MolToSmiles(scaffold if scaffold.GetNumAtoms() else molecule,
                                      canonical=True, isomericSmiles=False)
    return 'condition-group-' + _hash(representation)


def _input(row):
    substrate = _structure(row['aryl halide'])
    conditions = {role: _structure(row[role]) for role in ROLES}
    parts = row['rxn'].split('>')
    if len(parts) != 3:
        raise ValueError('Invalid source reaction input')
    target = _structure(parts[2])
    if len(_fragments(target)) != 1:
        raise ValueError('Source product must identify one molecule')
    reactants = [substrate, FIXED_PARTNER]
    reagents = [conditions[role] for role in ROLES] + [FIXED_PRECATALYST]
    expected = Counter(fragment for value in reactants + reagents for fragment in _fragments(value))
    actual = Counter(fragment for part in parts[:2] for fragment in _fragments(part))
    if expected != actual:
        raise ValueError('Source reaction inputs disagree with declared chemical roles')
    ident = 'condition-' + _hash(['DreherDoyle', substrate, target, conditions])
    return {'candidate_id': ident, 'substrate': substrate, 'target': target,
            'conditions': conditions, 'recipe': {'id': ident, 'reactants': reactants,
                                                'reagents': reagents, 'product': target},
            'group_id': _group(target), 'product_group_id': 'condition-product-' + _hash(target)}


def load_doyle_inputs(path, expected_sha256):
    """Return chemistry-only records and counts, without parsing the yield column."""
    records = tuple(_input(row) for row in _rows(path, expected_sha256))
    if len({row['candidate_id'] for row in records}) != len(records):
        raise ValueError('Duplicate chemical recipes require explicit replicate handling')
    grouped = defaultdict(set)
    for row in records:
        grouped[row['substrate']].add(row['target'])
    if any(len(targets) != 1 for targets in grouped.values()):
        raise ValueError('A substrate identifies multiple source products')
    audit = {'record_count': len(records), 'substrate_count': len(grouped),
             'product_count': len({r['target'] for r in records}),
             'product_scaffold_count': len({r['group_id'] for r in records}),
             'source_family_count': 1, 'source_family': 'doi:' + SOURCE_DOI,
             'dataset_sha256': expected_sha256, 'outcomes_inspected': False,
             'data_role': 'previously_used_development',
             'factor_counts': {role: len({r['conditions'][role] for r in records}) for role in ROLES}}
    return records, audit


def _positive(value, name):
    if type(value) is not int or not 1 <= value <= 100000:
        raise ValueError(f'{name} must be a bounded positive integer')


def _chosen_substrates(records, count):
    groups = defaultdict(set)
    for row in records:
        groups[row['target']].add(row['substrate'])
    ordered = lambda values: sorted(values, key=lambda value: hashlib.sha256(value.encode()).hexdigest())
    all_substrates = set().union(*groups.values()) if groups else set()
    if not len(groups) <= count <= len(all_substrates):
        raise ValueError('Study count must cover every product and fit available substrates')
    first = {ordered(values)[0] for values in groups.values()}
    fill = ordered(all_substrates - first)[:count - len(first)]
    return ordered(first | set(fill))


def _public_study(rows, dataset_sha256, initial_count, observation_budget):
    first = rows[0]
    ident = 'condition-study-' + _hash(['DreherDoyle', first['substrate'], first['target']])[:24]
    return {'schema_version': 'srg-condition-study-v1', 'data_role': 'development',
            'study_id': ident, 'substrate': first['substrate'], 'target': first['target'],
            'source_url': SOURCE_URL, 'source_locator': 'DreherDoyle fixed-substrate condition study',
            'dataset_sha256': dataset_sha256, 'observation_budget': observation_budget,
            'initial_ids': [r['candidate_id'] for r in rows[:initial_count]],
            'candidates': [{key: deepcopy(row[key]) for key in ('candidate_id', 'conditions', 'recipe')}
                           for row in rows],
            'group_id': first['group_id'], 'product_group_id': first['product_group_id'],
            'measurement': 'source_reported_yield_percent',
            'limitations': ['Previously used development publication; not a fresh held-out source.',
                            'Source projection omits solvent, temperature and duration; none is invented.',
                            'Measured dataset replay is not a newly performed experiment.']}


def select_studies(records, *, dataset_sha256, study_count=8, candidates_per_study=24,
                   initial_count=2, observation_budget=6):
    """Cover every product before filling substrate slots; recipe order is input-hash only."""
    _digest(dataset_sha256)
    for name, value in (('study_count', study_count), ('candidates_per_study', candidates_per_study),
                        ('initial_count', initial_count), ('observation_budget', observation_budget)):
        _positive(value, name)
    if not initial_count <= observation_budget <= candidates_per_study:
        raise ValueError('Initial observations and budget must fit the candidate space')
    grouped = defaultdict(list)
    for row in records:
        grouped[row['substrate']].append(row)
    selected = _chosen_substrates(records, study_count)
    if any(len(grouped[substrate]) < candidates_per_study for substrate in selected):
        raise ValueError('Insufficient candidates for a selected study')
    return tuple(_public_study(sorted(grouped[substrate], key=lambda row: row['candidate_id'])[:candidates_per_study],
                               dataset_sha256, initial_count, observation_budget) for substrate in selected)


def _selected_outcome(value):
    try:
        number = float(value)
    except (ValueError, TypeError) as error:
        raise ValueError('Invalid selected measured outcome') from error
    if not math.isfinite(number) or not 0 <= number <= 100:
        raise ValueError('Invalid selected measured outcome')
    return number


def _requested_inputs(studies, expected_sha256):
    if len({study['study_id'] for study in studies}) != len(studies):
        raise ValueError('Duplicate selected study identity')
    requested = {}
    for study in studies:
        if study['dataset_sha256'] != expected_sha256:
            raise ValueError('Selected source input digest differs')
        for candidate in study['candidates']:
            ident = candidate['candidate_id']
            if ident in requested:
                raise ValueError('Duplicate selected candidate identity')
            requested = {**requested, ident: (study, candidate)}
    return requested


def _match_selected_input(source, requested):
    study, candidate = requested
    expected = {key: source[key] for key in ('candidate_id', 'conditions', 'recipe')}
    if (candidate != expected or study['substrate'] != source['substrate']
            or study['target'] != source['target']):
        raise ValueError('Selected candidate inputs differ from the pinned source')


def materialize_outcomes(path, expected_sha256, studies):
    """Host-only preparation: parse outcomes only for the already selected IDs."""
    from .condition_identity import condition_input_digest
    requested = _requested_inputs(studies, expected_sha256)
    outcomes = {}
    for row in _rows(path, expected_sha256):
        candidate = _input(row)
        ident = candidate['candidate_id']
        if ident in requested:
            _match_selected_input(candidate, requested[ident])
            if ident in outcomes:
                raise ValueError('Duplicate selected source candidate')
            outcomes = {**outcomes, ident: _selected_outcome(row['yield'])}
    if set(outcomes) != set(requested):
        raise ValueError('Selected candidate absent from pinned source')
    return {study['study_id']: {'schema_version': 'srg-condition-outcomes-v1',
                              'study_id': study['study_id'], 'dataset_sha256': expected_sha256,
                              'candidate_inputs_sha256': condition_input_digest(study),
                              'outcomes': {c['candidate_id']: outcomes[c['candidate_id']]
                                           for c in study['candidates']}} for study in studies}


def _model_metadata(value):
    required = {'model_version', 'model_revision', 'source_url', 'license', 'manifest_sha256'}
    optional = {'asset_sha256', 'runtime_sha256', 'shared_cache', 'inference_seconds'}
    if not isinstance(value, dict) or not required <= set(value) or set(value) - required - optional:
        raise ValueError('Only public pinned model metadata is allowed')
    for name in required:
        if not isinstance(value[name], str) or not value[name]:
            raise ValueError('Invalid public model metadata')
    _digest(value['manifest_sha256'])
    if not re.fullmatch('[a-f0-9]{40}', value['model_revision']):
        raise ValueError('Invalid public model revision')
    source = urlsplit(value['source_url'])
    if source.scheme != 'https' or not source.netloc or source.username or source.password:
        raise ValueError('Model source must be a public HTTPS URL')
    _metadata_options(value)
    return json.loads(json.dumps(value, allow_nan=False))


def _metadata_options(value):
    for field in ('asset_sha256', 'runtime_sha256'):
        hashes = value.get(field, {})
        if not isinstance(hashes, dict):
            raise ValueError('Public model identities must be digest mappings')
        for key, digest in hashes.items():
            if not isinstance(key, str) or not re.fullmatch('[A-Za-z0-9_.-]{1,100}', key):
                raise ValueError('Invalid public asset identity')
            _digest(digest)
        if field == 'runtime_sha256' and set(hashes) - {'adapter_sha256', 'worker_sha256', 'python_sha256'}:
            raise ValueError('Unexpected runtime identity field')
    if 'shared_cache' in value and type(value['shared_cache']) is not bool:
        raise ValueError('Cache policy must be explicit')
    seconds = value.get('inference_seconds', 0)
    if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds < 0:
        raise ValueError('Inference time must be finite and nonnegative')


def _raw_prediction(row):
    raw = row['raw_yield_percent']
    if raw is not None and (type(raw) not in (int, float) or not math.isfinite(raw)):
        raise ValueError('Invalid raw model prediction')
    if row['status'] == 'scored' and raw != row['predicted_yield_percent']:
        raise ValueError('Raw and public predictions disagree')
    if row['status'] == 'abstained':
        outside = row['reason'] == 'prediction_out_of_range'
        if (outside and (raw is None or 0 <= raw <= 100)) or (not outside and raw is not None):
            raise ValueError('Raw prediction disagrees with abstention')


def _prediction(row, candidate_id, metadata):
    expected = {'id', 'status', 'predicted_yield_percent', 'raw_yield_percent', 'reason',
                'model_version', 'domain', 'uncertainty_kind', 'evidence_status', 'endpoint_scope'}
    if (not isinstance(row, dict) or set(row) != expected or row['id'] != candidate_id
            or row['model_version'] != metadata['model_version'] or row['evidence_status'] != 'predicted'
            or row['endpoint_scope'] != 'model_yield_not_experimental_feasibility'):
        raise ValueError('Prediction identity, model or evidence contract differs')
    value, status, reason = row['predicted_yield_percent'], row['status'], row['reason']
    if status == 'scored':
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 100 or reason is not None:
            raise ValueError('Invalid scored prediction')
    elif status != 'abstained' or value is not None or reason not in {
            'token_limit_exceeded', 'unknown_token', 'nonfinite_prediction', 'prediction_out_of_range'}:
        raise ValueError('Invalid prediction abstention')
    _raw_prediction(row)
    for field in ('domain', 'uncertainty_kind'):
        if not isinstance(row[field], str) or not 1 <= len(row[field]) <= 1000:
            raise ValueError('Prediction domain and uncertainty must remain explicit')
    ident = 'condition-prediction-' + _hash([candidate_id, metadata, status, value, reason])[:24]
    uncertainty = row['uncertainty_kind'] + (f'; abstention_reason={reason}' if reason else '')
    return {'candidate_id': candidate_id, 'prediction_id': ident, 'status': status,
            'value': float(value) if value is not None else None, 'unit': 'percent',
            'domain': row['domain'], 'model_version': row['model_version'], 'uncertainty': uncertainty}


def normalize_predictions(study, publisher_results, model_metadata):
    """Keep actual publisher abstentions; never coerce predictions into observations."""
    from .condition_identity import condition_input_digest
    metadata = _model_metadata(model_metadata)
    ids = [row['candidate_id'] for row in study['candidates']]
    if not isinstance(publisher_results, (list, tuple)) or len(publisher_results) != len(ids):
        raise ValueError('Incomplete or duplicate study prediction result')
    return {'schema_version': 'srg-condition-predictions-v1', 'study_id': study['study_id'],
            'candidate_inputs_sha256': condition_input_digest(study),
            'model_metadata': metadata,
            'predictions': [_prediction(row, ident, metadata) for row, ident in zip(publisher_results, ids)]}
