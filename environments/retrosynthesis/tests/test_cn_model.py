"""Source-scoped hit models are predictions and abstain outside their contract."""
from copy import deepcopy
import json
import numpy as np
import pytest
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from synthesis_route_gym.cn_model import (
    CNConditionModel, CN_ROLES, FEATURE_VERSION, MODEL_SCHEMA,
    cn_features, cn_domain_matches, export_classifier,
)


def row(**updates):
    return {'aryl':'Brc1ccccc1','amine':'CN','catalyst':'[Pd]','base':'CCN(CC)CC',
            'solvent':'O','product':'CNc1ccccc1',**updates}


def metadata(rows=None):
    rows=rows or [row()]
    return {'model_version':'fixture-v1','training_component_smiles':{
        role:sorted({r[role] for r in rows}) for role in CN_ROLES},
        'substrate_similarity_threshold':0.2,'endpoint':'source_reported_CAD_response_gte_10_not_isolated_yield_or_general_feasibility'}


def artifact(rows=None):
    return {'schema_version':MODEL_SCHEMA,'feature_version':FEATURE_VERSION,
        'n_features':768,'metadata':metadata(rows),'calibration':None,
        'trees':[{'left':[-1],'right':[-1],'feature':[-2],'threshold':[-2.0],'value':[0.8]}]}


def test_features_ignore_outcomes_ids_and_sources_and_canonicalize():
    source=row()
    changed={**source,'id':'bad','Yield':999,'labels':0,'source':'answer'}
    assert np.array_equal(cn_features([source]),cn_features([changed]))
    assert np.array_equal(cn_features([source]),cn_features([row(aryl='c1ccccc1Br')]))
    assert cn_features([]).shape==(0,768)
    with pytest.raises(ValueError):cn_features([{'aryl':'C'}])
    with pytest.raises(ValueError):cn_features([row(amine='invalid!')])


@pytest.mark.parametrize('record,expected',[(row(),True),
    (row(amine='CNC',product='CN(C)c1ccccc1'),True),
    (row(aryl='Clc1ccccc1'),True),(row(aryl='Ic1ccccc1'),True),
    (row(product='CCO'),False),(row(aryl='Fc1ccccc1'),False),
    (row(amine='CN(C)C'),False),(row(amine='bad'),False),({},False)])
def test_structural_domain_requires_actual_cn_product(record,expected):
    assert cn_domain_matches(record) is expected


@pytest.mark.parametrize('estimator_type',[ExtraTreesClassifier,RandomForestClassifier])
def test_export_parity_and_safe_json_roundtrip(tmp_path,estimator_type):
    rows=[row(base='N'),row(),row(solvent='CCO'),row(aryl='Clc1ccccc1')]
    fitted=estimator_type(n_estimators=5,max_depth=3,random_state=7).fit(cn_features(rows),[0,1,0,1])
    raw=export_classifier(fitted,metadata(rows))
    path=tmp_path/'model.json';path.write_text(json.dumps(raw))
    model=CNConditionModel.load(path)
    results=model.predict(rows)
    assert np.allclose([r['hit_score'] for r in results],fitted.predict_proba(cn_features(rows))[:,1])
    assert all(r['status']=='scored' and r['evidence_status']=='predicted' for r in results)
    assert all('yield' not in r for r in results)


def test_prediction_abstains_per_candidate_and_does_not_mutate_input():
    raw=artifact();raw['metadata']['substrate_similarity_threshold']=0.99
    model=CNConditionModel(raw)
    records=[row(id='yes'),row(id='domain',product='CCO'),row(id='condition',catalyst='[Ni]'),
             row(id='distance',aryl='Brc1ncncn1',product='CNc1ncncn1')]
    before=deepcopy(records);out=model.predict(records)
    assert records==before
    assert out[0]['hit_score']==0.8 and out[0]['id']=='yes'
    assert out[1]['status']=='abstained' and out[1]['hit_score'] is None
    assert out[2]['reason']=='unseen_condition_component'
    assert out[3]['reason']=='substrate_similarity_below_threshold'
    assert model.predict([])==[]


def test_calibration_numeric_interpolation_is_not_transfer_guarantee():
    raw=artifact();raw['calibration']={'kind':'isotonic','x':[0,0.5,1],'y':[0,0.2,1]}
    out=CNConditionModel(raw).predict([row()])[0]
    assert out['hit_score']==pytest.approx(0.68)
    assert 'not_transfer_guarantee' in out['calibration_kind']
    assert out['reason'] is None


def test_artifact_and_metadata_are_defensively_copied():
    raw=artifact();model=CNConditionModel(raw)
    raw['trees'][0]['value'][0]=0
    returned=model.metadata;returned['model_version']='tampered'
    assert model.predict([row()])[0]['hit_score']==0.8
    assert model.metadata['model_version']=='fixture-v1'


@pytest.mark.parametrize('mutate',[
    lambda a:a.update(schema_version='unknown'),lambda a:a.update(feature_version='unknown'),
    lambda a:a.update(n_features=True),lambda a:a.update(extra='bad'),lambda a:a.update(trees=[]),
    lambda a:a['trees'][0].update(left=[0]),lambda a:a['trees'][0].update(value=[float('nan')]),
    lambda a:a['trees'][0].update(value=[1.1]),lambda a:a['trees'][0].update(extra='bad'),
    lambda a:a['metadata'].update(model_version=''),
    lambda a:a['metadata'].update(substrate_similarity_threshold=-1),
    lambda a:a['metadata']['training_component_smiles'].update(base=['bad!']),
    lambda a:a.update(calibration={'kind':'isotonic','x':[0,0.5,0.2],'y':[0,0.5,1]}),
    lambda a:a.update(calibration={'kind':'isotonic','x':[0,1],'y':[1,0]}),
])
def test_malformed_artifacts_rejected(mutate):
    raw=artifact();mutate(raw)
    with pytest.raises(ValueError):CNConditionModel(raw)


def test_loader_rejects_duplicate_keys_nonfinite_and_oversize(tmp_path):
    path=tmp_path/'bad.json';path.write_text('{"schema_version":"a","schema_version":"b"}')
    with pytest.raises(ValueError):CNConditionModel.load(path)
    path.write_text('{"n_features":NaN}')
    with pytest.raises(ValueError):CNConditionModel.load(path)
    with path.open('wb') as handle:handle.truncate(100_000_001)
    with pytest.raises(ValueError):CNConditionModel.load(path)


def test_export_rejects_missing_class_or_wrong_features():
    fitted=ExtraTreesClassifier(n_estimators=1).fit(cn_features([row()]),[0])
    with pytest.raises(ValueError):export_classifier(fitted,metadata())
    fitted=ExtraTreesClassifier(n_estimators=1).fit([[0],[1]],[0,1])
    with pytest.raises(ValueError):export_classifier(fitted,metadata())


def test_tree_malformed_array_raises_value_error():
    raw=artifact();raw['trees'][0]['left']=None
    with pytest.raises(ValueError):CNConditionModel(raw)


@pytest.mark.parametrize('rows',[None,'notrows',[row()]*1001])
def test_invalid_prediction_batches_rejected(rows):
    with pytest.raises(ValueError):CNConditionModel(artifact()).predict(rows)


@pytest.mark.parametrize('metadata_change',[
    {'extra':'x'}, {'endpoint':''}, {'training_component_smiles':{}},
    {'training_component_smiles':{**metadata()['training_component_smiles'],'base':[]}},
    {'training_component_smiles':{**metadata()['training_component_smiles'],'base':[[1]]}},
])
def test_metadata_contract_rejects_unknown_or_invalid_fields(metadata_change):
    raw=artifact();raw['metadata'].update(metadata_change)
    with pytest.raises(ValueError):CNConditionModel(raw)


def test_unreachable_and_duplicate_parent_tree_nodes_rejected():
    raw=artifact();raw['trees']=[{'left':[-1,-1],'right':[-1,-1],
      'feature':[-2,-2],'threshold':[-2,-2],'value':[0.5,0.5]}]
    with pytest.raises(ValueError,match='connected'):CNConditionModel(raw)


def test_artifact_accessor_is_deep_copy():
    model=CNConditionModel(artifact());copy=model.artifact
    copy['trees'][0]['value'][0]=0
    assert model.predict([row()])[0]['hit_score']==0.8


@pytest.mark.parametrize('amine,product',[('C[NH2]','CNc1ccccc1'),
    ('N1CCCCC1','c1ccc(N2CCCCC2)cc1')])
def test_primary_and_cyclic_secondary_hydrogen_decrement(amine,product):
    assert cn_domain_matches(row(amine=amine,product=product))


def test_constructor_rejects_oversize_serialized_model(monkeypatch):
    import synthesis_route_gym.cn_model as module
    monkeypatch.setattr(module,'MAX_MODEL_BYTES',10)
    with pytest.raises(ValueError,match='size'):CNConditionModel(artifact())


def test_model_rejects_different_scientific_endpoint():
    raw=artifact();raw['metadata']['endpoint']='isolated_yield_prediction'
    with pytest.raises(ValueError,match='endpoint'):CNConditionModel(raw)


def test_raw_hit_score_preserves_forest_before_isotonic_plateau():
    raw=artifact();raw['calibration']={'kind':'isotonic','x':[0,0.5,1],'y':[0.3,0.3,0.3]}
    scored,abstained=CNConditionModel(raw).predict([row(),row(catalyst='[Ni]')])
    assert scored['hit_score']==0.3
    assert scored['raw_hit_score']==0.8
    assert abstained['raw_hit_score'] is None and abstained['hit_score'] is None
    plain=CNConditionModel(artifact()).predict([row()])[0]
    assert plain['raw_hit_score']==plain['hit_score']==0.8
