"""Synthetic input selection and private-outcome separation for the Doyle pilot."""
import csv
from copy import deepcopy
import hashlib
import json

import pytest

from synthesis_route_gym.condition_development import (
    SOURCE_COLUMNS, SOURCE_URL, load_doyle_inputs, select_studies,
    materialize_outcomes, normalize_predictions,
)
from synthesis_route_gym.condition_domain import FIXED_PARTNER, FIXED_PRECATALYST


def row(aryl='Brc1ccccc1', product='Cc1ccc(Nc2ccccc2)cc1', ligand='P', outcome='41.5'):
    inputs=[aryl,FIXED_PARTNER,FIXED_PRECATALYST,ligand,'CC','O']
    return {'ligand':ligand,'additive':'CC','base':'O','aryl halide':aryl,
            'rxn':'.'.join(inputs)+'>>'+product,'yield':outcome}


def write_source(tmp_path, rows, name='source.csv'):
    path=tmp_path/name
    with path.open('w',newline='')as handle:
        writer=csv.DictWriter(handle,fieldnames=SOURCE_COLUMNS)
        writer.writeheader();writer.writerows(rows)
    return path,hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows():
    return [row(aryl,product,ligand) for aryl,product in (
        ('Brc1ccccc1','Cc1ccc(Nc2ccccc2)cc1'),
        ('Clc1ccccc1','Cc1ccc(Nc2ccccc2)cc1'),
        ('Brc1ccncc1','Cc1ccc(Nc2ccncc2)cc1'))
        for ligand in ('P','CP','CCP','CCCP')]


def studies(tmp_path):
    path,sha=write_source(tmp_path,source_rows())
    records,audit=load_doyle_inputs(path,sha)
    return path,sha,select_studies(records,dataset_sha256=sha,study_count=3,
        candidates_per_study=3,initial_count=1,observation_budget=2),audit


def test_input_loader_does_not_parse_or_expose_outcomes(tmp_path):
    path,sha=write_source(tmp_path,[row(outcome='secret-not-a-number')])
    records,audit=load_doyle_inputs(path,sha)
    assert len(records)==1 and audit['record_count']==1
    assert 'yield' not in json.dumps(records) and 'secret' not in json.dumps(records)
    candidate=records[0]
    assert candidate['recipe']['reactants']==[candidate['substrate'],FIXED_PARTNER]
    assert candidate['recipe']['reagents'][-1]==FIXED_PRECATALYST
    assert candidate['recipe']['product']==candidate['target']
    assert audit['outcomes_inspected'] is False


def test_candidate_identity_and_selection_are_outcome_independent(tmp_path):
    p,a=write_source(tmp_path,source_rows())
    q,b=write_source(tmp_path,[{**r,'yield':'99.99'}for r in source_rows()],'other.csv')
    first,_=load_doyle_inputs(p,a);second,_=load_doyle_inputs(q,b)
    assert first==second
    one=select_studies(first,dataset_sha256=a,study_count=3,candidates_per_study=3,initial_count=1,observation_budget=2)
    two=select_studies(second,dataset_sha256=a,study_count=3,candidates_per_study=3,initial_count=1,observation_budget=2)
    assert one==two


def test_selection_covers_products_and_retains_only_allowed_public_inputs(tmp_path):
    _,sha,selected,audit=studies(tmp_path)
    assert audit['substrate_count']==3 and audit['product_count']==2
    assert len(selected)==3 and len({s['product_group_id']for s in selected})==2
    for study in selected:
        assert study['schema_version']=='srg-condition-study-v1'
        assert study['data_role']=='development' and study['source_url']==SOURCE_URL
        assert study['dataset_sha256']==sha and study['observation_budget']==2
        ids=[r['candidate_id']for r in study['candidates']]
        assert ids==sorted(ids) and study['initial_ids']==ids[:1]
        assert 'outcomes_sha256' not in study
        assert 'source_index' not in json.dumps(study)
        assert 'yield_percent' not in json.dumps(study['candidates'])
        assert all(set(c)=={'candidate_id','conditions','recipe'}for c in study['candidates'])


def test_selection_invariant_to_row_order_and_does_not_mutate_inputs(tmp_path):
    path,sha=write_source(tmp_path,source_rows())
    records,_=load_doyle_inputs(path,sha);before=deepcopy(records)
    kwargs=dict(dataset_sha256=sha,study_count=3,candidates_per_study=3,initial_count=1,observation_budget=2)
    assert select_studies(records,**kwargs)==select_studies(tuple(reversed(records)),**kwargs)
    assert records==before


@pytest.mark.parametrize('sha',['','bad','A'*64,'0'*64,None])
def test_source_hash_is_required_and_verified(tmp_path,sha):
    path,_=write_source(tmp_path,[row()])
    with pytest.raises(ValueError,match='digest'):
        load_doyle_inputs(path,sha)


@pytest.mark.parametrize('updates',[
    {'ligand':''},{'base':'invalid-smiles'}, {'rxn':'C'}, {'rxn':'C>>C.O'},
    {'rxn':'C>>invalid-smiles'},{'rxn':'C>>C'}, {'rxn':'bad>>C'},
])
def test_invalid_source_inputs_are_rejected(tmp_path,updates):
    path,sha=write_source(tmp_path,[{**row(),**updates}])
    with pytest.raises(ValueError):load_doyle_inputs(path,sha)


def test_invalid_columns_empty_and_duplicate_chemistry_are_rejected(tmp_path):
    path,sha=write_source(tmp_path,[])
    with pytest.raises(ValueError,match='empty'):load_doyle_inputs(path,sha)
    path,sha=write_source(tmp_path,[row(),row(outcome='99')])
    with pytest.raises(ValueError,match='Duplicate'):load_doyle_inputs(path,sha)
    path.write_text('ligand,yield\nP,10\n')
    with pytest.raises(ValueError,match='columns'):
        load_doyle_inputs(path,hashlib.sha256(path.read_bytes()).hexdigest())


def test_malformed_row_rejected(tmp_path):
    path,_=write_source(tmp_path,[row()])
    with path.open('a')as f:f.write('too,few\n')
    with pytest.raises(ValueError,match='columns'):
        load_doyle_inputs(path,hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.mark.parametrize('updates',[
    {'study_count':0},{'study_count':True},{'study_count':1},{'study_count':4},
    {'candidates_per_study':5},{'candidates_per_study':0},
    {'initial_count':0},{'initial_count':3},{'observation_budget':4},
    {'observation_budget':0},
])
def test_invalid_or_impossible_selection_rejected(tmp_path,updates):
    p,sha=write_source(tmp_path,source_rows());records,_=load_doyle_inputs(p,sha)
    args=dict(dataset_sha256=sha,study_count=3,candidates_per_study=3,initial_count=1,observation_budget=2)
    with pytest.raises(ValueError):select_studies(records,**{**args,**updates})


def test_private_materialization_returns_only_selected_observed_endpoint(tmp_path):
    path,sha,selected,_=studies(tmp_path)
    labels=materialize_outcomes(path,sha,selected)
    assert set(labels)=={s['study_id']for s in selected}
    for study in selected:
        private=labels[study['study_id']]
        assert set(private)=={'schema_version','study_id','dataset_sha256','candidate_inputs_sha256','outcomes'}
        assert private['candidate_inputs_sha256']==expected_input_digest(study)
        assert set(private['outcomes'])=={c['candidate_id']for c in study['candidates']}
        assert set(private['outcomes'].values())=={41.5}


@pytest.mark.parametrize('bad',['nan','inf','-1','101','secret-value',''])
def test_bad_selected_outcomes_fail_without_leaking_values(tmp_path,bad):
    path,sha=write_source(tmp_path,[row(outcome=bad)])
    records,_=load_doyle_inputs(path,sha)
    selected=select_studies(records,dataset_sha256=sha,study_count=1,candidates_per_study=1,initial_count=1,observation_budget=1)
    with pytest.raises(ValueError,match='outcome')as error:
        materialize_outcomes(path,sha,selected)
    assert 'secret-value' not in str(error.value)


def test_unknown_candidate_or_changed_source_refuses_materialization(tmp_path):
    path,sha,selected,_=studies(tmp_path)
    changed=deepcopy(selected);changed[0]['candidates'][0]['candidate_id']='unknown'
    with pytest.raises(ValueError,match='candidate'):materialize_outcomes(path,sha,changed)
    with pytest.raises(ValueError,match='digest'):materialize_outcomes(path,'0'*64,selected)


def metadata():
    return {'model_version':'fixture-model-v1','model_revision':'a'*40,
            'source_url':'https://example.org/model','license':'MIT','manifest_sha256':'b'*64}


def publisher(study):
    return [{'id':c['candidate_id'],'status':'scored','predicted_yield_percent':12.0,
             'raw_yield_percent':12.0,'reason':None,'model_version':'fixture-model-v1',
             'domain':'transfer_unverified','uncertainty_kind':'not_calibrated',
             'evidence_status':'predicted','endpoint_scope':'model_yield_not_experimental_feasibility'}
            for c in study['candidates']]


def test_prediction_normalization_preserves_abstentions_and_explicit_provenance(tmp_path):
    _,_,selected,_=studies(tmp_path);study=selected[0];rows=publisher(study)
    rows[1]={**rows[1],'status':'abstained','predicted_yield_percent':None,'raw_yield_percent':None,'reason':'unknown_token'}
    output=normalize_predictions(study,rows,metadata())
    assert set(output)=={'schema_version','study_id','candidate_inputs_sha256','model_metadata','predictions'}
    assert output['schema_version']=='srg-condition-predictions-v1'
    assert output['predictions'][0]['unit']=='percent' and output['predictions'][0]['value']==12
    assert output['predictions'][1]['value'] is None
    assert output['predictions'][1]['uncertainty']=='not_calibrated; abstention_reason=unknown_token'
    assert all(p['prediction_id']for p in output['predictions'])
    assert 'raw_yield_percent' not in json.dumps(output)


@pytest.mark.parametrize('changes',[
    {'id':'wrong'},{'status':'measured'},{'predicted_yield_percent':float('nan')},
    {'predicted_yield_percent':101},{'model_version':'other'},
    {'evidence_status':'experimental'},{'reason':'unknown_token'},
    {'status':'abstained','predicted_yield_percent':None,'reason':'invented_reason'},
])
def test_malformed_prediction_rejected(tmp_path,changes):
    _,_,selected,_=studies(tmp_path);study=selected[0];rows=publisher(study)
    rows[0]={**rows[0],**changes}
    with pytest.raises(ValueError):normalize_predictions(study,rows,metadata())


def test_prediction_identity_completeness_and_metadata_boundaries(tmp_path):
    _,_,selected,_=studies(tmp_path);study=selected[0];rows=publisher(study)
    for values in (rows[:-1],rows+[rows[0]],list(reversed(rows))):
        with pytest.raises(ValueError):normalize_predictions(study,values,metadata())
    with pytest.raises(ValueError):normalize_predictions(study,rows,{**metadata(),'private_path':'/private/outcomes'})


@pytest.mark.parametrize('change',[
    {'source_url':'https://user:secret@example.org/model'}, {'source_url':'file:///private/model'},
    {'model_version':None}, {'manifest_sha256':'bad'}, {'model_revision':'main'},
    {'asset_sha256':{'../private':'a'*64}}, {'asset_sha256':{'config.json':'/private/path'}},
    {'runtime_sha256':{'unknown':'b'*64}}, {'shared_cache':'yes'},
    {'inference_seconds':float('nan')}, {'inference_seconds':-1},
])
def test_model_metadata_is_public_bounded_and_pinned(tmp_path,change):
    _,_,selected,_=studies(tmp_path);study=selected[0]
    with pytest.raises(ValueError):normalize_predictions(study,publisher(study),{**metadata(),**change})


@pytest.mark.parametrize('change',[
    {'raw_yield_percent':None}, {'raw_yield_percent':float('inf')}, {'raw_yield_percent':99},
    {'status':'abstained','predicted_yield_percent':None,'raw_yield_percent':12,'reason':'unknown_token'},
    {'status':'abstained','predicted_yield_percent':None,'raw_yield_percent':50,'reason':'prediction_out_of_range'},
    {'domain':''}, {'uncertainty_kind':None},
])
def test_publisher_numeric_and_uncertainty_consistency(tmp_path,change):
    _,_,selected,_=studies(tmp_path);study=selected[0];rows=publisher(study)
    rows[0]={**rows[0],**change}
    with pytest.raises(ValueError):normalize_predictions(study,rows,metadata())


def test_out_of_range_raw_prediction_remains_abstained(tmp_path):
    _,_,selected,_=studies(tmp_path);study=selected[0];rows=publisher(study)
    rows[0]={**rows[0],'status':'abstained','predicted_yield_percent':None,'raw_yield_percent':-3,'reason':'prediction_out_of_range'}
    result=normalize_predictions(study,rows,metadata())
    assert result['predictions'][0]['value'] is None
    assert 'prediction_out_of_range' in result['predictions'][0]['uncertainty']


def test_source_size_utf8_and_multiple_product_boundaries(tmp_path,monkeypatch):
    from synthesis_route_gym import condition_development as module
    path,sha=write_source(tmp_path,[row()])
    monkeypatch.setattr(module,'MAX_SOURCE_BYTES',1)
    with pytest.raises(ValueError,match='size'):load_doyle_inputs(path,sha)
    monkeypatch.setattr(module,'MAX_SOURCE_BYTES',100000)
    path.write_bytes(b'\xff')
    with pytest.raises(ValueError,match='UTF-8'):
        load_doyle_inputs(path,hashlib.sha256(path.read_bytes()).hexdigest())
    path,sha=write_source(tmp_path,[row(),row(product='Cc1ccc(Nc2ccncc2)cc1')])
    with pytest.raises(ValueError,match='multiple'):load_doyle_inputs(path,sha)


def test_valid_public_model_metadata_is_copied(tmp_path):
    _,_,selected,_=studies(tmp_path);study=selected[0]
    meta={**metadata(),'asset_sha256':{'config.json':'c'*64},
          'runtime_sha256':{'worker_sha256':'d'*64},'shared_cache':True,'inference_seconds':1.0}
    result=normalize_predictions(study,publisher(study),meta)
    result['model_metadata']['asset_sha256']['config.json']='changed'
    assert meta['asset_sha256']['config.json']=='c'*64


def expected_input_digest(study):
    inputs={key:study[key]for key in ('study_id','substrate','target','dataset_sha256')}
    inputs['candidates']=sorted(study['candidates'],key=lambda row:row['candidate_id'])
    return hashlib.sha256(json.dumps(inputs,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def test_predictions_bind_complete_candidate_chemistry_not_only_ids(tmp_path):
    _,_,selected,_=studies(tmp_path);study=selected[0];before=deepcopy(study)
    baseline=normalize_predictions(study,publisher(study),metadata())
    assert baseline['candidate_inputs_sha256']==expected_input_digest(study)
    for field,value in [('substrate','CO'),('target','CC=O'),('dataset_sha256','c'*64)]:
        changed={**study,field:value}
        assert normalize_predictions(changed,publisher(changed),metadata())['candidate_inputs_sha256']!=baseline['candidate_inputs_sha256']
    for update in ('conditions','recipe'):
        changed=deepcopy(study)
        if update=='conditions':changed['candidates'][0]['conditions']['base']='N'
        else:changed['candidates'][0]['recipe']['reagents']=['N']
        result=normalize_predictions(changed,publisher(changed),metadata())
        assert result['candidate_inputs_sha256']!=baseline['candidate_inputs_sha256']
    assert study==before


def test_input_binding_is_order_independent_and_excludes_private_outcome_commitment(tmp_path):
    _,_,selected,_=studies(tmp_path);study=selected[0]
    first=normalize_predictions(study,publisher(study),metadata())
    reordered={**study,'candidates':list(reversed(study['candidates'])),'outcomes_sha256':'d'*64}
    second=normalize_predictions(reordered,publisher(reordered),metadata())
    assert first['candidate_inputs_sha256']==second['candidate_inputs_sha256']


@pytest.mark.parametrize('field',['recipe','conditions','substrate','target','dataset_sha256'])
def test_materialization_rejects_changed_selected_chemistry_before_assigning_outcomes(tmp_path,field):
    path,sha,selected,_=studies(tmp_path);changed=deepcopy(selected)
    if field=='recipe':changed[0]['candidates'][0]['recipe']['reagents']=['N']
    elif field=='conditions':changed[0]['candidates'][0]['conditions']['base']='N'
    elif field=='dataset_sha256':changed[0][field]='d'*64
    else:changed[0][field]='CO'
    with pytest.raises(ValueError,match='input|digest'):
        materialize_outcomes(path,sha,changed)


def test_duplicate_selected_studies_or_candidates_fail_closed(tmp_path):
    path,sha,selected,_=studies(tmp_path)
    with pytest.raises(ValueError,match='Duplicate'):
        materialize_outcomes(path,sha,selected+(selected[0],))
    changed=deepcopy(selected)
    changed[0]['candidates'].append(deepcopy(changed[0]['candidates'][0]))
    with pytest.raises(ValueError,match='Duplicate'):
        materialize_outcomes(path,sha,changed)
