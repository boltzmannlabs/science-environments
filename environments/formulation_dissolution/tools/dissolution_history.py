"""Conservative history inventory and source-linked public profile import.

Public numerical transcriptions are from the supplied investigation specification;
they are literature-reported summaries, never recalled-lot observations.
"""
import csv
import hashlib
import json
from pathlib import Path

FIELDS = ('path_source_id','checksum','source_locator','api','product','batch_id','method_id','record_count','evidence_type','data_origin','permission_status','eligibility','exclusion_reason')
PATENT_PH = 'https://www.quickcompany.in/patents/sustained-release-compositions-of-ranolazine'
PATENT_HCL = 'https://patents.google.com/patent/US6525057#p=15'
ZENODO = 'https://doi.org/10.5281/zenodo.1170150'
FDA_URL = 'https://api.fda.gov/drug/enforcement.json?search=recall_number:%22D-0010-2027%22&limit=1'
# One Ranexa reference, not the repeated reference printed against each example.
PH68 = {
 'Ranexa_1g': [0,18,26,29,34,57,73,75],
 'Example_3': [0,20,27,33,38,53,70,82],
 'Example_4': [0,9,28,40,43,46,61,77],
 'Example_5': [0,14,15,23,26,34,54,65],
 'Example_6': [0,12,18,27,31,44,62,74],
 'Example_7': [0,10,20,26,29,44,64,76],
 'Example_8': [0,20,28,28,29,33,36,40],
}
HCL = {'IR':[88.1,100.5,101.7,None,None,None,None,None],
       'SR_A':[None,13.9,19.9,27.8,39.0,52.4,61.6,80.8],
       'SR_B':[None,17.6,26.0,47.5,69.2,90.1,99.6,105.6],
       'SR_C':[None,17.5,25.7,35.9,48.4,64.7,74.2,95.4]}
METHODS = {
 'patent_201741007784_ph68': {'method_id':'patent_201741007784_ph68','version':None,'apparatus':'USP II','speed_rpm':100,'medium':'pH 6.8 phosphate buffer','volume_mL':900,'temperature_C':37,'source_locator':PATENT_PH},
 'patent_US6525057_hcl': {'method_id':'patent_US6525057_hcl','version':None,'apparatus':'USP II','speed_rpm':None,'medium':'0.1 M hydrochloric acid','volume_mL':900,'temperature_C':None,'source_locator':PATENT_HCL},
}
LEGACY = [
 'dissolution_data_curation/data/processed/'+n for n in ('profiles.csv','formulations.csv','compounds.csv','media.csv','methods.csv','fda_methods.csv')
] + ['dissolution_data_curation/output/'+n for n in ('50api_profiles.csv','50api_formulations.csv','model_comparison.csv','PROJECT_REPORT.md')]+[
 'dissolution_prediction/output/results/benchmark_results.csv','dissolution_prediction/RESULTS.md',
 'formulation_plan/data/dissolution_data.csv','formulation_plan/data/generate_synthetic_data.py',
 'dissolution_data_curation/data/raw/Dissolution_Test_Behavior_Modeling_ML_Project/Dissolution Methods.csv']
PRIOR = ['configs/exploratory_ranolazine_500.json','data/processed/ranolazine_research_scenario_results.json']


def sha(path):
    """Hash a local input without modifying it."""
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def profile_rows():
    """Seed literature-reported profiles with explicit methods and missing cells."""
    rows=[]
    for name, values in PH68.items():
        for t,v in zip((0,30,60,90,120,240,480,720),values):
            rows.append(dict(profile_id='201741007784_'+name,formulation_id=name,batch_id=None,
                product='Ranexa 1 g reference' if name=='Ranexa_1g' else 'research example '+name,
                api='ranolazine',dosage_form='extended_release_tablet',strength_value=1000 if name=='Ranexa_1g' else None,
                strength_unit='mg' if name=='Ranexa_1g' else None,method_id='patent_201741007784_ph68',
                time_value=t,time_unit='min',release_value=v,release_unit='percent',sample_id=None,replicate_id=None,
                observation_level='summary',replicate_count=None,dispersion_type=None,dispersion_value=None,
                evidence_label='literature_reported',data_origin='experimental',source_id='201741007784',
                source_locator=PATENT_PH+' (Examples 3–8 dissolution tables)',raw_units_available=False))
    for name,values in HCL.items():
        for t,v in zip((0.25,0.5,1,2,4,8,12,24),values):
            rows.append(dict(profile_id='US6525057_'+name,formulation_id=name,batch_id=None,
                product='research formulation '+name,api='ranolazine',dosage_form='immediate_release_tablet' if name=='IR' else 'sustained_release_tablet',
                strength_value=None,strength_unit=None,method_id='patent_US6525057_hcl',
                time_value=t,time_unit='h',release_value=v,release_unit='percent',sample_id=None,replicate_id=None,
                observation_level='summary',replicate_count=None,dispersion_type=None,dispersion_value=None,
                evidence_label='literature_reported',data_origin='experimental',source_id='US6525057B2',
                source_locator=PATENT_HCL+' (Table 4)',raw_units_available=False))
    rows.append(dict(profile_id='zenodo_F8_endpoint',formulation_id='F8',batch_id=None,
        product='500 mg research tablet',api='ranolazine',dosage_form='extended_release_tablet',strength_value=500,
        strength_unit='mg',method_id=None,time_value=24,time_unit='h',release_value=99.5,release_unit='percent',
        sample_id=None,replicate_id=None,observation_level='author_reported_abstract_endpoint',replicate_count=None,
        dispersion_type=None,dispersion_value=None,evidence_label='literature_reported',data_origin='experimental',
        source_id='zenodo_1170150',source_locator=ZENODO+' (abstract)',raw_units_available=False))
    return rows


def validate_profile(row, methods=METHODS):
    """Reject absent units/identity; keep values greater than 100 and nulls unchanged."""
    missing=[key for key in ('profile_id','api','dosage_form','time_unit','release_unit','source_locator','evidence_label','data_origin') if not row.get(key)]
    if row.get('time_unit') not in ('min','h'): missing.append('supported_time_unit')
    if row.get('release_unit') != 'percent': missing.append('supported_release_unit')
    if row.get('method_id') and row['method_id'] not in methods: missing.append('known_method')
    if row.get('release_value') is not None and not isinstance(row['release_value'],(int,float)): missing.append('numeric_release')
    return {'valid':not missing,'missing':missing,'comparability_group':(row.get('dosage_form'),row.get('strength_value'),row.get('method_id'),row.get('batch_id'))}


def normalize(row):
    """Create a separate derived minute time, never overwrite the original."""
    validate=validate_profile(row)
    if not validate['valid']: raise ValueError(validate['missing'])
    return {**row,'derived_time_min':row['time_value']*(60 if row['time_unit']=='h' else 1),'transformation':'h_to_min' if row['time_unit']=='h' else 'identity'}


def _csv_count(path):
    with path.open(newline='',encoding='utf-8-sig',errors='replace') as stream:
        return sum(1 for _ in csv.reader(stream))-1


def archive_profile_origins(path):
    """Count row-level provenance without loading/rewriting mixed historical CSVs."""
    from collections import Counter
    counts=Counter()
    with path.open(newline='',encoding='utf-8-sig',errors='replace') as stream:
        for row in csv.DictReader(stream):
            counts[(row.get('source_type') or 'unknown').lower()]+=1
    return dict(counts)


def inventory(legacy_root=None, prior_gym_root=None, additional_sources=(), transcription_source=None):
    """Inventory configured archives without claiming unverified rows are measurements."""
    items=[(legacy_root,p) for p in LEGACY]+[(prior_gym_root,p) for p in PRIOR]
    items += [(None,p) for p in additional_sources]
    if transcription_source:
        items.append((None,transcription_source))
    manifest=[]
    for root,rel in items:
        path=Path(root,rel) if root else Path(rel)
        exists=path.is_file()
        name=path.name.lower()
        kind=('mixed_row_level' if name=='profiles.csv' and 'dissolution_data_curation' in str(path) else
              'predicted' if 'scenario_results' in name else 'synthetic' if 'synthetic' in name or '50api_' in name or 'formulation_plan/data/dissolution_data' in str(path) else
              'method_only' if 'method' in name else 'reported_benchmark' if 'benchmark' in name or 'comparison' in name or 'results.md' in name else 'unknown')
        count=_csv_count(path) if exists and path.suffix.lower()=='.csv' else None
        manifest.append(dict(zip(FIELDS,(str(path),sha(path) if exists else None,str(path) if exists else None,
            None,None,None,None,count,kind,'synthetic' if kind=='synthetic' else None,
            'local_read_only' if exists else 'unresolved', 'excluded_pending_row_provenance' if exists else 'not_found',
            'not a verified affected-lot measured profile' if exists else 'file missing'))))
    return manifest


def write_history(out, legacy_root=None, prior_gym_root=None, additional_sources=(), transcription_source=None):
    """Create reproducible processed artifacts; raw archive inputs remain untouched."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest=inventory(legacy_root,prior_gym_root,additional_sources,transcription_source)
    seen={}
    duplicates=[]
    for item in manifest:
        checksum=item['checksum']
        if checksum and checksum in seen:
            item['eligibility']='duplicate_source'
            item['exclusion_reason']='same content as '+seen[checksum]
            duplicates.append({'copy':item['path_source_id'],'canonical':seen[checksum],'reason':'sha256 match'})
        elif checksum:
            seen[checksum]=item['path_source_id']
    rows=profile_rows()
    transcription_hash=sha(transcription_source) if transcription_source and Path(transcription_source).is_file() else None
    for source,url,group in [('201741007784',PATENT_PH,'ph68'),('US6525057B2',PATENT_HCL,'hcl'),('zenodo_1170150',ZENODO,'endpoint')]:
        selected=[r for r in rows if r['source_id']==source]
        manifest.append(dict(zip(FIELDS,(source,transcription_hash,url+' | transcription: '+str(transcription_source) if transcription_source else url,'ranolazine','research/reference, not Ajanta',None,
            selected[0]['method_id'],len(selected),'literature_reported','experimental','user_supplied_transcription',
            'reference_only_not_recalled_lot','unit data unavailable; not current-product QC'))))
    with (out/'history_manifest.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,FIELDS);writer.writeheader();writer.writerows(manifest)
    (out/'duplicates.json').write_text(json.dumps(duplicates,indent=2))
    (out/'literature_profiles.json').write_text(json.dumps([normalize(r) for r in rows],indent=2))
    (out/'literature_methods.json').write_text(json.dumps(METHODS,indent=2))
    mixed=Path(legacy_root)/'dissolution_data_curation/data/processed/profiles.csv' if legacy_root else None
    if mixed and mixed.is_file():
        (out/'archive_row_origins.json').write_text(json.dumps(archive_profile_origins(mixed),indent=2))
    prior=Path(prior_gym_root or '')/'data/processed/ranolazine_research_scenario_results.json' if prior_gym_root else None
    if prior and prior.is_file():
        (out/'prior_scenario_reference.json').write_text(json.dumps({'source_path':str(prior),'sha256':sha(prior),
            'status':'exploratory_assumption_conditional_NOT_product_prediction','evidence_label':'predicted','data_origin':'synthetic',
            'artifact':json.loads(prior.read_text())},indent=2))
    counts={'usable_affected_lot_profiles':0,'public_ranolazine_research_or_reference_profiles':len(set(r['profile_id'] for r in rows)),
            'other_experimental_profiles_verified':0,'mixed_archive_row_origins':archive_profile_origins(mixed) if mixed and mixed.is_file() else {},
            'synthetic_sources':sum(m['evidence_type']=='synthetic' and m['checksum'] is not None for m in manifest),
            'prediction_sources':sum(m['evidence_type']=='predicted' and m['checksum'] is not None for m in manifest),
            'method_only_sources':sum(m['evidence_type']=='method_only' and m['checksum'] is not None for m in manifest)}
    (out/'history_counts.json').write_text(json.dumps(counts,indent=2))
    return {'status':'success','manifest':str(out/'history_manifest.csv'),'profiles':str(out/'literature_profiles.json'),
            'counts':counts,'unresolved':[m['path_source_id'] for m in manifest if m['permission_status']=='unresolved']}
