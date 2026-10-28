"""Provisional final cohort design from hash-pinned public inputs only.

No evaluator, reference route, model, condition observation or inventory loader
is imported. RDKit computes only canonical input identities and scaffolds.
"""
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold

ARMS = ('main', 'strongest_fixed_pending_development', 'experimental_specialist_pending_development')
REGIMES = ('budgeted', 'unbudgeted')
METADATA_KEYS = {'task_id', 'partition', 'track'}
TASK_KEYS = METADATA_KEYS | {'target', 'inventory_exclusions', 'constraints', 'budget'}
CONSTRAINT_KEYS = {'max_steps', 'forbidden_smiles', 'forbidden_smarts',
                   'available_equipment', 'forbidden_operations', 'require_complete_conditions'}
BUDGET_KEYS = {'max_actions', 'max_expansions', 'max_wall_seconds', 'max_llm_tokens', 'top_k'}
DIGEST = re.compile(r'[a-f0-9]{64}\Z')
IDENTITY = re.compile(r'(route|condition)-[A-Za-z0-9_-]+\Z')


def _sha(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def _pairs(pairs):
    if len({key for key, _ in pairs}) != len(pairs):
        raise ValueError('Duplicate JSON keys are not public input contracts')
    return dict(pairs)


def _json(raw):
    def reject(_):
        raise ValueError('Nonfinite public input')
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=reject)


def _keys(value, allowed, required=None):
    if (not isinstance(value, dict) or set(value)-allowed
            or not (allowed if required is None else required) <= set(value)):
        raise ValueError('Expected only allowlisted public input fields')


def _path(root, relative):
    if (not isinstance(relative, str) or '\\' in relative
            or PurePosixPath(relative).is_absolute()
            or any(part in {'', '.', '..'} for part in relative.split('/'))):
        raise ValueError('Public input path is not a canonical relative path')
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError('Public input path escapes anchored public tree')
    return path


def _manifest(root, anchor):
    if not isinstance(anchor, str) or DIGEST.fullmatch(anchor) is None:
        raise ValueError('An explicit manifest SHA256 anchor is required')
    raw = _path(root, 'manifest.json').read_bytes()
    if _sha(raw) != anchor:
        raise ValueError('Public manifest differs from development-selection anchor')
    manifest = _json(raw)
    _keys(manifest, {'schema_version','bundle_kind','files','tasks'})
    if manifest['schema_version'] != '1.0' or manifest['bundle_kind'] != 'public':
        raise ValueError('Expected public benchmark bundle')
    if not isinstance(manifest['files'], dict) or not isinstance(manifest['tasks'], list):
        raise ValueError('Expected public file map and metadata list')
    identities = set()
    for row in manifest['tasks']:
        _keys(row, METADATA_KEYS)
        identity = row['task_id']
        if (not isinstance(identity, str) or not IDENTITY.fullmatch(identity) or identity in identities
                or row['partition'] not in {'smoke','development','sealed_final'}
                or row['track'] not in {'reference_route','measured_conditions'}
                or identity.startswith('route-') != (row['track'] == 'reference_route')):
            raise ValueError('Invalid or duplicate public task metadata')
        identities.add(identity)
    expected = {'inventory.json','provenance.json'} | {'tasks/'+i+'.json' for i in identities}
    if set(manifest['files']) != expected:
        raise ValueError('Only public inventory/provenance and declared tasks may be indexed')
    for name, digest in manifest['files'].items():
        _path(root, name)
        if not isinstance(digest, str) or DIGEST.fullmatch(digest) is None:
            raise ValueError('Invalid pinned public file hash')
    return manifest


def _canonical(text):
    if not isinstance(text, str) or not text or len(text)>10000:
        raise ValueError('Expected bounded input SMILES')
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(text)
    if mol is None or mol.GetNumAtoms() == 0:
        raise ValueError('Invalid input SMILES')
    return Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)


def _task(root, manifest, metadata):
    name = 'tasks/'+metadata['task_id']+'.json'
    raw = _path(root, name).read_bytes()
    if _sha(raw) != manifest['files'][name]:
        raise ValueError('Public task differs from pinned manifest hash')
    row = _json(raw)
    _keys(row, TASK_KEYS)
    if any(row[key] != metadata[key] for key in METADATA_KEYS):
        raise ValueError('Public task identity differs from manifest metadata')
    _keys(row['constraints'], CONSTRAINT_KEYS, set())
    _keys(row['budget'], BUDGET_KEYS, {'top_k'})
    for key, value in row['constraints'].items():
        if key == 'max_steps':
            valid = type(value) is int and 0 <= value <= 100
        elif key == 'require_complete_conditions':
            valid = type(value) is bool
        else:
            valid = isinstance(value, list) and all(isinstance(v,str) for v in value)
        if not valid:
            raise ValueError('Invalid public constraint input')
    for key, value in row['budget'].items():
        if (type(value) not in ((int,float) if key=='max_wall_seconds' else (int,))
                or not math.isfinite(value) or value <= 0 or (key=='top_k' and value>100)):
            raise ValueError('Invalid finite public task budget')
    exclusions = row['inventory_exclusions']
    if not isinstance(exclusions, list):
        raise ValueError('Expected input inventory exclusions')
    canonical = sorted({_canonical(value) for value in exclusions})
    if len(canonical) != len(exclusions):
        raise ValueError('Duplicate inventory exclusion identities')
    return {'task_id': row['task_id'], 'path': name, 'sha256': manifest['files'][name],
            'target': _canonical(row['target']), 'inventory_exclusions': canonical,
            'constraints': row['constraints'], 'budget': row['budget']}


def _groups(tasks):
    grouped = {}
    for task in tasks:
        grouped = {**grouped, task['target']: [*grouped.get(task['target'], []), task]}
    rows = []
    for target, siblings in grouped.items():
        if (len(siblings) != 2 or sum(not row['inventory_exclusions'] for row in siblings) != 1
                or any(row['constraints'] != siblings[0]['constraints']
                       or row['budget'] != siblings[0]['budget'] for row in siblings)):
            raise ValueError('Each target requires consistent full/limited inventory siblings')
        scaffold = MurckoScaffold.MurckoScaffoldSmiles(smiles=target, includeChirality=False)
        rows.append({'group_id': _sha(target), 'target': target,
            'selection_key': _sha('srg12-final-v1:'+target), 'scaffold_smiles': scaffold,
            'scaffold_cluster_id': _sha('murcko:'+scaffold) if scaffold else 'empty-scaffold-conservative-group',
            'tasks': sorted([{**row, 'inventory_variant': 'limited' if row['inventory_exclusions'] else 'full'}
                             for row in siblings], key=lambda row: row['task_id'])})
    return sorted(rows, key=lambda row: row['selection_key'])


def _schedule(groups):
    result = []
    for group in groups:
        for task in group['tasks']:
            for repeat in (1,2):
                for regime in REGIMES:
                    block = f"{task['task_id']}:{repeat}:{regime}"
                    arms = sorted(ARMS, key=lambda arm: _sha('srg12-arm-order-v1:'+block+':'+arm))
                    for position, arm in enumerate(arms, 1):
                        result.append({'episode_id': _sha(block+':'+arm), 'block_id': block,
                            'group_id': group['group_id'], 'task_id': task['task_id'],
                            'task_sha256': task['sha256'], 'inventory_variant': task['inventory_variant'],
                            'repeat': repeat, 'regime': regime, 'arm': arm, 'position_in_block': position,
                            'arm_order_key': _sha('srg12-arm-order-v1:'+block+':'+arm),
                            'top_k': task['budget']['top_k'], 'execution_authorized': False})
    return result


def build_cohort(public_root, manifest_sha256, *, count=20, expected_groups=50):
    """Prepare a descriptive design, never a finalized runtime or executable plan."""
    if (type(count) is not int or type(expected_groups) is not int
            or not 1 <= count <= expected_groups):
        raise ValueError('Invalid proposed cohort size')
    root = Path(public_root).resolve(strict=True)
    manifest = _manifest(root, manifest_sha256)
    metadata = [row for row in manifest['tasks'] if row['track']=='reference_route'
                and row['partition']=='sealed_final']
    candidates = _groups([_task(root, manifest, row) for row in metadata])
    if len(candidates) != expected_groups:
        raise ValueError('Candidate target group count differs from predeclared design')
    groups = candidates[:count]
    return {'schema_version': 'srg12-final-cohort-proposal-v1', 'public_manifest_sha256': manifest_sha256,
        'configuration_frozen': False, 'execution_authorized': False, 'final_labels_opened': False,
        'runtime_finalists': {'main': 'main', 'fixed': None, 'experimental_specialist': None},
        'candidate_target_groups': len(candidates), 'selected_target_groups': count,
        'candidate_groups': candidates, 'groups': groups,
        'task_hashes': {task['task_id']: task['sha256'] for group in groups for task in group['tasks']},
        'public_file_hashes': {name: manifest['files'][name] for name in ('inventory.json','provenance.json')},
        'hash_verification_scope': 'Manifest and candidate-final route tasks verified; inventory/provenance hashes recorded only.',
        'schedule': _schedule(groups), 'repeats': 2, 'regimes': list(REGIMES), 'arms': list(ARMS),
        'statistics': {'design': 'descriptive; not powered for a five-percentage-point improvement',
            'rough_20_group_binomial_margin_pp': 100*1.96*math.sqrt(.25/20),
            'margin_scope': 'Rough worst-case independent-binomial illustration only; not a paired/cluster interval.',
            'variance_gate': 'Measure development paired/cluster variance before final freeze.',
            'replicate_policy': 'Inventory siblings and LLM repeats do not add independent chemistry groups.',
            'seed_policy': 'Salted ordering is reproducible; LLM generations have no reproducible seed guarantee.'},
        'independence': {'scaffold_policy': 'Exact nonchiral Murcko clusters; all empty scaffolds share one conservative cluster.',
            'source_family_attestation': 'Not inferred from public target inputs; see cited existing curation receipt.',
            'limits': 'Target groups are not proven independent patent families or exhaustive chemical analogue groups.'},
        'matching_policy': 'Same hardware, tool/model versions, source permissions, candidate outcome access and top-k in both regimes; only aggregate research ceilings differ.',
        'release_gate': 'Commit ALL final decisions for ALL arms, repeats, inventories and BOTH regimes before opening any final answers.'}


def validate_cohort(value, public_root, manifest_sha256, *, count=20, expected_groups=50):
    """Analysis consumers must reject edited schedules, paths or added labels."""
    if value != build_cohort(public_root, manifest_sha256, count=count, expected_groups=expected_groups):
        raise ValueError('Provisional cohort differs from regenerated public-input-only design')
    return True
