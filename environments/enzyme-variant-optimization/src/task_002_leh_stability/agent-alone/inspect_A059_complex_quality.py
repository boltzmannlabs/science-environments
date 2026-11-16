# Archived agent code: workspace paths and private input-key literals are parameterized.
def _publication_input_key(variable):
    import os
    if variable not in os.environ:
        raise RuntimeError('Set ' + variable + ' to the exact archived input_path expected by this verification.')
    return os.environ[variable]
'Inspect actual A059 artifacts and derive descriptive component-linked summaries. No scientific dispatch or input repair.'
import pathlib, json, csv, io, zipfile, hashlib, collections, math, re
import gemmi
R = pathlib.Path(__file__).resolve().parent
load = lambda f: json.loads((R / f).read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(f, v):
    p = R / f
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=2) + '\n')
archive = R / 'raw/A059/results.zip'
z = zipfile.ZipFile(archive)
review = load('NEXT_COMPLEX_INPUT_REVIEW_REQUEST.json')
expected = {e['archive_member']: e for e in review['structures']}
manifest = json.loads(z.read('manifest.json'))
thresholds = json.loads(z.read('quality_thresholds_used.json'))
summary = list(csv.DictReader(io.StringIO(z.read('candidate_summary.csv').decode())))
invalid = list(csv.DictReader(io.StringIO(z.read('invalid_candidates.csv').decode())))
outliers = list(csv.DictReader(io.StringIO(z.read('validation_outliers.csv').decode())))
assert manifest['counts'] == {'invalid': 0, 'measured': 11, 'passed': 0, 'rejected': 0, 'total': 11} and len(summary) == 11 and (not invalid)
assert thresholds == {} and manifest['execution_mode'] == 'measurement_only'
assert manifest['input_path'] == _publication_input_key('MOLPROBITY_INPUT_KEY_80BA701903DA')
assert set((x['source_name'] for x in summary)) == set(expected) and len({x['candidate_id'] for x in summary}) == 11
for info in z.infolist():
    p = pathlib.PurePosixPath(info.filename)
    assert not p.is_absolute() and '..' not in p.parts and (not info.filename.startswith('\\')) and (p.suffix in ['.json', '.csv'])
    dest = R / 'raw/A059/extracted' / info.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(z.read(info.filename))
rows = []
comparisons = []
all_ligand_contacts = []
all_water_contacts = []
per_candidate = []
metric_observations = []
maxcoorderror = 0
coordschecked = 0
reg = load('current_candidate_registry.json')
records = {x['candidate_id']: x for x in [reg['parent']] + reg['valid_initial'] + reg['valid_revision1']}
for s in summary:
    e = expected[s['source_name']]
    cid = e['candidate_id']
    native = s['candidate_id']
    p = pathlib.Path(e['path'])
    assert sha(p) == e['sha256']
    assert native == pathlib.Path(s['source_name']).stem and s['status'] == 'measured' and (not s['error']) and (not s['failed_thresholds'])
    model = gemmi.read_structure(str(p))
    assert len(model) == 1
    source = {}
    residues = set()
    for ch in model[0]:
        for res in ch:
            residues.add((ch.name, res.seqid.num, res.seqid.icode.strip(), res.name))
            for at in res:
                source[ch.name, res.seqid.num, res.seqid.icode.strip(), res.name, at.name] = (at.element.name, [at.pos.x, at.pos.y, at.pos.z])
    assert len(source) == int(s['atom_count']) and len(residues) == int(s['residue_count']) == 302 and (int(s['model_count']) == 1)
    bonddata = json.loads(z.read(f'raw_json/{native}/bonds_angles.json'))
    clashdata = json.loads(z.read(f'raw_json/{native}/clashscore2.json'))
    clashes = clashdata['outlier_results']
    assert len(clashes) == int(s['num_clashes'])
    observedcounts = collections.Counter((x['validator'] for x in outliers if x['candidate_id'] == native))
    assert observedcounts['clashscore2'] == len(clashes)
    geometry_counts = {}
    localchecks = 0
    localerror = 0
    for key, col, validator in [('mp_bonds', 'bond_outliers', 'bonds'), ('mp_angles', 'angle_outliers', 'angles')]:
        data = bonddata[key]
        totals = list(data['summary_results'].values())
        assert len(totals) == 1
        tot = totals[0]
        assert tot['num_outliers'] == int(s[col]) == len(data['outlier_results']) == observedcounts[validator]
        geometry_counts[key] = tot
        for item in data['outlier_results']:
            for ch, resn, ic, rn, an, el, xyz in zip(item['atoms_chain_id'], item['atoms_resseq'], item['atoms_icode'], item['atoms_resname'], item['atoms_name'], item['atoms_element'], item['atoms_xyz']):
                k = (ch.strip(), int(resn), ic.strip(), rn.strip(), an.strip())
                assert k in source and source[k][0] == el.strip()
                err = max((abs(a - b) for a, b in zip(xyz, source[k][1])))
                assert err < 1e-08
                localerror = max(localerror, err)
                localchecks += 1
    stats = collections.Counter()
    missing = []
    ligand = []
    water = []
    native_hydrogen_atom_references = 0
    for item in clashes:
        a = item.get('resname', '').strip()
        b = item.get('target_resname', '').strip()
        names = {a, b}
        if names == {'GH9', 'HOH'}:
            category = 'water_ligand'
        elif 'GH9' in names:
            category = 'ligand_ligand' if a == b == 'GH9' else 'protein_ligand'
        elif 'HOH' in names:
            category = 'water_water' if a == b == 'HOH' else 'protein_water'
        else:
            category = 'protein_protein'
        stats[category] += 1
        isH = []
        for pref in ['', 'target_']:
            name = item[pref + 'name'].strip()
            key = (item[pref + 'chain_id'].strip(), int(item[pref + 'resseq']), item[pref + 'icode'].strip(), item[pref + 'resname'].strip(), name)
            if key in source:
                isH.append(source[key][0] in ['H', 'D'])
            elif re.match('^[0-9]*[HD]', name):
                isH.append(True)
                native_hydrogen_atom_references += 1
            else:
                isH.append(False)
                missing.append(key)
        stats['H_containing_clash_rows' if any(isH) else 'all_heavy_clash_rows'] += 1
        entry = {'candidate_id': cid, 'native_candidate_id': native, 'category': category, 'contains_native_generated_H_reference': any(isH), 'native_record': item}
        if 'GH9' in names:
            ligand.append(entry)
            all_ligand_contacts.append(entry)
        if names == {'GH9', 'HOH'}:
            water.append(entry)
            all_water_contacts.append(entry)
    assert not missing
    assert sum((stats[k] for k in ['water_ligand', 'ligand_ligand', 'protein_ligand', 'water_water', 'protein_water', 'protein_protein'])) == len(clashes)
    rawmetrics = {k: float(v) for k, v in s.items() if k not in ['candidate_id', 'source_name', 'status', 'failed_thresholds', 'error']}
    assert all((math.isfinite(v) and v >= 0 for v in rawmetrics.values()))
    apo = load(f'structure_evidence/{cid}/molprobity_apo_qa.json')
    old = apo['summary']
    comparison = {'candidate_id': cid, 'native_candidate_id': native, 'complete_complex_clashscore': float(s['clashscore']), 'apo_clashscore': float(old['clashscore']), 'complete_complex_minus_apo_clashscore': float(s['clashscore']) - float(old['clashscore']), 'native_num_clashes': int(s['num_clashes']), 'apo_num_clashes': int(old['num_clashes']), 'protein_ligand_clash_rows': stats['protein_ligand'], 'water_ligand_clash_rows': stats['water_ligand'], 'all_ligand_related_clash_rows': len(ligand), 'all_heavy_clash_rows': stats['all_heavy_clash_rows'], 'H_containing_clash_rows': stats['H_containing_clash_rows'], 'ramachandran_outliers': int(s['ramachandran_outliers']), 'rotamer_outliers': int(s['rotamer_outliers']), 'bond_outliers': int(s['bond_outliers']), 'angle_outliers': int(s['angle_outliers']), 'other_bonds_evaluated': geometry_counts['mp_bonds']['num_total_other'], 'other_angles_evaluated': geometry_counts['mp_angles']['num_total_other'], 'other_bond_outliers': geometry_counts['mp_bonds']['num_outliers_other'], 'other_angle_outliers': geometry_counts['mp_angles']['num_outliers_other'], 'minimum_ligand_related_native_signed_overlap': min((x['native_record']['overlap'] for x in ligand)) if ligand else None}
    comparisons.append(comparison)
    qp = f'structure_evidence/{cid}/molprobity_complete_complex_qa.json'
    qa = {'candidate_id': cid, 'attempt_id': 'A059', 'job_name': 'Mol_Probity', 'doc_id': 'JOB_0100', 'native_candidate_id': native, 'source_name': s['source_name'], 'source_structure_path': str(p), 'source_structure_sha256': e['sha256'], 'input_archive_sha256': review['proposed_operation']['sha256'], 'raw_archive_sha256': sha(archive), 'native_status': s['status'], 'summary': s, 'manifest': manifest, 'quality_thresholds_used': thresholds, 'native_raw_member_prefix': f'raw_json/{native}/', 'native_bond_angle_totals': geometry_counts, 'clash_categories': dict(stats), 'source_selector_and_heavy_atom_name_checks': True, 'native_clash_H_refs_not_in_input': native_hydrogen_atom_references, 'reported_bond_angle_outlier_atom_coordinate_checks': localchecks, 'reported_coordinate_max_absolute_difference_A': localerror, 'all_ligand_related_native_clash_records': ligand, 'all_native_water_ligand_clash_records': water, 'limitations': ['Measured, not passed; no caller-selected quality thresholds.', 'Clashscore2 regenerated/optimized H internally; no prepared H-containing receptor/complex was exported.', 'This does not verify reactive Asp101 protonation, catalytic-water H/orientation or free-terminal OXT completion.', 'Input source hash is a locally verified provenance link; worker did not return a hash of every source member or a processed structure.', 'Ordinary GH9 atoms and water are represented in actual native validator records; this does not establish complete ligand chemistry or experimental catalysis.', 'Full-complex QA covers only11assembled primary-pose scenes (22ligands), not all188parent/variant docking alternatives.', 'Raw overlap sign/field values retained; no new numerical catalytic or quality acceptance bounds invented.']}
    save(qp, qa)
    per_candidate.append({'candidate_id': cid, 'qa_path': qp, 'status': 'measured', 'source_structure_sha256': e['sha256']})
    for k, v in rawmetrics.items():
        if k.endswith('_percent'):
            unit = 'percent'
        elif k == 'clashscore':
            unit = 'native_MolProbity_clashscore'
        else:
            unit = 'count'
        metric_observations.append({'candidate_id': cid, 'sequence_sha256': records[cid]['sequence_sha256'], 'metric': 'complete_complex_' + k, 'value': v, 'unit': unit, 'method': 'Mol_Probity measurement_only; A059; assembled native-primary pair', 'round': 'parent' if cid == 'LEH_PARENT' else 1 if cid.startswith('LEH_R') else 0, 'evidence_path': qp, 'uncertainty': 'not_reported', 'notes': 'Native measured-only, thresholds omitted. Reduce2/Probe2 H policy is not verified assay-specific reactive preparation.'})
    coordschecked += localchecks
    maxcoorderror = max(maxcoorderror, localerror)
parent = next((x for x in comparisons if x['candidate_id'] == 'LEH_PARENT'))
for row in comparisons:
    row['clashscore_delta_matched_parent'] = row['complete_complex_clashscore'] - parent['complete_complex_clashscore']
with (R / 'complete_complex_quality_comparison.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(comparisons[0]))
    w.writeheader()
    w.writerows(comparisons)
for name, entries in [('all_ligand_related_native_clashes.json', all_ligand_contacts), ('all_water_ligand_native_clashes.json', all_water_contacts)]:
    save('structure_evidence/' + name, entries)
obs = list(csv.DictReader((R / 'observations.csv').open()))
fields = list(obs[0])
keys = {(x['candidate_id'], x['metric'], x['method'], x['evidence_path']) for x in obs}
for row in metric_observations:
    k = tuple((row[x] for x in ['candidate_id', 'metric', 'method', 'evidence_path']))
    if k not in keys:
        obs.append(row)
        keys.add(k)
with (R / 'observations.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(obs)
result = {'attempt_id': 'A059', 'doc_id': 'JOB_0100', 'status': 'ARTIFACT_IDENTITY_COUNTS_AND_NATIVE_MEASUREMENTS_VERIFIED', 'provider_status': 'Success', 'native_counts': manifest['counts'], 'structure_count': 11, 'summary_rows': len(summary), 'invalid_rows': len(invalid), 'native_outlier_rows': len(outliers), 'archive_members': len(z.infolist()), 'archive_path': str(archive), 'archive_sha256': sha(archive), 'all11_input_member_and_source_identity_joins': True, 'execution_mode': 'measurement_only', 'quality_thresholds_used': thresholds, 'engine_version': manifest['engine_version'], 'hydrogen_policy': manifest['hydrogen_policy'], 'reported_bond_angle_outlier_atom_coordinate_checks': coordschecked, 'reported_coordinate_max_absolute_difference_A': maxcoorderror, 'all_ligand_related_clash_rows': len(all_ligand_contacts), 'all_water_ligand_clash_rows': len(all_water_contacts), 'per_candidate': per_candidate, 'comparisons': comparisons, 'scientific_acceptance': False, 'workflow_complete': False, 'reactive_protonation_water_H_and_terminal_completion_unverified': True, 'no_new_scientific_submission_for_QA': True}
save('structure_evidence/complete_complex_quality_A059_qa.json', result)
print(json.dumps({k: result[k] for k in ['status', 'native_counts', 'archive_members', 'native_outlier_rows', 'reported_bond_angle_outlier_atom_coordinate_checks', 'reported_coordinate_max_absolute_difference_A', 'all_ligand_related_clash_rows', 'all_water_ligand_clash_rows']}, indent=2))
print(json.dumps(comparisons, indent=2))
