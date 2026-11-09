"""Recompute comparisons from frozen outputs; never submit or run scientific jobs."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
import math
import statistics
import zipfile
import openpyxl
from rdkit import Chem
from rdkit.Chem import rdMolAlign
from rdkit.Chem import rdMolDescriptors
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]
TASK = 'task_001_d2r_peripheral_candidate_prioritisation'
RESULT = ROOT / 'results' / TASK
SUB = RESULT / 'submitted'
SUP = RESULT / 'supporting'
AUDIT = RESULT / 'audit'
BENCH = RESULT / 'benchmark_results'
REF = ROOT / 'benchmark' / TASK / 'reference'
AUDIT.mkdir(exist_ok=True)

def csv_rows(path):
    with path.open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))

def write_csv(path, records):
    assert records, path
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

def num(value):
    try:
        parsed = float(str(value).replace('\u2212', '-'))
        return parsed if math.isfinite(parsed) else None
    except (ValueError, TypeError):
        return None

def key(smiles):
    molecule = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(molecule) if molecule is not None else None

def heavy_topology(molecule):
    original = Chem.RemoveHs(molecule)
    graph = Chem.RWMol()
    for atom in original.GetAtoms():
        new_atom = Chem.Atom(atom.GetAtomicNum())
        new_atom.SetNoImplicit(True)
        graph.AddAtom(new_atom)
    for bond in original.GetBonds():
        graph.AddBond(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx(), Chem.BondType.SINGLE)
    return Chem.MolToSmiles(graph.GetMol(), isomericSmiles=False)

def workbook_records(path):
    book = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheet = book.worksheets[0]
    iterator = sheet.iter_rows(values_only=True)
    fields = next(iterator)
    return [dict(zip(fields, row)) for row in iterator]

def correlation(pairs):
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    if len(pairs) < 3:
        return {'n': len(pairs), 'pearson_r': None, 'spearman_rho': None}
    x, y = zip(*pairs)
    return {'n': len(pairs), 'pearson_r': float(pearsonr(x, y).statistic), 'spearman_rho': float(spearmanr(x, y).statistic)}

library = csv_rows(ROOT / 'inputs/library/compounds_400.csv')
by_id = {int(row['compound_id']): row for row in library}
integrated = csv_rows(SUB / 'integrated_raw.csv')
agent = {int(row['compound_id']): row for row in integrated}
ranked = csv_rows(SUB / 'ranked_candidates.csv')
reported_ids = [int(row['compound_id']) for row in ranked]
reported_priorities = [int(row['compound_id']) for row in ranked if row['priority'] == 'YES']
paper_s1 = workbook_records(REF / 's003.xlsx')
paper = {int(row['Molecule'].split()[-1]): row for row in paper_s1}
paper_s2 = workbook_records(REF / 's004.xlsx')
paper_dock = {int(row['compound no.']): row for row in paper_s2 if isinstance(row['compound no.'], (int, float))}
paper_score_field = 'AutoDock Vina docking score (kcal/mol)'
paper_reference = next(row for row in paper_s2 if not isinstance(row['compound no.'], (int, float)))
paper_reference_score = num(paper_reference[paper_score_field])
paper_hits = sorted(cid for cid, row in paper_dock.items() if num(row[paper_score_field]) is not None and num(row[paper_score_field]) < paper_reference_score)
paper_priorities = [128, 381]
paper_interaction = [27, 128, 360, 381]
paper_wrong_canonical = [cid for cid, row in paper.items() if row['Canonical SMILES'] and key(row['Canonical SMILES']) != key(row['SMILES CODE'])]
paper_missing_canonical = [cid for cid, row in paper.items() if not row['Canonical SMILES']]
paper_duplicate_prediction_rows = [cid for cid in range(2, 401) if list(paper[cid].values())[3:] == list(paper[cid-1].values())[3:] and key(paper[cid]['SMILES CODE']) != key(paper[cid-1]['SMILES CODE'])]

identity_checks = []
for cid, row in agent.items():
    source = by_id[cid]
    identity_checks.append({'compound_id': cid, 'zinc_id_match': row['zinc_id'] == source['zinc_id'] == paper[cid]['ZINC ID'], 'source_smiles_match': row['smiles_source'] == source['smiles'] == paper[cid]['SMILES CODE'], 'full_inchikey_match': key(row['smiles_source']) == source['inchikey'] == row['computed_inchikey']})
write_csv(AUDIT / 'input_identity_checks.csv', identity_checks)
duplicates = defaultdict(list)
for row in library:
    duplicates[row['inchikey']].append(int(row['compound_id']))
duplicate_groups = [ids for ids in duplicates.values() if len(ids) > 1]

raw_affinity = csv_rows(SUP / 'boltzmann/d2r_affinity_400.csv')
canonical_sequence = ''.join(line.strip() for line in (ROOT / 'inputs/targets/DRD2_P14416.fasta').read_text().splitlines() if not line.startswith('>'))
affinity_input_matches = len(raw_affinity) == 400 and all(key(row['smiles']) == by_id[index]['inchikey'] and row['sequence'] == canonical_sequence for index, row in enumerate(raw_affinity, 1))
affinity_integrated_matches = all(abs(float(row['binding_affinity']) - float(agent[index]['binding_affinity'])) < 1e-10 for index, row in enumerate(raw_affinity, 1))
controls = csv_rows(SUP / 'boltzmann/control_affinity_results.csv')
control_affinity = {('risperidone' if key(row['smiles']) == by_id[1]['inchikey'] else 'domperidone'): float(row['binding_affinity']) for row in controls}
control_primary = csv_rows(SUP / 'boltzmann/control_primary.csv')
control_caco = {('risperidone' if key(row['SMILES']) == by_id[1]['inchikey'] else 'domperidone'): float(row['CaCo2_permeability']) for row in control_primary}
ranking_expected = [cid for cid in sorted(agent, key=lambda cid: float(agent[cid]['binding_affinity'])) if by_id[cid]['inchikey'] != by_id[1]['inchikey']][:8]

raw_property = csv_rows(SUP / 'boltzmann/property_primary.csv')
property_failures = [index for index, row in enumerate(raw_property, 1) if num(row.get('BBB')) is None or num(row.get('HIA')) is None]
property_smiles_match = len(raw_property) == 400 and all(key(row['SMILES']) == by_id[index]['inchikey'] for index, row in enumerate(raw_property, 1))

vina_rows = csv_rows(SUP / 'boltzmann/vina_all_poses.csv')
vina_groups = defaultdict(list)
for row in vina_rows:
    vina_groups[int(row['NAMES'])].append(row)
vina_best = {cid: min(float(row['Score']) for row in rows) for cid, rows in vina_groups.items()}
vina_sorted = sorted(vina_best, key=lambda cid: (vina_best[cid], cid))
vina_rank = {cid: index for index, cid in enumerate(vina_sorted, 1)}
submitted_vina = csv_rows(SUB / 'vina_docking_results/vina_ranking.csv')
vina_consistency = all(abs(float(row['Score']) - vina_best[int(row['compound_id'])]) < 1e-9 for row in submitted_vina)

diff_raw = csv_rows(SUP / 'boltzmann/diffdock_all_poses.csv')
diff_groups = defaultdict(list)
diff_failures = []
for row in diff_raw:
    if num(row.get('Confidence')) is None:
        diff_failures.append(row)
    else:
        diff_groups[int(row['NAMES'])].append(row)
if diff_failures:
    write_csv(AUDIT / 'diffdock_rows_without_confidence.csv', diff_failures)
diff_reported = {int(row['compound_id']): num(row['diffdock_best']) for row in csv_rows(SUB / 'diffdock_mapped.csv')}
diff_corrected = []
for cid, poses in diff_groups.items():
    maximum = max(float(row['Confidence']) for row in poses)
    minimum = min(float(row['Confidence']) for row in poses)
    rank0 = next((float(row['Confidence']) for row in poses if int(row['Rank']) == 0), None)
    diff_corrected.append({'compound_id': cid, 'poses_returned': len(poses), 'reported_best_minimum': diff_reported.get(cid), 'raw_minimum': minimum, 'correct_best_maximum': maximum, 'rank0_confidence': rank0, 'reported_value_is_worst_pose': diff_reported.get(cid) is not None and math.isclose(diff_reported[cid], minimum, abs_tol=1e-7), 'correct_pose_confidence_band': 'high' if maximum > 0 else 'moderate' if maximum > -1.5 else 'low', 'binding_affinity_confirmed_by_confidence': False})
diff_corrected.sort(key=lambda row: row['correct_best_maximum'], reverse=True)
for index, row in enumerate(diff_corrected, 1):
    row['correct_cross_compound_confidence_rank_descriptive_only'] = index
write_csv(AUDIT / 'diffdock_confidence_audit.csv', diff_corrected)
diff_best = {row['compound_id']: row['correct_best_maximum'] for row in diff_corrected}

admet_records = []
with gzip.open(SUP / 'admetlab/admetlab3_bbb_results.jsonl.gz', 'rt') as stream:
    admet_records.extend(('local_main_response_snapshot', json.loads(line)) for line in stream if line.strip())
for name in ('admetlab3_tierA_retry.jsonl', 'admetlab3_control.jsonl'):
    admet_records.extend((name, json.loads(line)) for line in (SUB / name).read_text().splitlines() if line.strip())
admet_by_id = {}
admet_rows = []
admet_errors = []
endpoint_definitions = {}
admet_attempted_library_ids = set()
for origin, record in admet_records:
    cid = str(record.get('compound_id'))
    if cid.isdigit():
        admet_attempted_library_ids.add(int(cid))
    response = record.get('response', {})
    if response.get('status') != 'success' or not isinstance(response.get('data'), dict):
        admet_errors.append({'compound_id': cid, 'origin': origin, 'response_keys': list(response), 'error': response.get('error') or response.get('http_error')})
        continue
    payload = response['data']
    sections = payload.get('data', {})
    distribution = {item['name']: item['value'] for item in sections.get('distribution', [])}
    absorption = {item['name']: item['value'] for item in sections.get('absorption', [])}
    for items in sections.values():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get('name') in ('BCRP', 'BBB', 'HIA', 'caco2', 'pgp-substrate', 'pgp-inhibitor'):
                    endpoint_definitions[item['name']] = {field: item.get(field) for field in ('name', 'display', 'explanation')}
    # Preserve the service keys. Endpoint interpretation is taken from its
    # official documentation, never inferred from convenient numeric variation.
    row = {'compound_id': cid, 'origin': origin, 'returned_smiles': payload.get('raw_smiles') or payload.get('smiles'), 'BCRP_raw': distribution.get('BCRP'), 'BBB_raw': distribution.get('BBB'), 'HIA_raw': absorption.get('HIA'), 'Caco2_raw': absorption.get('caco2'), 'BCRP_endpoint_type': 'inhibitor classification; not a substrate/efflux measurement'}
    admet_rows.append(row)
    admet_by_id[cid] = row
write_csv(AUDIT / 'admet_response_audit.csv', admet_rows)
(AUDIT / 'endpoint_definitions_as_returned.json').write_text(json.dumps(endpoint_definitions, indent=2) + '\n')

tier_a = [cid for cid, row in agent.items() if float(row['binding_affinity']) <= control_affinity['domperidone']]
tier_report = csv_rows(SUB / 'tierA_strict_audit.csv')
dom_bcrp = num(admet_by_id.get('domperidone', {}).get('BCRP_raw'))
if dom_bcrp is None:
    # An explicit missing value remains missing; do not copy the reported cutoff.
    raise ValueError('Control BCRP was not located under the expected raw response key; inspect the response schema.')
bcrp_cutoff_ids = [cid for cid in tier_a if num(admet_by_id.get(str(cid), {}).get('BCRP_raw')) is not None and float(admet_by_id[str(cid)]['BCRP_raw']) >= dom_bcrp]

compound_comparison = []
for cid in range(1, 401):
    paper_score = num(paper_dock[cid][paper_score_field]) if cid in paper_dock else None
    compound_comparison.append({'compound_id': cid, 'zinc_id': by_id[cid]['zinc_id'], 'paper_BBB_permeant_SwissADME': paper[cid]['BBB permeant'], 'paper_GI_absorption_SwissADME': paper[cid]['GI absorption'], 'paper_Vina_score_kcal_mol': paper_score, 'paper_shortlisted_eight': cid in paper_hits, 'paper_interaction_four': cid in paper_interaction, 'paper_final_priority': cid in paper_priorities, 'agent_submitted_shortlist_rank': reported_ids.index(cid)+1 if cid in reported_ids else '', 'agent_submitted_priority': cid in reported_priorities, 'agent_NESSO_score_units_unestablished': num(agent[cid]['binding_affinity']), 'agent_Vina_best_kcal_mol': vina_best.get(cid), 'agent_Vina_rank_among_400': vina_rank.get(cid), 'Vina_score_difference_agent_minus_paper_protocol_dependent': vina_best[cid]-paper_score if cid in vina_best and paper_score is not None else '', 'agent_BBB_raw_label_uninterpreted': agent[cid].get('BBB'), 'agent_HIA_raw_label_uninterpreted': agent[cid].get('HIA'), 'agent_Caco2_raw_scale_requires_confirmation': agent[cid].get('CaCo2_permeability'), 'agent_ADMETlab_BCRP_inhibitor_score': admet_by_id.get(str(cid), {}).get('BCRP_raw', ''), 'agent_DiffDock_maximum_confidence': diff_best.get(cid, ''), 'biological_ground_truth_available': False})
write_csv(BENCH / 'compound_comparison.csv', compound_comparison)

def atoms(path, residue, number, names=None):
    result = []
    for line in path.read_text().splitlines():
        if line.startswith(('ATOM', 'HETATM')) and line[17:20].strip() == residue and int(line[22:26]) == number:
            name = line[12:16].strip()
            if names is None or name in names:
                result.append((name, (float(line[30:38]), float(line[38:46]), float(line[46:54]))))
    return result

receptor = SUP / 'preparation/6CM4_receptor_prep.pdb'
asp = atoms(receptor, 'ASP', 114, {'OD1', 'OD2'})
trp_c = atoms(receptor, 'TRP', 386, {'CG', 'CD1', 'CD2', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2'})
trp_all = atoms(receptor, 'TRP', 386, {'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2'})
assert len(asp) == 2 and len(trp_c) == 8
def distance(molecule, atom_ids, receptor_atoms):
    conf = molecule.GetConformer()
    values = [math.dist(tuple(conf.GetAtomPosition(index)), coordinate) for index in atom_ids for _, coordinate in receptor_atoms]
    return min(values) if values else None

geometry = []
pose_counts = {}
pose_identity = []
native_mol = next(molecule for molecule in Chem.SDMolSupplier(str(ROOT / 'inputs/controls/6CM4_8NU_chain_A_native.sdf'), removeHs=True) if molecule is not None)
native_rmsd = None
with zipfile.ZipFile(SUP / 'boltzmann/vina_poses.zip') as bundle:
    assert bundle.testzip() is None
    for name in bundle.namelist():
        if not name.endswith('.sdf'):
            continue
        cid = int(Path(name).stem.rsplit('_', 1)[1])
        molecules = list(Chem.ForwardSDMolSupplier(io.BytesIO(bundle.read(name)), removeHs=True))
        pose_counts[cid] = len(molecules)
        molecule = molecules[0]
        if molecule is None:
            pose_identity.append({'compound_id': cid, 'first_pose_readable': False, 'InChIKey_connectivity_block_matches': False, 'heavy_atom_topology_matches': False, 'formula_matches': False, 'source_formula': rdMolDescriptors.CalcMolFormula(Chem.MolFromSmiles(by_id[cid]['smiles'])), 'returned_formula': '', 'full_inchikey_matches': False})
            continue
        observed = Chem.MolToInchiKey(molecule)
        expected = by_id[cid]['inchikey']
        source_molecule = Chem.MolFromSmiles(by_id[cid]['smiles'])
        source_formula = rdMolDescriptors.CalcMolFormula(source_molecule)
        returned_formula = rdMolDescriptors.CalcMolFormula(molecule)
        pose_identity.append({'compound_id': cid, 'first_pose_readable': True, 'InChIKey_connectivity_block_matches': observed.split('-')[0] == expected.split('-')[0], 'heavy_atom_topology_matches': heavy_topology(source_molecule) == heavy_topology(molecule), 'formula_matches': source_formula == returned_formula, 'source_formula': source_formula, 'returned_formula': returned_formula, 'full_inchikey_matches': observed == expected})
        if cid == 1:
            try:
                native_rmsd = float(rdMolAlign.CalcRMS(molecule, native_mol))
            except RuntimeError:
                pass
        if cid in reported_ids:
            nitrogen = [atom.GetIdx() for atom in molecule.GetAtoms() if atom.GetAtomicNum() == 7]
            aromatic_carbon = [atom.GetIdx() for atom in molecule.GetAtoms() if atom.GetAtomicNum() == 6 and atom.GetIsAromatic()]
            geometry.append({'compound_id': cid, 'pose_index': 0, 'minimum_any_N_to_Asp114_OD_A': distance(molecule, nitrogen, asp), 'minimum_aromatic_C_to_Trp386_ring_C_A': distance(molecule, aromatic_carbon, trp_c), 'minimum_aromatic_C_to_Trp386_all_ring_atoms_A': distance(molecule, aromatic_carbon, trp_all), 'charge_state_and_salt_bridge_confirmed': False, 'ring_plane_geometry_and_pi_stacking_confirmed': False, 'calculated_by': 'reviewer from retained first Vina pose; not a new docking run'})
write_csv(AUDIT / 'vina_first_pose_identity_checks.csv', sorted(pose_identity, key=lambda row: row['compound_id']))
write_csv(AUDIT / 'pose_distance_recalculation.csv', sorted(geometry, key=lambda row: reported_ids.index(row['compound_id'])))
write_csv(AUDIT / 'same_model_absorption_comparison.csv', [
    {'compound_id': cid, 'library_Boltzmann_Caco2': num(agent[cid]['CaCo2_permeability']), 'risperidone_Boltzmann_Caco2': control_caco['risperidone'], 'domperidone_Boltzmann_Caco2': control_caco['domperidone'], 'difference_vs_domperidone_same_model': num(agent[cid]['CaCo2_permeability'])-control_caco['domperidone'], 'ratio_if_values_are_log10_Papp': 10**(num(agent[cid]['CaCo2_permeability'])-control_caco['domperidone']), 'interpretation': 'Higher log permeability means higher apparent permeability; ratios conditional on confirmed common log10 scale. This does not establish in-vivo absorption.'}
    for cid in reported_ids
])
pose_identity_by_id = {row['compound_id']: row for row in pose_identity}
for row in compound_comparison:
    cid = row['compound_id']
    row['paper_S1_prediction_identity_conflict'] = cid in paper_wrong_canonical
    row['paper_S1_incomplete_canonical_descriptor_record'] = cid in paper_missing_canonical
    row['agent_first_Vina_pose_heavy_atom_topology_matches'] = pose_identity_by_id[cid]['heavy_atom_topology_matches']
    row['agent_first_Vina_pose_formula_matches'] = pose_identity_by_id[cid]['formula_matches']
    row['agent_first_Vina_pose_full_inchikey_matches'] = pose_identity_by_id[cid]['full_inchikey_matches']
write_csv(BENCH / 'compound_comparison.csv', compound_comparison)
reviewed_candidates = []
for submitted in ranked:
    cid = int(submitted['compound_id'])
    reviewed_candidates.append({'reported_rank': submitted['rank'], 'compound_id': cid, 'reported_priority': submitted['priority'], 'reported_NESSO_score': submitted['binding_affinity'], 'NESSO_physical_energy_unit_established': False, 'reported_BCRP_score': submitted['admet_BCRP'], 'verified_BCRP_endpoint': 'inhibitor probability', 'peripheral_restriction_supported_by_BCRP': False, 'Boltzmann_Caco2': submitted['CaCo2_permeability'], 'same_model_domperidone_Caco2': control_caco['domperidone'], 'Vina_best_score_kcal_mol': vina_best[cid], 'returned_Vina_pose_formula_matches_source': pose_identity_by_id[cid]['formula_matches'], 'reported_DiffDock_confidence': submitted['diffdock_confidence'], 'correct_DiffDock_max_confidence': diff_best.get(cid, ''), 'review_status': 'Target-model prediction retained; peripheral-priority rationale requires scientific correction'})
write_csv(AUDIT / 'reviewed_candidate_evidence.csv', reviewed_candidates)

md_summary = []
md = openpyxl.load_workbook(REF / 's005.xlsx', read_only=True, data_only=True)
for sheet_name in ('Ligand_RMSD', 'Receptor_RMSD'):
    iterator = md[sheet_name].iter_rows(values_only=True)
    headers = next(iterator)
    data = list(iterator)
    for column, label in enumerate(headers[1:], 1):
        values = [float(row[column]) for row in data]
        md_summary.append({'sheet': sheet_name, 'system': label, 'points': len(values), 'mean_nm_recomputed': statistics.mean(values), 'sample_SD_nm_recomputed': statistics.stdev(values), 'start_ns': data[0][0], 'end_ns': data[-1][0], 'first_interval_ns': data[1][0]-data[0][0], 'agent_comparison': 'not applicable: MD excluded from the task execution scope'})
write_csv(BENCH / 'paper_MD_reference_only.csv', md_summary)

paired_vina = [(num(paper_dock[cid][paper_score_field]), vina_best.get(cid)) for cid in paper_dock]
all_vina_qspr = [(vina_best[cid], num(agent[cid]['binding_affinity'])) for cid in agent]
metrics = {
    'review_status': 'scientific_corrections_required; original submission retained',
    'new_scientific_jobs_run_by_this_review': 0,
    'library': {'records': len(library), 'distinct_full_inchikeys': len(duplicates), 'duplicate_record_groups': duplicate_groups, 'all_input_identity_checks_pass': all(all(row[field] for field in ('zinc_id_match', 'source_smiles_match', 'full_inchikey_match')) for row in identity_checks), 'submitted_task_exactly_matches_canonical_task': (RESULT / 'task_as_executed.md').read_bytes() == (ROOT / 'tasks' / (TASK + '.md')).read_bytes()},
    'paper': {'S1_records': len(paper_s1), 'docking_candidate_rows': len(paper_dock), 'numeric_docking_candidate_rows': sum(num(row[paper_score_field]) is not None for row in paper_dock.values()), 'missing_docking_score_ids': [cid for cid, row in paper_dock.items() if num(row[paper_score_field]) is None], 'reference_Vina_kcal_mol': paper_reference_score, 'strict_docking_hits': paper_hits, 'reference_score_ties': [cid for cid, row in paper_dock.items() if num(row[paper_score_field]) == paper_reference_score], 'interaction_selected_four': paper_interaction, 'final_priorities': paper_priorities, 'S1_conflicting_canonical_identity_ids': paper_wrong_canonical, 'S1_missing_canonical_identity_ids': paper_missing_canonical, 'S1_complete_prediction_payload_duplicates_preceding_row_ids': paper_duplicate_prediction_rows, 'S1_BBB_negative_count': sum(row['BBB permeant'] == 'No' for row in paper.values()), 'S1_BBB_negative_and_high_GI_count': sum(row['BBB permeant'] == 'No' and row['GI absorption'] == 'High' for row in paper.values())},
    'agent': {'reported_shortlist': reported_ids, 'reported_priorities': reported_priorities, 'ranked_rows': len(ranked), 'reported_order_matches_NESSO_sort_excluding_risperidone_identity': reported_ids == ranking_expected, 'NESSO_rows': len(raw_affinity), 'NESSO_rows_match_input_and_DRD2_sequence': affinity_input_matches, 'NESSO_values_match_integrated_table': affinity_integrated_matches, 'NESSO_units': 'not established; kcal/mol attribution in submission unsupported by the retained contract', 'control_NESSO_scores': control_affinity, 'library_risperidone_identity_score': num(agent[1]['binding_affinity']), 'property_rows': len(raw_property), 'property_input_identity_order_matches': property_smiles_match, 'property_non_numeric_endpoint_ids': property_failures, 'BBB_numeric_labels': dict(Counter(row['BBB'] for row in raw_property if num(row.get('BBB')) is not None)), 'HIA_numeric_labels': dict(Counter(row['HIA'] for row in raw_property if num(row.get('HIA')) is not None)), 'vina_pose_rows': len(vina_rows), 'vina_compounds': len(vina_groups), 'vina_pose_count_distribution': dict(Counter(len(rows) for rows in vina_groups.values())), 'vina_ranking_matches_raw_pose_minima': vina_consistency, 'vina_SDF_pose_count': sum(pose_counts.values()), 'vina_first_pose_InChIKey_connectivity_block_matches': sum(row['InChIKey_connectivity_block_matches'] for row in pose_identity), 'vina_first_pose_full_inchikey_matches': sum(row['full_inchikey_matches'] for row in pose_identity), 'reviewer_risperidone_fixed_frame_symmetry_RMSD_A': native_rmsd, 'diffdock_raw_table_rows': len(diff_raw), 'diffdock_numeric_pose_rows': sum(len(rows) for rows in diff_groups.values()), 'diffdock_rows_without_confidence': len(diff_failures), 'diffdock_compounds_with_returned_poses': len(diff_groups), 'final_shortlist_with_diffdock_data': sorted(set(reported_ids) & set(diff_groups)), 'final_shortlist_with_diffdock_count': len(set(reported_ids) & set(diff_groups)), 'reported_DiffDock_best_values_that_are_raw_minima': sum(row['reported_value_is_worst_pose'] for row in diff_corrected), 'ADMETlab_response_records_available': len(admet_records), 'ADMETlab_successful_distinct_library_ids': len([cid for cid in admet_by_id if cid.isdigit()]), 'ADMETlab_non_success_records': len(admet_errors), 'tier_A_model_threshold_ids': tier_a, 'tier_A_BCRP_values_supplied_in_strict_audit': sum(num(row['BCRP']) is not None for row in tier_report), 'tier_A_BCRP_values_available_after_raw_response_reconciliation': sum(num(admet_by_id.get(str(cid), {}).get('BCRP_raw')) is not None for cid in tier_a), 'domperidone_BCRP_inhibitor_score': dom_bcrp, 'tier_A_ids_meeting_literal_reported_BCRP_threshold': bcrp_cutoff_ids, 'note_on_BCRP_threshold': 'This is an inhibitor-score comparison, not valid evidence of brain efflux or BBB exclusion.'},
    'selection_agreement_descriptive_only': {'shortlist_intersection': sorted(set(paper_hits) & set(reported_ids)), 'shortlist_overlap_count': len(set(paper_hits) & set(reported_ids)), 'shortlist_reference_count': 8, 'final_priority_intersection': sorted(set(paper_priorities) & set(reported_priorities)), 'final_priority_overlap_count': len(set(paper_priorities) & set(reported_priorities)), 'final_priority_reference_count': 2, 'interpretation': 'Different selected sets do not establish biological inferiority; paper selections are computational outputs, not experimental truth.'},
    'correlations_descriptive_only': {'paper_Vina_vs_agent_Vina_on_available_common_ids': correlation(paired_vina), 'agent_Vina_vs_NESSO_all_library': correlation(all_vina_qspr), 'agent_NESSO_vs_DiffDock_reported_minimum': correlation([(num(agent[cid]['binding_affinity']), value) for cid, value in diff_reported.items()]), 'agent_NESSO_vs_DiffDock_correct_maximum': correlation([(num(agent[cid]['binding_affinity']), value) for cid, value in diff_best.items()])},
    'scope': {'MD_required_by_task': False, 'paper_MD_reproduction_claimed': False, 'task_MD_penalty': 'not applicable', 'direct_ADMETlab_used': True, 'Boltzmann_only_execution_certifiable': False, 'external_service_approval_evidence': 'not included in supplied ZIP; task.md itself does not specify provider restriction'},
}
metrics['agent'].update({
    'vina_first_pose_heavy_atom_topology_matches': sum(row['heavy_atom_topology_matches'] for row in pose_identity),
    'vina_first_pose_formula_matches': sum(row['formula_matches'] for row in pose_identity),
    'vina_first_pose_formula_mismatch_ids': [row['compound_id'] for row in pose_identity if not row['formula_matches']],
    'reference_pose_RMSD_unavailable_reason': 'Returned risperidone SDF does not match the native chemical graph; C23H29FN4O2 returned versus C23H27FN4O2 supplied. The location of the change in preparation or export cannot be determined from these files.',
    'same_model_Boltzmann_control_Caco2': control_caco,
    'ADMETlab_attempted_library_ids_represented_in_retained_records': len(admet_attempted_library_ids),
    'ADMETlab_no_successful_retained_response_ids': [cid for cid in range(1, 401) if str(cid) not in admet_by_id],
    'ADMETlab_successful_input_echo_identity_matches': all(key(row['returned_smiles']) == by_id[int(cid)]['inchikey'] for cid, row in admet_by_id.items() if cid.isdigit()),
    'enantiomers_2_and_3_are_distinct_full_inchikeys': by_id[2]['inchikey'] != by_id[3]['inchikey'],
    'raw_endpoint_definitions': 'results/' + TASK + '/audit/endpoint_definitions_as_returned.json',
})
(BENCH / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
(AUDIT / 'admet_non_success_records.json').write_text(json.dumps(admet_errors, indent=2) + '\n')
print(json.dumps(metrics, indent=2))
