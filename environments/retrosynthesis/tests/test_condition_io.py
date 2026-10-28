"""Host-only study joins keep measurement identities and endpoints explicit."""
import hashlib
import json
import pytest
from synthesis_route_gym.condition_io import load_condition_inputs
from synthesis_route_gym.condition_identity import condition_input_digest


def files(tmp_path):
    labels={'schema_version':'srg-condition-outcomes-v1','study_id':'study',
            'dataset_sha256':'a'*64,'outcomes':{'a':12.0,'b':84.0}}
    raw=json.dumps(labels).encode(); (tmp_path/'labels.json').write_bytes(raw)
    study={'schema_version':'srg-condition-study-v1','data_role':'development',
           'study_id':'study','substrate':'CCBr','target':'CCO',
           'source_url':'https://example.org/data','source_locator':'development study',
           'dataset_sha256':'a'*64,'observation_budget':2,'initial_ids':['a'],
           'outcomes_sha256':hashlib.sha256(raw).hexdigest(),
           'candidates':[{'candidate_id':key,'conditions':{'base':base},
                          'recipe':{'id':key,'reactants':['CCBr'],'reagents':[base],
                                    'product':'CCO'}} for key,base in [('a','O'),('b','N')]]}
    labels={**labels,'candidate_inputs_sha256':condition_input_digest(study)}
    raw=json.dumps(labels).encode();(tmp_path/'labels.json').write_bytes(raw)
    study={**study,'outcomes_sha256':hashlib.sha256(raw).hexdigest()}
    rewrite(tmp_path,'study.json',study)
    predictions={'schema_version':'srg-condition-predictions-v1','study_id':'study',
                 'candidate_inputs_sha256':condition_input_digest(study),
                 'model_metadata':{'version':'test-model'},'predictions':[
                     {'candidate_id':key,'prediction_id':'pred-'+key,'status':'scored',
                      'value':40.0,'unit':'percent','domain':'transfer_unknown',
                      'uncertainty':'not_calibrated','model_version':'test-model'}for key in ('a','b')]}
    rewrite(tmp_path,'predictions.json',predictions)
    return study,labels,predictions


def load(tmp_path,prediction=True):
    return load_condition_inputs(tmp_path/'study.json',tmp_path/'labels.json',
                                 tmp_path/'predictions.json' if prediction else None)


def rewrite(tmp_path,name,value):
    (tmp_path/name).write_text(json.dumps(value))


def test_valid_host_study_hides_unqueried_yield(tmp_path):
    files(tmp_path); inputs=load(tmp_path)
    assert inputs['study'].observed_ids==('a',) and inputs['study'].budget==2
    assert inputs['study'].view()['observations'][0]['yield_percent']==12
    assert '84' not in json.dumps(inputs['study'].view())
    assert len(inputs['predictions'])==2
    assert inputs['study_id']=='study' and inputs['target']=='CCO'
    assert 'labels.json' not in json.dumps(inputs['public_metadata'])


def test_predictions_optional(tmp_path):
    files(tmp_path); assert load(tmp_path,False)['predictions']==()


@pytest.mark.parametrize('patch',[
    {'data_role':'final'},{'measurement':'CAD response'},{'observation_budget':True},
    {'observation_budget':0},{'initial_ids':['a','a']},{'initial_ids':['unknown']},
    {'observation_budget':1,'initial_ids':['a','b']},{'source_url':'file:///private'},
    {'source_url':'https://user:password@example.org/data'},{'unknown':'field'},
])
def test_invalid_public_study_before_private_access(tmp_path,patch):
    study,_,_=files(tmp_path);rewrite(tmp_path,'study.json',{**study,**patch})
    (tmp_path/'labels.json').unlink()
    with pytest.raises(ValueError,match='public condition study'):load(tmp_path)


@pytest.mark.parametrize('mutation',['duplicate','wrong_product','wrong_id','outcome_factor','mixed_factors'])
def test_candidate_schema(tmp_path,mutation):
    study,_,_=files(tmp_path)
    if mutation=='duplicate':study['candidates'][1]=study['candidates'][0]
    if mutation=='wrong_product':study['candidates'][0]['recipe']['product']='CCN'
    if mutation=='wrong_id':study['candidates'][0]['recipe']['id']='wrong'
    if mutation=='outcome_factor':study['candidates'][0]['conditions']={'yield':'84'}
    if mutation=='mixed_factors':study['candidates'][0]['conditions']={'ligand':'O'}
    rewrite(tmp_path,'study.json',study)
    with pytest.raises(ValueError,match='public condition study'):load(tmp_path)


def test_hash_mismatch(tmp_path):
    files(tmp_path)
    with (tmp_path/'labels.json').open('a')as f:f.write(' ')
    with pytest.raises(ValueError,match='outcome commitment'):load(tmp_path)


@pytest.mark.parametrize('patch',[
    {'study_id':'other'},{'dataset_sha256':'b'*64},{'outcomes':{'a':12}},
    {'outcomes':{'a':12,'b':101}},{'outcomes':{'a':True,'b':20}},
    {'outcomes':{'a':12,'b':'private-label-text'}},
])
def test_private_errors_hide_values(tmp_path,patch):
    study,labels,_=files(tmp_path);rewrite(tmp_path,'labels.json',{**labels,**patch})
    study['outcomes_sha256']=hashlib.sha256((tmp_path/'labels.json').read_bytes()).hexdigest()
    rewrite(tmp_path,'study.json',study)
    with pytest.raises(ValueError,match='Invalid host condition outcomes')as exc:load(tmp_path)
    assert 'private-label-text' not in str(exc.value)


@pytest.mark.parametrize('mutation',['unknown','duplicate','wrong_study','invalid_score','bad_abstention','extra'])
def test_prediction_integrity(tmp_path,mutation):
    _,_,p=files(tmp_path)
    if mutation=='unknown':p['predictions'][0]['candidate_id']='other'
    if mutation=='duplicate':p['predictions'][1]=p['predictions'][0]
    if mutation=='wrong_study':p['study_id']='other'
    if mutation=='invalid_score':p['predictions'][0]['value']=float('nan')
    if mutation=='bad_abstention':p['predictions'][0]['status']='abstained'
    if mutation=='extra':p['predictions'][0]['measured_yield']=88
    rewrite(tmp_path,'predictions.json',p)
    with pytest.raises(ValueError,match='condition predictions'):load(tmp_path)


def test_duplicate_json_keys(tmp_path):
    files(tmp_path);(tmp_path/'study.json').write_text('{"study_id":"a","study_id":"b"}')
    with pytest.raises(ValueError,match='public condition study'):load(tmp_path)


def test_input_size_bound(tmp_path):
    files(tmp_path);(tmp_path/'study.json').write_bytes(b' '*(2_000_001))
    with pytest.raises(ValueError,match='public condition study'):load(tmp_path)


@pytest.mark.parametrize('change',['conditions','recipe'])
def test_predictions_bound_to_chemical_inputs_not_only_ids(tmp_path,change):
    study,labels,_=files(tmp_path)
    if change=='conditions':study['candidates'][0]['conditions']['base']='Cl'
    else:study['candidates'][0]['recipe']['reagents']=['Cl']
    # A deliberately updated measured binding cannot authorize a stale predictor.
    labels={**labels,'candidate_inputs_sha256':condition_input_digest(study)}
    rewrite(tmp_path,'labels.json',labels)
    study['outcomes_sha256']=hashlib.sha256((tmp_path/'labels.json').read_bytes()).hexdigest()
    rewrite(tmp_path,'study.json',study)
    with pytest.raises(ValueError,match='condition predictions'):load(tmp_path)


def test_measured_outcomes_bound_to_chemical_inputs_without_predictor(tmp_path):
    study,_,_=files(tmp_path)
    study['candidates'][0]['conditions']['base']='Cl'
    rewrite(tmp_path,'study.json',study)
    with pytest.raises(ValueError,match='Invalid host condition outcomes'):load(tmp_path,False)
