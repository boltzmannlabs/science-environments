# Archived agent code: workspace paths and private input-key literals are parameterized.
def _publication_input_key(variable):
    import os
    if variable not in os.environ:
        raise RuntimeError('Set ' + variable + ' to the exact archived input_path expected by this verification.')
    return os.environ[variable]
'Inspect actual A076 results and candidate-linked coordinates; never prepare or submit.'
import collections
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import stat
import zipfile
import gemmi
R = Path(__file__).resolve().parent
A = R / 'raw/A076'
archive = A / 'results.zip'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
request = json.loads((R / 'A076_TEN_MATCHED_VARIANT_QUALITY_OPERATION_REVIEW.json').read_text())
assert sha(archive) == '8d4333e5fdae13d6fb524bf3794fa4eaa1c74e4ada69b1400efda1aeed72dcae'
source_by_member = {s['archive_member']: s for s in request['structures']}
assert len(source_by_member) == 10
parent = json.loads((R / 'raw/A065/artifact_QA.json').read_text())
old_rows = list(csv.DictReader((R / 'raw/A059/extracted/candidate_summary.csv').open()))

def source_lookup(path):
    table = gemmi.cif.read_file(str(path)).sole_block().find_mmcif_category('_atom_site.')
    c = {tag.split('.', 1)[1]: i for i, tag in enumerate(table.tags)}
    atoms = {}
    for row in table:
        insertion = row[c['pdbx_PDB_ins_code']]
        key = (row[c['auth_asym_id']], row[c['auth_seq_id']], '' if insertion in ('.', '?') else insertion, row[c['label_comp_id']], row[c['label_atom_id']])
        assert key not in atoms
        atoms[key] = {'element': row[c['type_symbol']], 'xyz': [float(row[c[n]]) for n in ('Cartn_x', 'Cartn_y', 'Cartn_z')]}
        assert all((math.isfinite(v) for v in atoms[key]['xyz']))
    return atoms

def endpoint(record, prefix=''):
    return tuple((str(record[prefix + name] or '').strip() for name in ('chain_id', 'resseq', 'icode', 'resname', 'name')))

def endpoint_element(key, lookup):
    if key in lookup:
        return (lookup[key]['element'], 'exact_source_atom')
    if key[-1].lstrip('0123456789').startswith('H'):
        return ('H', 'validator_H_name_inference_not_source_state')
    return (None, 'unmapped_native_atom')
with zipfile.ZipFile(archive) as z:
    members = z.infolist()
    assert len({i.filename for i in members}) == len(members)
    inventory = []
    for info in members:
        p = PurePosixPath(info.filename)
        assert not p.is_absolute() and '..' not in p.parts
        assert not stat.S_ISLNK(info.external_attr >> 16)
        data = z.read(info)
        target = A / 'extracted' / info.filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == data
        else:
            target.write_bytes(data)
        inventory.append({'member': info.filename, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    summary = list(csv.DictReader(io.StringIO(z.read('candidate_summary.csv').decode())))
    invalid = list(csv.DictReader(io.StringIO(z.read('invalid_candidates.csv').decode())))
    outliers = list(csv.DictReader(io.StringIO(z.read('validation_outliers.csv').decode())))
    manifest = json.loads(z.read('manifest.json'))
    thresholds = json.loads(z.read('quality_thresholds_used.json'))
    assert len(summary) == 10 and invalid == []
    assert set((r['source_name'] for r in summary)) == set(source_by_member)
    assert len({r['candidate_id'] for r in summary}) == 10
    assert manifest['counts'] == {'invalid': 0, 'measured': 10, 'passed': 0, 'rejected': 0, 'total': 10}
    assert manifest['execution_mode'] == 'measurement_only' and thresholds == {}
    assert manifest['custom_ligand_bindings'] == 0
    assert manifest['input_path'] == _publication_input_key('MOLPROBITY_INPUT_KEY_6CEDE97613EE')
    rows = []
    native_rows = []
    total_references = 0
    global_classes = {'bonds': collections.Counter(), 'angles': collections.Counter()}
    native_clash_rows = []
    for row in summary:
        source = source_by_member[row['source_name']]
        assert row['candidate_id'] == Path(source['archive_member']).stem
        assert row['status'] == 'measured' and row['error'] == ''
        assert int(row['atom_count']) == source['total_atoms']
        assert int(row['residue_count']) == 302 and int(row['model_count']) == 1
        path = Path(source['output_path'])
        assert sha(path) == source['output_sha256']
        lookup = source_lookup(path)
        assert len(lookup) == source['total_atoms']
        prefix = 'raw_json/' + row['candidate_id'] + '/'
        bonds_angles = json.loads(z.read(prefix + 'bonds_angles.json'))
        clashes = json.loads(z.read(prefix + 'clashscore2.json'))
        classes = {}
        refs = exact = rounded = 0
        maximum_delta = 0.0
        oxt_angle_outliers = 0
        for raw_key, label, summary_key in (('mp_bonds', 'bonds', 'bond_outliers'), ('mp_angles', 'angles', 'angle_outliers')):
            records = bonds_angles[raw_key]['outlier_results']
            assert len(records) == int(row[summary_key])
            counts = collections.Counter()
            target_ranges = collections.defaultdict(list)
            for record in records:
                elements = [x.strip() for x in record['atoms_element']]
                has_h = 'H' in elements
                category = 'H_containing' if has_h else 'all_heavy'
                counts[category] += 1
                protein = all((x.strip() not in ('GH9', 'HOH') for x in record['atoms_resname']))
                counts[('protein_' if protein else 'nonprotein_') + category] += 1
                if has_h:
                    target_ranges['protein' if protein else 'nonprotein'].append(record['target'])
                if label == 'angles' and 'OXT' in [x.strip() for x in record['atoms_name']]:
                    oxt_angle_outliers += 1
                for i, actual_xyz in enumerate(record['atoms_xyz']):
                    key = (record['atoms_chain_id'][i].strip(), record['atoms_resseq'][i].strip(), record['atoms_icode'][i].strip(), record['atoms_resname'][i].strip(), record['atoms_name'][i].strip())
                    assert key in lookup, (source['candidate_id'], key)
                    expected = lookup[key]
                    assert elements[i] == expected['element']
                    delta = max((abs(a - b) for a, b in zip(actual_xyz, expected['xyz'])))
                    assert math.isfinite(delta)
                    maximum_delta = max(maximum_delta, delta)
                    refs += 1
                    if delta < 1e-10:
                        exact += 1
                    else:
                        assert delta <= 0.000500001, (key, delta)
                        assert all((abs(v * 1000 - round(v * 1000)) < 1e-07 for v in actual_xyz))
                        rounded += 1
            global_classes[label].update(counts)
            classes[label] = {'counts': dict(counts), 'native_H_targets': {k: {'minimum': min(v), 'maximum': max(v)} for k, v in target_ranges.items()}}
        records = clashes['outlier_results']
        assert len(records) == int(row['num_clashes'])
        contact_categories = collections.Counter()
        element_provenance = collections.Counter()
        for record in records:
            one, two = (endpoint(record), endpoint(record, 'target_'))
            elements = []
            for atom in (one, two):
                element, provenance = endpoint_element(atom, lookup)
                elements.append(element)
                element_provenance[provenance] += 1
            kinds = sorted(('ligand' if key[3] == 'GH9' else 'water' if key[3] == 'HOH' else 'protein' for key in (one, two)))
            category = '_'.join(kinds)
            contact_categories[category] += 1
            h_category = 'H_containing' if 'H' in elements else 'unmapped_element' if None in elements else 'all_heavy'
            contact_categories[category + ':' + h_category] += 1
            if category != 'protein_protein':
                native_clash_rows.append({'candidate_id': source['candidate_id'], 'native_candidate_id': row['candidate_id'], 'source_atom': list(one), 'target_atom': list(two), 'element_classification': h_category, 'native_overlap': record['overlap'], 'native_record': record})
        per_model_table = [r for r in outliers if r['candidate_id'] == row['candidate_id']]
        validator_counts = collections.Counter((r['validator'] for r in per_model_table))
        for key, expected in (('bonds', int(row['bond_outliers'])), ('angles', int(row['angle_outliers'])), ('clashscore2', int(row['num_clashes']))):
            assert validator_counts[key] == expected
        raw_counts = {}
        for validator in ('cablam', 'cbetadev', 'omegalyze', 'ramalyze', 'rotalyze'):
            raw = json.loads(z.read(prefix + validator + '.json'))
            assert isinstance(raw, dict)
            if isinstance(raw.get('outlier_results'), list):
                raw_counts[validator] = len(raw['outlier_results'])
                assert validator_counts[validator] == len(raw['outlier_results'])
            else:
                raw_counts[validator] = {'schema_keys': list(raw), 'rows_not_inferred': True}
        old = [r for r in old_rows if r['source_name'] == 'structures/' + source['candidate_id'] + '_native_primary_pair.cif']
        assert len(old) == 1
        record = {'candidate_id': source['candidate_id'], 'native_candidate_id': row['candidate_id'], 'producer_attempt': source['producer_attempt'], 'source_member': row['source_name'], 'source_sha256': source['output_sha256'], 'native_summary': row, 'bond_angle_classification': classes, 'OXT_angle_outlier_rows': oxt_angle_outliers, 'source_atom_references_checked': refs, 'exact_coordinate_matches': exact, 'PDB_precision_coordinate_matches': rounded, 'maximum_delta_A': maximum_delta, 'clash_categories': dict(contact_categories), 'clash_atom_element_provenance': dict(element_provenance), 'native_outlier_table_rows': len(per_model_table), 'validator_counts': dict(validator_counts), 'raw_validator_record_counts': raw_counts, 'older_Hfree_A059_summary': old[0], 'parent_A065_clashscore_difference_descriptive': float(row['clashscore']) - float(parent['native_summary']['clashscore']), 'source_state_and_worker_H_policy_distinct': True}
        native_rows.append(record)
        rows.append({'candidate_id': source['candidate_id'], 'native_candidate_id': row['candidate_id'], 'source_member': row['source_name'], 'status': row['status'], 'atom_count': row['atom_count'], 'clashscore': row['clashscore'], 'num_clashes': row['num_clashes'], 'rama_outliers': row['ramachandran_outliers'], 'rotamer_outliers': row['rotamer_outliers'], 'bond_H_outliers': classes['bonds']['counts'].get('H_containing', 0), 'bond_heavy_outliers': classes['bonds']['counts'].get('all_heavy', 0), 'angle_H_outliers': classes['angles']['counts'].get('H_containing', 0), 'angle_heavy_outliers': classes['angles']['counts'].get('all_heavy', 0), 'OXT_angle_outliers': oxt_angle_outliers})
        total_references += refs
assert sum((r['native_outlier_table_rows'] for r in native_rows)) == len(outliers)
result = {'attempt_id': 'A076', 'job_name': 'Mol_Probity', 'doc_id': 'JOB_0103', 'technical_status': 'Success_archive_verified_measured_not_passed', 'archive_sha256': sha(archive), 'archive_members': len(inventory), 'inventory': inventory, 'native_manifest': manifest, 'thresholds_used': thresholds, 'summary_rows': len(summary), 'invalid_rows': len(invalid), 'outlier_table_rows': len(outliers), 'candidate_evidence': native_rows, 'total_source_atom_references_checked': total_references, 'global_bond_angle_classification': {k: dict(v) for k, v in global_classes.items()}, 'full_processed_structure_not_exported': True, 'limitations': ['Measured is not passed; no supplied quality thresholds or catalytic bounds.', 'clashscore2 regenerates/optimizes H with Reduce2/Probe2; no frozen source H/protonation/orientation certification.', 'Bonded-H reference conventions differ from native physical/nuclear force-field geometry; raw H outlier totals are not mutant effects.', 'Candidate source joins use exact members, local source hashes, counts and actual coordinate references. Worker does not echo full source-file hashes.', 'Original heavy poses are unchanged. Joint reactive geometry, binding, catalysis, stability and eligibility are not certified.', 'All adverse findings and original Hfree/A065 baselines are retained; no reranking of native ligand poses.']}
(A / 'artifact_QA.json').write_text(json.dumps(result, indent=2) + '\n')
(R / 'structure_evidence/A076_nonprotein_native_clashes.json').write_text(json.dumps(native_clash_rows, indent=2) + '\n')
with (R / 'A076_matched_quality_comparison.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(json.dumps({'attempt_id': 'A076', 'archive_sha256': result['archive_sha256'], 'measured': len(summary), 'invalid': len(invalid), 'passed': 0, 'raw_outlier_rows': len(outliers), 'source_atom_references': total_references, 'global_bond_angle_counts': result['global_bond_angle_classification'], 'candidate_comparison_rows': rows}, indent=2))
