"""Conservative, versioned imports of completed route artifacts; no network IO.

REBOLT's historical ``reference=True`` marks duplicate reaction display nodes,
not verified literature. Legacy stock flags, yields, scores and costs are not
imported as scientific evidence or environment assessments.
"""
from __future__ import annotations

import hashlib
import json
import re

from .chemistry import canonical_smiles
from .schemas import RouteCandidate, Task
from .validation import assess_route

FORMATS = ('srg-route-candidates-v1', 'rebolt-scored-paths-v1')
MAX_BYTES = 2_000_000
MAX_ROUTES = 100


def _payload_hash(payload):
    pending, active, nodes = [(payload, 0, False)], set(), 0
    while pending:
        value, depth, leaving = pending.pop()
        if leaving:
            active.remove(id(value))
            continue
        nodes += 1
        if nodes > 100_000 or depth > 420:
            raise ValueError('Artifact size/depth exceeds import bounds')
        if isinstance(value, (dict, list, tuple)):
            if id(value) in active:
                raise ValueError('Artifact contains an object cycle')
            active.add(id(value))
            pending.append((value, depth, True))
            if isinstance(value, dict):
                if any(not isinstance(key, str) for key in value):
                    raise ValueError('Artifact object keys must be strings')
                values = value.values()
            else:
                values = value
            pending.extend((item, depth + 1, False) for item in values)
    try:
        encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError('Artifact must be finite JSON data') from exc
    if len(encoded) > MAX_BYTES:
        raise ValueError('Artifact size exceeds two million bytes')
    return hashlib.sha256(encoded).hexdigest()


def _provenance(value, digest):
    value = {} if value is None else value
    allowed = {'job_name', 'doc_id', 'source_version', 'artifact_id'}
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError('Provenance permits only bounded job/artifact identifiers')
    for key, item in value.items():
        if not isinstance(item, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,256}', item):
            raise ValueError('Invalid provenance identifier')
        if key == 'job_name' and item != 'retrosynthesis':
            raise ValueError('Source job must be retrosynthesis')
    return {**value, 'payload_sha256':digest}


def _flag(node, key):
    value = node.get(key)
    if value is True or value == 'True':
        return True
    if value is False or value == 'False':
        return False
    raise ValueError('REBOLT node requires explicit Boolean ' + key)


def _children(node):
    children = node.get('children', [])
    if not isinstance(children, list) or len(children) > 100:
        raise ValueError('Invalid REBOLT node children')
    return children


def _molecule(node, version, ancestors=()):
    if not isinstance(node, dict) or _flag(node, 'reference'):
        raise ValueError('Expected a REBOLT molecule display node')
    product = canonical_smiles(node.get('smile'))
    if product in ancestors:
        raise ValueError('Route contains a molecule cycle')
    if len(ancestors) > 100:
        raise ValueError('Route depth exceeds 100 transformations')
    children, building_block = _children(node), _flag(node, 'building_block')
    if not children:
        if not building_block or not _flag(node, 'terminal'):
            raise ValueError('Unexpanded REBOLT nodes require explicit terminal stock flags')
        return product, ()
    if building_block or len(children) != 1:
        raise ValueError('A molecule must contain exactly one reaction display node')
    reaction = children[0]
    if not isinstance(reaction, dict) or not _flag(reaction, 'reference'):
        raise ValueError('Expected the paired REBOLT reaction display node')
    if _flag(reaction, 'building_block') or _flag(reaction, 'terminal'):
        raise ValueError('Reaction display node cannot be a terminal building block')
    if canonical_smiles(reaction.get('smile')) != product:
        raise ValueError('Paired reaction display product differs from molecule')
    precursors = _children(reaction)
    if not precursors:
        raise ValueError('A reaction requires all precursor molecule nodes')
    pairs = [_molecule(child, version, (*ancestors, product)) for child in precursors]
    substeps = tuple(step for _, steps in pairs for step in steps)
    if len(substeps) >= 100:
        raise ValueError('Route exceeds 100 transformations')
    step = {'step_id':'import-' + hashlib.sha256(product.encode()).hexdigest()[:20],
            'product':product, 'reactants':[{'smiles':smiles} for smiles, _ in pairs],
            'source_tool':'REBOLT/retrosynthesis', 'source_version':version,
            'evidence_ids':[], 'conditions_complete':False}
    return product, (*substeps, step)


def _rebolt_routes(payload, version):
    if not isinstance(payload, dict) or not 1 <= len(payload) <= MAX_ROUTES:
        raise ValueError('Expected one to 100 completed REBOLT scored paths')
    if any(not re.fullmatch(r'top[0-9]+', key) for key in payload):
        raise ValueError('Unsupported REBOLT artifact shape; expected topN keys')
    routes = []
    for key in sorted(payload, key=lambda key:int(key[3:])):
        item = payload[key]
        if not isinstance(item, dict) or set(item) != {'path', 'idx'}:
            raise ValueError('Each scored path requires only path and idx')
        if type(item['idx']) is not int or item['idx'] != int(key[3:]):
            raise ValueError('Scored path index must match topN key')
        target, steps = _molecule(item['path'], version)
        producers = {}
        for step in steps:
            previous = producers.get(step['product'])
            if previous is not None:
                old = sorted(use['smiles'] for use in previous['reactants'])
                new = sorted(use['smiles'] for use in step['reactants'])
                if old != new:
                    raise ValueError('Route has conflicting intermediate syntheses')
            else:
                producers = {**producers, step['product']:step}
        identity = json.dumps({'target':target,'steps':list(producers.values())}, sort_keys=True)
        route_id = 'rebolt-' + hashlib.sha256((key + identity).encode()).hexdigest()[:24]
        routes.append({'route_id':route_id,'target':target,'steps':list(producers.values())})
    return routes


def _canonical_routes(payload):
    if not isinstance(payload, list) or not 1 <= len(payload) <= MAX_ROUTES:
        raise ValueError('Expected one to 100 canonical route candidates')
    routes = [RouteCandidate.model_validate(item) for item in payload]
    return [route.model_copy(update={'steps':tuple(step.model_copy(update={'evidence_ids':()})
                   for step in route.steps)}).model_dump(mode='json') for route in routes]


def import_routes(payload, *, target, format, provenance=None):
    """Validate an entire artifact before returning routes; never mutate inputs.

    Callers must store returned candidates through environment ``propose_route``
    and expose its assessments. Import is not inventory acceptance or scientific
    validation. No task evidence records or evaluator outcomes are accessed.
    """
    if format not in FORMATS:
        raise ValueError('Unsupported route import format/version')
    identity = _provenance(provenance, _payload_hash(payload))
    target = canonical_smiles(target)
    routes = (_canonical_routes(payload) if format == FORMATS[0] else
              _rebolt_routes(payload, identity.get('source_version', 'unreported')))
    task = Task(task_id='route-import-check', target=target, inventory=[])
    seen = set()
    for raw in routes:
        route = RouteCandidate.model_validate(raw)
        if route.route_id in seen:
            raise ValueError('Duplicate route identifiers in import artifact')
        seen.add(route.route_id)
        if route.target != target:
            raise ValueError('Imported route target differs from task target')
        if not assess_route(task, route).graph_valid:
            raise ValueError('Imported route has invalid or disconnected dependency graph')
    return {'schema_version':'srg-route-import-v1','format':format,'routes':routes,
            'provenance':identity,'evidence_status':'predicted',
            'warnings':['Imported evidence claims are not trusted; all steps remain predicted.',
                        'Inventory, quantities and task constraints require environment assessment.',
                        'Legacy REBOLT stock flags, scores, costs and yield fields are not imported.']}
