"""Synthetic source-scoped ranking experiments; no private scientific outcomes."""
import json
import pytest
from synthesis_route_gym.cn_training import (
    run_cn_experiment, score_choices, make_choices, candidate_panel, bootstrap_difference,
)


def records():
    return tuple({'record_id':f'g{group:02}-c{condition}', 'group_id':f'group-{group:02}',
        'source_index':group*4+condition, 'aryl':'C'*group+'c1ccc(Br)cc1', 'amine':'CN',
        'product':'C'*group+'c1ccc(NC)cc1', 'catalyst':'[Pd]',
        'base':'N' if condition<2 else 'O', 'solvent':'O' if condition%2 else 'CCO',
        'label':int(condition>=2), 'reported_response':20.0 if condition>=2 else 0.0}
        for group in range(1,25) for condition in range(4))


def splits(rows):
    return {name:[i for i,r in enumerate(rows) if low<=int(r['group_id'][-2:])<=high]
        for name,low,high in [('train',1,14),('development',15,18),('calibration',19,21),('assessment',22,24)]}


def tiny_panel(monkeypatch):
    import synthesis_route_gym.cn_training as module
    original=candidate_panel()
    monkeypatch.setattr(module,'candidate_panel',lambda:tuple({**r,'config':{**r['config'],'n_estimators':3,'n_jobs':1}}
        if r['kind']=='forest' else r for r in original))


def test_group_macro_metric_penalizes_abstention_and_preserves_denominators():
    rows=[{'record_id':'a','group_id':'one','product':'CC','label':1},
          {'record_id':'b','group_id':'one','product':'CC','label':0},
          {'record_id':'c','group_id':'two','product':'CCC','label':0}]
    choices=make_choices(rows,[0.1,0.9,None])
    score=score_choices(rows,choices,[0.1,0.9,None])
    assert score['top_1_group_macro_regret']==1.0
    assert score['top_5_group_macro_regret']==0.5
    assert score['group_count']==2 and score['candidate_count']==3
    assert score['scored_candidate_count']==2
    assert score['missing_choice_count']==1


def test_choice_order_does_not_inspect_outcomes_or_input_order():
    rows=list(records()[:4]); changed=[{**r,'label':1-r['label']} for r in rows]
    assert make_choices(rows,[0.5]*4)==make_choices(changed,[0.5]*4)
    assert make_choices(rows,[0.5]*4)==make_choices(list(reversed(rows)),[0.5]*4)
    assert all('label' not in r for r in make_choices(rows,[0.5]*4))


def test_write_once_recipe_predictions_before_scoring_and_artifact_roundtrip(tmp_path,monkeypatch):
    tiny_panel(monkeypatch)
    import synthesis_route_gym.cn_training as module
    rows=records(); output=tmp_path/'experiment'; original=module.score_choices
    def observed(evaluated,choices,scores,raw_scores=None):
        if evaluated and evaluated[0]['group_id'] in {'group-22','group-23','group-24'}:
            assert (output/'assessment-decisions.json').exists()
            assert (output/'candidate-model.json').exists()
        assert (output/'recipe.json').exists()
        return original(evaluated,choices,scores,raw_scores)
    monkeypatch.setattr(module,'score_choices',observed)
    report=run_cn_experiment(rows,output,split=splits(rows),source_metadata={'kind':'synthetic'})
    assert report['final_run_authorized'] is False
    assert report['scope']=='source_scoped_development_holdout'
    assert report['baseline_selected'] in {r['name'] for r in candidate_panel() if r['arm']=='baseline'}
    assert len(report['development_trials'])==7
    assert report['existing_default_modified'] is False
    from synthesis_route_gym.cn_model import CNConditionModel
    predictor=CNConditionModel.load(output/'candidate-model.json')
    predictions=json.loads((output/'assessment-decisions.json').read_text())['candidate']['predictions']
    queries=[{k:r[k] for k in ('aryl','amine','catalyst','base','solvent','product')} for r in rows if r['group_id']=='group-22']
    assert [r['hit_score'] for r in predictor.predict(queries)]==[r['hit_score'] for r in predictions[:4]]
    assert set(report['calibration_record_ids']).isdisjoint(report['training_record_ids'])
    with pytest.raises(FileExistsError):
        run_cn_experiment(rows,output,split=splits(rows),source_metadata={'kind':'synthetic'})


def test_assessment_outcomes_do_not_change_fitted_models_or_choices(tmp_path,monkeypatch):
    tiny_panel(monkeypatch); rows=records(); split=splits(rows)
    changed=tuple({**r,'label':1-r['label'],'reported_response':11 if not r['label'] else 0}
        if i in split['assessment'] else r for i,r in enumerate(rows))
    run_cn_experiment(rows,tmp_path/'one',split=split,source_metadata={'kind':'synthetic'})
    run_cn_experiment(changed,tmp_path/'two',split=split,source_metadata={'kind':'synthetic'})
    for name in ['candidate-model.json','baseline-model.json','assessment-decisions.json']:
        assert (tmp_path/'one'/name).read_bytes()==(tmp_path/'two'/name).read_bytes()


def test_overlapping_groups_or_indices_and_missing_classes_fail_before_fit(tmp_path,monkeypatch):
    tiny_panel(monkeypatch); rows=records(); split=splits(rows)
    bad={**split,'assessment':[split['train'][0],*split['assessment']]}
    with pytest.raises(ValueError,match='[Pp]artition'):
        run_cn_experiment(rows,tmp_path/'overlap',split=bad,source_metadata={'kind':'synthetic'})
    single=tuple({**r,'label':0} if i in split['train'] else r for i,r in enumerate(rows))
    with pytest.raises(ValueError,match='classes'):
        run_cn_experiment(single,tmp_path/'single',split=split,source_metadata={'kind':'synthetic'})
    assert not (tmp_path/'single'/'candidate-model.json').exists()


def test_paired_bootstrap_is_deterministic_and_keeps_negative_findings():
    old={'per_group':[{'group_id':'a','top_1_regret':0.0},{'group_id':'b','top_1_regret':0.0}]}
    new={'per_group':[{'group_id':'a','top_1_regret':1.0},{'group_id':'b','top_1_regret':0.5}]}
    first=bootstrap_difference(old,new)
    assert first==bootstrap_difference(old,new)
    assert first['mean_regret_reduction']<0 and first['upper_95']<0
    assert first['scope']=='descriptive_scaffold_group_bootstrap_one_source'


@pytest.mark.parametrize('scores', [[float('nan')],[2],[-1],[]])
def test_invalid_scores_fail_closed(scores):
    with pytest.raises(ValueError):
        make_choices([{'record_id':'a','group_id':'g','product':'C'}],scores)


def test_calibration_plateau_preserves_raw_preference():
    rows=[{'record_id':'a','group_id':'g','product':'C'},
          {'record_id':'b','group_id':'g','product':'C'}]
    assert make_choices(rows,[.5,.5],[.1,.9])[0]['ordered_record_ids']==['b','a']
    with pytest.raises(ValueError,match='coverage'):
        make_choices(rows,[.5,None],[.1,.9])


def test_mean_baseline_unknown_condition_keeps_global_fallback():
    from synthesis_route_gym.cn_training import _fit, _predict
    rows=records()[:4]
    model=_fit(candidate_panel()[1],rows,{})
    unseen=[{**rows[0],'catalyst':'[Ni]'}]
    prediction=_predict(model,unseen)[0]
    assert prediction['status']=='scored' and prediction['hit_score']==.5


def test_calibration_constant_and_all_abstained_are_explicit(monkeypatch):
    import synthesis_route_gym.cn_training as module
    rows=records()[:4]
    model=module._fit(candidate_panel()[0],rows,{})
    calibrated,report=module._calibrate(model,rows)
    assert report['status']=='fitted_constant'
    assert calibrated['calibration']['x']==[0,1]
    original=dict(model)
    monkeypatch.setattr(module,'_predict',lambda model,rows:[{'status':'abstained','hit_score':None,'raw_hit_score':None} for _ in rows])
    unchanged,report=module._calibrate(model,rows)
    assert unchanged==original and report['status']=='unavailable_no_scored_candidates'
    assert report['before']['brier'] is None


def test_invalid_evaluation_choices_labels_and_bootstrap():
    rows=[{'record_id':'a','group_id':'g','product':'C','label':1}]
    with pytest.raises(ValueError,match='Choices'):
        score_choices(rows,[],[.5])
    with pytest.raises(ValueError,match='binary'):
        score_choices([{**rows[0],'label':2}],[],[.5])
    with pytest.raises(ValueError,match='Paired'):
        bootstrap_difference({'per_group':[]},{'per_group':[]})


def test_split_validation_rejects_group_leaks_and_duplicate_ids():
    from synthesis_route_gym.cn_training import _validate_split
    rows=records(); split=splits(rows)
    with pytest.raises(ValueError,match='four'):
        _validate_split(rows,{'train':list(range(len(rows)))})
    changed=[{**r,'record_id':'duplicate'} for r in rows]
    with pytest.raises(ValueError,match='unique'):
        _validate_split(changed,split)
    changed=[{**r,'group_id':'one-group'} for r in rows]
    with pytest.raises(ValueError,match='crosses'):
        _validate_split(changed,split)


def test_source_change_invalidates_experiment(tmp_path,monkeypatch):
    tiny_panel(monkeypatch)
    import synthesis_route_gym.cn_training as module
    calls=iter([{'a':'before'},{'a':'after'}])
    monkeypatch.setattr(module,'_code_hashes',lambda:next(calls))
    rows=records(); output=tmp_path/'changed'
    with pytest.raises(RuntimeError,match='invalidated'):
        run_cn_experiment(rows,output,split=splits(rows),source_metadata={'kind':'synthetic'})
    assert (output/'invalidated.json').exists()
    assert not (output/'evaluation.json').exists()


def test_production_wrapper_uses_verified_loader_and_frozen_split(tmp_path,monkeypatch):
    import synthesis_route_gym.cn_training as module
    import synthesis_route_gym.cn_data as data
    rows=records(); split=splits(rows); calls=[]
    monkeypatch.setattr(data,'load_cn_records',lambda path,sha:(calls.append((path,sha)) or (rows,{'verified':True})))
    monkeypatch.setattr(data,'frozen_split',lambda values:split if values==rows else pytest.fail('wrong source'))
    monkeypatch.setattr(module,'run_cn_experiment',lambda values,path,**kwargs:kwargs)
    result=module.train_cn_model('source.csv',tmp_path/'new',expected_sha256='hash')
    assert calls==[('source.csv','hash')]
    assert result=={'split':split,'source_metadata':{'verified':True}}


def test_novelty_diagnostics_are_input_only_and_report_reasons():
    from synthesis_route_gym.cn_training import _coverage_diagnostics
    training=records()[:4]; query=[{**training[0],'base':'[Na+]','label':1}]
    predictions=[{'status':'abstained','reason':'unknown_condition','hit_score':None,'raw_hit_score':None}]
    first=_coverage_diagnostics(query,predictions,training)
    second=_coverage_diagnostics([{**query[0],'label':0}],predictions,training)
    assert first==second
    assert first['novel_component_candidate_counts']['base']==1
    assert first['novel_component_candidate_counts']['solvent']==0
    assert first['abstention_reason_counts']=={'unknown_condition':1}


def test_missing_raw_score_fails_with_clear_contract_error(monkeypatch):
    import synthesis_route_gym.cn_training as module
    monkeypatch.setattr(module,'_predict',lambda model,rows:[{'status':'scored','hit_score':.5}])
    with pytest.raises(ValueError,match='raw_hit_score'):
        module._decision({},records()[:1])


def test_multiple_product_pools_are_averaged_before_groups():
    rows=[{'record_id':'a','group_id':'g1','product':'C','label':1},
          {'record_id':'b','group_id':'g1','product':'C','label':0},
          {'record_id':'c','group_id':'g1','product':'CC','label':0},
          {'record_id':'d','group_id':'g2','product':'CCC','label':1}]
    scores=[.1,.9,.2,.8]
    result=score_choices(rows,make_choices(rows,scores),scores)
    assert result['top_1_group_macro_regret']==.25
    assert result['product_count']==3 and result['group_count']==2


def test_probability_report_exposes_calibration_harm():
    from synthesis_route_gym.cn_training import _assessment_probability_diagnostics
    rows=[{'label':1},{'label':0}]
    predictions=[{'hit_score':.5,'raw_hit_score':.9},{'hit_score':.5,'raw_hit_score':.1}]
    result=_assessment_probability_diagnostics(rows,predictions)
    assert result['calibration_brier_change']>0
    assert result['calibration_harmed_assessment_brier'] is True
    assert result['retuning_permitted'] is False
