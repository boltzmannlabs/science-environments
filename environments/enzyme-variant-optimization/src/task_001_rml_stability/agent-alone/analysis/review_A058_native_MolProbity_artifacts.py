"""Review A058 native artifacts only; no molecular validator, optimization or inference.

All classifications are returned CCTBX findings. Local calculations reconcile tables,
counts and unchanged input addresses/coordinates, never create quality predictions.
"""
import collections
import csv
import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import zipfile

ARM=Path(__file__).resolve().parents[1]
RAW=ARM/'raw/A058_minimized_parent_MolProbity'
EXT=RAW/'extracted'
OUT=ARM/'analysis/A058_minimized_parent_MolProbity'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def native_summary(data):
    summaries=data['summary_results']
    if set(summaries)!={''}:
        raise ValueError('Unexpected native model summary keys')
    return summaries['']


def finite_records(value):
    if isinstance(value,float):
        return math.isfinite(value)
    if isinstance(value,list):
        return all(finite_records(x) for x in value)
    if isinstance(value,dict):
        return all(finite_records(x) for x in value.values())
    return True


def main():
    if OUT.exists():
        raise RuntimeError('Review directory already exists; inspect retained QA rather than overwrite')
    request=load(ARM/'native_evidence/RML_POST_A057_MOLPROBITY_MEASUREMENT_REVIEW_REQUEST.json')
    source=Path(request['exact_local_input']['path'])
    checks={}
    def check(name,result):
        checks[name]=bool(result)
    check('exact_request_and_source_input',sha(ARM/'native_evidence/RML_POST_A057_MOLPROBITY_MEASUREMENT_REVIEW_REQUEST.json')=='4eca4496bc922c82d2ea6dbeadde8bff8a0e2a7d55178503abd8e9fb300a031b' and sha(source)==request['exact_local_input']['sha256'])
    with zipfile.ZipFile(RAW/'results.zip') as archive:
        members={i.filename:archive.read(i) for i in archive.infolist() if not i.is_dir()}
    actual={str(p.relative_to(EXT)):p.read_bytes() for p in EXT.rglob('*') if p.is_file()}
    check('every_actual_archive_member_preserved_exact',len(members)==12 and members==actual)
    csvs={k:list(csv.DictReader(io.StringIO(v.decode('utf-8-sig')))) for k,v in members.items() if k.endswith('.csv')}
    js={k:json.loads(v) for k,v in members.items() if k.endswith('.json')}
    manifest=js['manifest.json'];thresholds=js['quality_thresholds_used.json']
    check('all9_JSON3_CSV_artifacts_parsed',len(js)==9 and len(csvs)==3)
    summary=csvs['candidate_summary.csv']
    check('one_measured_summary_zero_invalid_thresholds_omitted',len(summary)==1 and summary[0]['status']=='measured' and len(csvs['invalid_candidates.csv'])==0 and thresholds=={} and manifest['counts']=={'invalid':0,'measured':1,'passed':0,'rejected':0,'total':1})
    row=summary[0]
    check('native_source_coverage_and_input_join',row['source_name']==source.name and row['candidate_id']==source.stem and int(row['model_count'])==1 and int(row['atom_count'])==4808 and int(row['residue_count'])==507 and manifest['input_path']==request['actual_upload']['storage_path'])
    raw={Path(k).stem:v for k,v in js.items() if k.startswith('raw_json/')}
    check('all_seven_native_validator_outputs_present',set(raw)=={'bonds_angles','cablam','cbetadev','clashscore2','omegalyze','ramalyze','rotalyze'})
    bond=raw['bonds_angles']['mp_bonds'];angle=raw['bonds_angles']['mp_angles']
    native_rows={'bonds':bond['outlier_results'],'angles':angle['outlier_results']}
    native_rows.update({k:raw[k]['outlier_results'] for k in ['cablam','cbetadev','clashscore2','omegalyze','ramalyze','rotalyze']})
    counts={k:len(v) for k,v in native_rows.items()}
    csv_counts=dict(collections.Counter(x['validator'] for x in csvs['validation_outliers.csv']))
    check('every_native_outlier_reconciles_to_CSV_count',csv_counts==counts and sum(counts.values())==len(csvs['validation_outliers.csv'])==2551)
    check('all_raw_numeric_values_finite',all(finite_records(x) for x in js.values()))
    partitions={k:{'H_containing':sum('H' in x['atoms_element'] for x in v),'all_heavy':sum('H' not in x['atoms_element'] for x in v),'total':len(v)} for k,v in native_rows.items() if k in ['bonds','angles']}
    check('bond_angle_native_counts_complete_not_missing_key_zeros',native_summary(bond)['num_outliers']==int(row['bond_outliers'])==len(native_rows['bonds']) and native_summary(angle)['num_outliers']==int(row['angle_outliers'])==len(native_rows['angles']) and native_summary(bond)['num_total']==4624 and native_summary(angle)['num_total']==7705)
    metric_links=[('clashscore2','clashscore','clashscore'),('clashscore2','num_clashes','num_clashes'),('ramalyze','num_outliers','ramachandran_outliers'),('ramalyze','outlier_percentage','ramachandran_outlier_percent'),('ramalyze','favored_percentage','ramachandran_favored_percent'),('rotalyze','num_outliers','rotamer_outliers'),('rotalyze','outlier_percentage','rotamer_outlier_percent'),('rotalyze','favored_percentage','rotamer_favored_percent'),('cbetadev','num_outliers','cbeta_outliers'),('cablam','num_cablam_outliers','cablam_outliers'),('cablam','num_cablam_disfavored','cablam_disfavored'),('cablam','cablam_outliers_percentage','cablam_outlier_percent'),('cablam','cablam_disfavored_percentage','cablam_disfavored_percent'),('omegalyze','num_cis_general','cis_nonproline')]
    check('native_scalar_summary_agrees_with_each_validator',all(math.isclose(float(row[output]),native_summary(raw[validator])[native],rel_tol=1e-12,abs_tol=1e-12) for validator,native,output in metric_links) and int(row['twisted_peptides'])==native_summary(raw['omegalyze'])['num_twisted_general']+native_summary(raw['omegalyze'])['num_twisted_proline'])
    pdb_lines=[x for x in source.read_text().splitlines() if x.startswith(('ATOM  ','HETATM'))]
    # PDB/CCTBX fixed-field padding is recognized only in this separate address view.
    source_atoms={(x[21],int(x[22:26]),x[26].strip(),x[12:16].strip()):{'element':x[76:78].strip(),'resname':x[17:20].strip(),'XYZ_A':[float(x[30:38]),float(x[38:46]),float(x[46:54])]} for x in pdb_lines}
    matched=0;missing=[];max_delta=0.0
    for rows in [native_rows['bonds'],native_rows['angles']]:
        for result in rows:
            for i,name in enumerate(result['atoms_name']):
                address=(result['atoms_chain_id'][i].strip(),int(result['atoms_resseq'][i]),result['atoms_icode'][i].strip(),name.strip())
                atom=source_atoms.get(address)
                if atom is None:
                    missing.append(address);continue
                if atom['element']!=result['atoms_element'][i] or atom['resname']!=result['atoms_resname'][i]:
                    missing.append(address);continue
                matched+=1
                max_delta=max(max_delta,max(abs(a-b) for a,b in zip(atom['XYZ_A'],result['atoms_xyz'][i])))
    check('all_returned_bond_angle_addresses_elements_XYZ_match_exact_input',not missing and matched==2*len(native_rows['bonds'])+3*len(native_rows['angles']) and max_delta<1e-10)
    clash_partitions=collections.Counter();clash_unknown=[]
    for result in native_rows['clashscore2']:
        elements=[]
        for prefix in ['', 'target_']:
            address=(result[prefix+'chain_id'].strip(),int(result[prefix+'resseq']),result[prefix+'icode'].strip(),result[prefix+'name'].strip())
            atom=source_atoms.get(address)
            if atom is None:clash_unknown.append(address)
            elements.append(atom['element'] if atom else None)
        category='unmapped_endpoint' if None in elements else 'H_containing_internally_regenerated_H_endpoint' if 'H' in elements else 'all_heavy'
        clash_partitions[category]+=1
    check('clash_partition_uses_both_endpoints_and_retains_unknowns',sum(clash_partitions.values())==int(row['num_clashes']))
    old=load(ARM/'analysis/A055_open_parent_MolProbity/quality_evidence.json')
    metadata_fields=['engine','engine_version','execution_mode','hydrogen_policy','backend_workers']
    matched_protocol={k:{'A055':old['native_manifest'][k],'A058':manifest[k],'equal':old['native_manifest'][k]==manifest[k]} for k in metadata_fields}
    check('reported_A055_A058_protocol_and_thresholds_match',all(x['equal'] for x in matched_protocol.values()) and old['quality_thresholds_used']==thresholds and manifest['execution_mode']=='measurement_only')
    metrics=[x for x in row if x not in ['candidate_id','source_name','status','failed_thresholds','error']]
    comparison=[{'metric':metric,'A055':float(old['native_summary_row'][metric]),'A058':float(row[metric]),'delta_A058_minus_A055':float(row[metric])-float(old['native_summary_row'][metric]),'scope':'same-parent preparation-method comparison; not isolated mutation effect'} for metric in metrics]
    check('all_summary_measurements_finite_and_compared',len(comparison)==20 and all(math.isfinite(x[k]) for x in comparison for k in ['A055','A058','delta_A058_minus_A055']))
    omega=raw['omegalyze']['outlier_results'];cablam=raw['cablam']['outlier_results']
    adverse={'clashes':raw['clashscore2']['outlier_results'],'Cbeta':raw['cbetadev']['outlier_results'],'Ramachandran':raw['ramalyze']['outlier_results'],'omega':omega,'rotamers':raw['rotalyze']['outlier_results'],'cablam':cablam,'all_heavy_angle_outliers':native_rows['angles']}
    # Raw native H-containing bond rows remain wholly in their original JSON/CSV.
    check('all_adverse_record_categories_retained',len(adverse['Cbeta'])==int(row['cbeta_outliers']) and len(adverse['Ramachandran'])==int(row['ramachandran_outliers']) and len(adverse['rotamers'])==int(row['rotamer_outliers']) and len(adverse['omega'])==5 and len(adverse['cablam'])==24)
    OUT.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    inventory=[{'path':str((EXT/name).relative_to(ARM)),'member':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()} for name,b in members.items()]
    evidence={'native_summary_row':row,'native_manifest':manifest,'quality_thresholds_used':thresholds,'raw_outlier_row_counts':counts,'native_CSV_rows':len(csvs['validation_outliers.csv']),'bond_angle_H_heavy_partitions':partitions,'native_clash_partitions_using_both_endpoints':dict(clash_partitions),'unmapped_clash_endpoints':clash_unknown,'bond_angle_outlier_atom_addresses_matched':matched,'max_returned_input_atom_component_delta_A':max_delta,'missing_bond_angle_addresses':missing,'cablam_label_counts':dict(collections.Counter(x['outlier_type'] for x in cablam)),'cablam_summary_not_disjoint_row_sum':native_summary(raw['cablam']),'omega_summary':native_summary(raw['omegalyze']),'native_residual_records':adverse,'A055_A058_protocol_metadata':matched_protocol,'A055_A058_comparison':comparison,'classification':'native measured; not passed/eligible','H_policy':'Native clashscore regenerates/optimizes H; bond/angle supplied-H distance convention findings are retained, not source H-state validation.'}
    save('artifact_inventory.json',{'archive':{'path':str((RAW/'results.zip').relative_to(ARM)),'sha256':sha(RAW/'results.zip'),'bytes':(RAW/'results.zip').stat().st_size},'members':inventory})
    save('quality_evidence.json',evidence)
    with (OUT/'A055_A058_comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(comparison[0]));writer.writeheader();writer.writerows(comparison)
    template=list(csv.DictReader((ARM/'analysis/A055_open_parent_MolProbity/observations.csv').open()))
    obs=[]
    for oldrow in template:
        metric=oldrow['metric'].split('.',1)[1]
        item=dict(oldrow);item['metric']='A058_minimized_parent_preparation.'+metric;item['value']=row[metric];item['protocol_id']='Mol_Probity.measurement_only.cctbx2025.11.A057_minimized_parent_preparation';item['evidence_path']=str((EXT/'candidate_summary.csv').relative_to(ARM));obs.append(item)
    with (OUT/'observations.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(template[0]));writer.writeheader();writer.writerows(obs)
    qa={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scientific_attempt_number':58,'doc_id':'JOB_0003','native_status':row['status'],'checks':checks,'check_count':len(checks),'all_passed':all(checks.values()),'archive_members_reviewed':len(members),'JSON_artifacts':len(js),'CSV_artifacts':len(csvs),'summary_rows':len(summary),'invalid_rows':len(csvs['invalid_candidates.csv']),'native_outlier_rows':len(csvs['validation_outliers.csv']),'native_observation_companion_rows':len(obs),'source_sha256':sha(source),'input_atom_count':len(pdb_lines),'protein_residues':269,'water_residues':238,'bond_angle_H_heavy_partitions':partitions,'quality_thresholds_used':thresholds,'CCTBX_version':manifest['engine_version'],'worker_H_policy':manifest['hydrogen_policy'],'scientific_quality_function_stability_or_eligibility_pass':False,'no_pNPL_or_reactive_water_assigned':True,'new_local_molecular_validation_calls':0,'approved_scientific_followups':[]}
    save('QA.json',qa)
    print(json.dumps({'checks':len(checks),'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v],'outlier_rows':len(csvs['validation_outliers.csv']),'observation_rows':len(obs),'QA':str(OUT/'QA.json')}))
    return 0 if all(checks.values()) else 1


if __name__=='__main__':
    sys.exit(main())
