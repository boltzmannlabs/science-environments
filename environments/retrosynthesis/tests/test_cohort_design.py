"""Public-input-only cohort selection never consults hidden route answers."""
import copy
import hashlib
import json
from pathlib import Path
import pytest
from synthesis_route_gym.cohort_design import build_cohort, validate_cohort


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True))
    return digest(path.read_bytes())


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / 'public'
    files = {'inventory.json': 'a'*64, 'provenance.json': 'b'*64}
    entries = []
    for number, target in enumerate(('CCO', 'CCC', 'c1ccccc1', 'c1ccncc1')):
        for variant in range(2):
            identity = f'route-{number}-{variant}'
            metadata = {'task_id': identity, 'partition': 'sealed_final', 'track': 'reference_route'}
            row = {**metadata, 'target': target, 'inventory_exclusions': [] if variant == 0 else ['O'],
                   'constraints': {'max_steps': 8}, 'budget': {'top_k': 5}}
            path = 'tasks/' + identity + '.json'
            files[path] = write(root/path, row)
            entries.append(metadata)
    manifest = {'schema_version': '1.0', 'bundle_kind': 'public', 'files': files, 'tasks': entries}
    anchor = write(root/'manifest.json', manifest)
    return root, anchor


def build(bundle, **kwargs):
    return build_cohort(*bundle, count=2, expected_groups=4, **kwargs)


def repin(root):
    manifest = json.loads((root/'manifest.json').read_text())
    for name in manifest['files']:
        if name.startswith('tasks/') and (root/name).is_file():
            manifest['files'][name] = digest((root/name).read_bytes())
    return write(root/'manifest.json', manifest)


def test_deterministic_selection_siblings_schedule_and_public_only_reads(bundle):
    result = build(bundle)
    assert result == build(bundle)
    assert len(result['groups']) == 2 and len(result['schedule']) == 48
    assert len(result['task_hashes']) == 4
    assert result['candidate_target_groups'] == 4
    assert len(result['candidate_groups']) == 4
    assert all(len(group['tasks']) == 2 for group in result['groups'])
    assert [g['selection_key'] for g in result['groups']] == sorted(
        digest(('srg12-final-v1:'+target).encode()) for target in ('CCO','CCC','c1ccccc1','c1ccncc1'))[:2]
    assert result['configuration_frozen'] is False
    assert not result['execution_authorized'] and not result['final_labels_opened']
    assert result['statistics']['rough_20_group_binomial_margin_pp'] == pytest.approx(21.913466, abs=.00001)
    blocks = {}
    for episode in result['schedule']:
        blocks.setdefault(episode['block_id'], []).append(episode)
    assert len(blocks) == 16
    for block in blocks.values():
        assert {e['arm'] for e in block} == {'main','strongest_fixed_pending_development','experimental_specialist_pending_development'}
        assert [e['arm_order_key'] for e in block] == sorted(e['arm_order_key'] for e in block)
    validate_cohort(result, *bundle, count=2, expected_groups=4)


def test_empty_scaffolds_share_conservative_cluster(bundle):
    rows = build(bundle)['candidate_groups']
    acyclic = [r for r in rows if r['target'] in {'CCO','CCC'}]
    assert len({r['scaffold_cluster_id'] for r in acyclic}) == 1
    assert all(r['scaffold_smiles'] == '' for r in acyclic)


@pytest.mark.parametrize('key', ['outcome','reference_routes','support_label','yield_percent','unknown'])
@pytest.mark.parametrize('nested', [False, True])
def test_forbidden_or_unknown_fields_fail_even_with_reanchored_hash(bundle, key, nested):
    root, _ = bundle
    path = root/'tasks/route-0-0.json'
    row = json.loads(path.read_text())
    (row['constraints'] if nested else row)[key] = 'injected'
    write(path, row)
    with pytest.raises(ValueError):
        build((root, repin(root)))


@pytest.mark.parametrize('mutation', ['hash','manifest_hash','duplicate','outside','symlink','task_id','partition','siblings','variant'])
def test_input_integrity_and_boundary_fail_closed(bundle, mutation):
    root, anchor = bundle
    manifest = json.loads((root/'manifest.json').read_text())
    path = root/'tasks/route-0-0.json'
    if mutation == 'hash':
        path.write_text(path.read_text()+' ')
    elif mutation == 'manifest_hash':
        anchor = '0'*64
    elif mutation == 'duplicate':
        manifest['tasks'].append(manifest['tasks'][0])
        anchor = write(root/'manifest.json',manifest)
    elif mutation == 'outside':
        manifest['files']['../private.json'] = '0'*64
        anchor = write(root/'manifest.json',manifest)
    elif mutation == 'symlink':
        outside = root.parent/'outside.json'
        outside.write_bytes(path.read_bytes())
        path.unlink();path.symlink_to(outside)
    elif mutation == 'siblings':
        manifest['tasks'] = manifest['tasks'][1:]
        del manifest['files']['tasks/route-0-0.json']
        anchor = write(root/'manifest.json',manifest)
    else:
        row = json.loads(path.read_text())
        if mutation == 'task_id':row['task_id'] = 'route-other'
        if mutation == 'partition':row['partition'] = 'development'
        if mutation == 'variant':row['inventory_exclusions'] = ['O']
        write(path,row);anchor=repin(root)
    with pytest.raises(ValueError):build((root,anchor))


@pytest.mark.parametrize('change', ['outcome','path','arm','freeze'])
def test_analysis_index_revalidates_all_fields(bundle, change):
    result = copy.deepcopy(build(bundle))
    if change == 'outcome':result['groups'][0]['support_label']=True
    if change == 'path':result['groups'][0]['tasks'][0]['path']='../private/answers.json'
    if change == 'arm':result['schedule'][0]['arm']='chosen_using_final_answers'
    if change == 'freeze':result['configuration_frozen']=True
    with pytest.raises(ValueError):validate_cohort(result,*bundle,count=2,expected_groups=4)


def test_invalid_selection_counts_and_duplicate_json(bundle):
    root, anchor=bundle
    for count in (True,0,5):
        with pytest.raises(ValueError):build_cohort(root,anchor,count=count,expected_groups=4)
    path=root/'tasks/route-0-0.json'
    path.write_text('{"task_id":"x","task_id":"y"}')
    with pytest.raises(ValueError):build((root,repin(root)))


def test_nonfinal_and_condition_tasks_are_never_loaded(bundle):
    root, _ = bundle
    manifest = json.loads((root/'manifest.json').read_text())
    for identity, partition, track in [('condition-missing','sealed_final','measured_conditions'),
                                       ('route-missing','development','reference_route')]:
        manifest['tasks'].append({'task_id':identity,'partition':partition,'track':track})
        manifest['files']['tasks/'+identity+'.json']='a'*64
    assert len(build((root,write(root/'manifest.json',manifest)))['schedule'])==48


@pytest.mark.parametrize('patch', [
    {'target':'not valid smiles'}, {'target':None}, {'inventory_exclusions':['O','O']},
    {'inventory_exclusions':{}}, {'budget':{'top_k':True}}, {'budget':{'top_k':0}},
    {'constraints':{'max_steps':True}}, {'constraints':{'forbidden_smiles':{'outcome':1}}},
    {'constraints':{'require_complete_conditions':'yes'}},
])
def test_malformed_public_inputs_fail_closed(bundle, patch):
    root, _=bundle
    path=root/'tasks/route-0-0.json'
    write(path,{**json.loads(path.read_text()),**patch})
    with pytest.raises(ValueError):build((root,repin(root)))


def test_expected_candidate_count_is_mandatory(bundle):
    with pytest.raises(ValueError):build_cohort(*bundle,count=2,expected_groups=5)
