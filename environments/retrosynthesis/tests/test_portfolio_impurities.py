"""Synthetic assay fixtures test contracts; none are experimental data."""
from copy import deepcopy
import pytest
from synthesis_route_gym.portfolio_impurities import ImpurityAnnotation, build_impurity_report, impurity_recipe_digest
from synthesis_route_gym.schemas import ReactionStep
from synthesis_route_gym.tool_registry import ToolBinding, ToolRegistry


def step(**changes):
    return {'step_id':'s1','reactants':[{'smiles':'CCOC(C)=O'},{'smiles':'O'}],
            'product':'CCO','reagents':[], 'source_tool':'fixture', 'source_version':'1',
            'conditions':['fixture temperature'], 'conditions_complete':True, **changes}


def prediction(s=None, values=('CC(=O)O','CO'), status='ok'):
    s=s or step();args={'reactants':[v['smiles'] for v in s['reactants']], 'product':s['product'], 'top_k':5}
    reg=ToolRegistry({'predict_impurities':ToolBinding(lambda args: {'status':status,'predicted_smiles':list(values)},'fixture-v1')})
    return {'action':'predict_impurities','arguments':args,'result':reg.invoke('predict_impurities',args)}


def limit(value=0.1,unit='mass_percent'):
    return {'value':value,'unit':unit,'basis':'of isolated crude product'}


def annotation(s=None,**changes):
    s=s or step()
    return {'annotation_id':'a1', 'reactants':[v['smiles']for v in s['reactants']],
            'product':s['product'],'recipe_sha256':impurity_recipe_digest(s),
            'source_url':'https://example.org/software-fixture','source_locator':'synthetic assay row',
            'source_content_sha256':'a'*64,'assay_method':'synthetic quantitative assay',
            'assay_scope':'Identified organic impurities above the stated reporting limit in this fixture sample.',
            'annotation_coverage':'partial','reporting_limit':limit(),
            'impurities':[{'smiles':'CC(=O)O','concentration':None}], **changes}


def test_no_annotation_is_hypothesis_only():
    r=build_impurity_report(step(),prediction=prediction())
    assert r['schema_version']=='srg-impurity-report-v1'
    assert r['predicted_impurities']==['CC(=O)O','CO']
    assert r['evaluation_status']=='no_matched_measurement_annotations'
    assert r['metrics'] is None and r['measured_impurities'] is None
    assert r['claims_experimental_validation'] is False


def test_no_prediction_does_not_become_empty_prediction_score():
    r=build_impurity_report(step(),annotations=[annotation()])
    assert r['prediction_status']=='not_run' and r['predicted_impurities'] is None
    assert r['annotation_results'][0]['metrics'] is None


def test_partial_labels_do_not_create_false_positives():
    r=build_impurity_report(step(),prediction=prediction(),annotations=[annotation()])
    row=r['annotation_results'][0];m=row['metrics']
    assert m['known_annotation_recall']==1 and m['true_positives']==1
    assert m['precision'] is None and m['recall'] is None and m['f1'] is None
    assert m['false_positives'] is None and m['unlabeled_predictions']==1
    assert row['evidence_status']=='host_supplied_measurement_claim'
    assert row['verification_status']=='not_independently_verified'


def test_complete_finite_assay_metrics_have_explicit_scope():
    r=build_impurity_report(step(),prediction=prediction(),annotations=[annotation(annotation_coverage='complete_within_assay_scope')])
    m=r['annotation_results'][0]['metrics']
    assert m['precision']==.5 and m['recall']==1 and m['f1']==pytest.approx(2/3)
    assert m['false_positives']==1 and m['false_negatives']==0
    assert m['scope']=='supplied_assay_identity_annotations_above_reporting_limit'
    assert r['metrics'] is None


def test_reporting_limit_required_for_complete_metric():
    a=annotation(annotation_coverage='complete_within_assay_scope',reporting_limit=None)
    assert build_impurity_report(step(),prediction=prediction(),annotations=[a])['annotation_results'][0]['metrics']['precision'] is None


def test_incomplete_recipe_cannot_establish_exhaustive_negative_labels():
    s=step(conditions_complete=False)
    r=build_impurity_report(s,prediction=prediction(s),annotations=[annotation(s,annotation_coverage='complete_within_assay_scope')])
    assert r['annotation_results'][0]['metrics']['precision'] is None
    assert 'route_recipe_incomplete' in r['annotation_results'][0]['metric_limitations']


@pytest.mark.parametrize('change,reason', [({'reactants':['CCOC(C)=O']},'reaction_mismatch'),
    ({'reactants':['CCOC(C)=O','O','O']},'reaction_mismatch'), ({'product':'CO'},'reaction_mismatch'),
    ({'recipe_sha256':'b'*64},'recipe_mismatch')])
def test_source_binding_mismatch_is_excluded(change,reason):
    r=build_impurity_report(step(),prediction=prediction(),annotations=[annotation(**change)])
    assert r['annotation_results']==[] and r['excluded_annotations'][0]['reason']==reason
    assert r['measured_impurities'] is None


@pytest.mark.parametrize('change', [
    {'conditions':['different']}, {'reagents':[{'smiles':'N'}]},
    {'reactants':[{'smiles':'CCOC(C)=O','amount_mmol':1},{'smiles':'O'}]},
    {'product_amount_mmol':1}, {'condition_inputs':{'solvent':'O'}},
    {'required_equipment':['reactor']}, {'operations':['heat']}, {'conditions_complete':False}])
def test_recipe_binds_process_fields(change):
    assert impurity_recipe_digest(step())!=impurity_recipe_digest(step(**change))


def test_recipe_ignores_identifiers_scores_and_participant_order():
    s=step();changed=step(step_id='changed',source_tool='different',predicted_yield=.8,reactants=list(reversed(s['reactants'])))
    assert impurity_recipe_digest(s)==impurity_recipe_digest(changed)
    assert impurity_recipe_digest(ReactionStep.model_validate(s))==impurity_recipe_digest(s)


def test_isotope_and_stereochemistry_are_preserved():
    assert impurity_recipe_digest(step(product='[13CH3]CO'))!=impurity_recipe_digest(step())
    assert impurity_recipe_digest(step(product='C[C@H](O)F'))!=impurity_recipe_digest(step(product='C[C@@H](O)F'))


def test_recorded_prediction_must_match_step():
    p=prediction();p['arguments']['reactants']+=['O']
    with pytest.raises(ValueError,match='reaction'):build_impurity_report(step(),prediction=p)


@pytest.mark.parametrize('status',['error','unavailable'])
def test_failed_prediction_retains_unknown_not_zero(status):
    r=build_impurity_report(step(),prediction=prediction(status=status),annotations=[annotation()])
    assert r['prediction_status']==status and r['predicted_impurities'] is None
    assert r['annotation_results'][0]['metrics'] is None


@pytest.mark.parametrize('field,value', [('capability','forward_check'),('evidence_kind','measured'),('data',{'predicted_smiles':['CO'],'concentration':.2})])
def test_prediction_authority_cannot_escalate(field,value):
    p=prediction();p['result'][field]=value
    with pytest.raises(ValueError):build_impurity_report(step(),prediction=p)


def test_prediction_binding_required():
    p=prediction();p['result']['provenance']['binding']=None
    with pytest.raises(ValueError):build_impurity_report(step(),prediction=p)


def test_prediction_rejects_wrong_authority():
    p=prediction();p['result']['provenance']['binding']['authority']='measured_replay'
    with pytest.raises(ValueError):build_impurity_report(step(),prediction=p)


def test_major_product_not_impurity_and_prediction_bound():
    p=prediction();p['result']['data']['predicted_smiles']=['CCO']
    with pytest.raises(ValueError):build_impurity_report(step(),prediction=p)
    p=prediction();p['arguments']['top_k']=1
    with pytest.raises(ValueError):build_impurity_report(step(),prediction=p)


def test_source_concentration_requires_units_method_quantitation_limit():
    a=annotation(quantitation_limit=limit(.05), impurities=[{'smiles':'CC(=O)O','concentration':limit(.2)}])
    r=build_impurity_report(step(),prediction=prediction(),annotations=[a])
    assert r['annotation_results'][0]['impurities'][0]['concentration']==limit(.2)
    assert r['predicted_concentrations'] is None


@pytest.mark.parametrize('change', [{'quantitation_limit':None}, {'quantitation_limit':limit(.3)},
    {'quantitation_limit':limit(.05,'mg_per_L')}, {'assay_method':''}])
def test_unquantified_concentration_rejected(change):
    a=annotation(quantitation_limit=limit(.05),impurities=[{'smiles':'CO','concentration':limit(.2)}]);a.update(change)
    with pytest.raises(ValueError):build_impurity_report(step(),annotations=[a])


@pytest.mark.parametrize('change', [
    {'source_url':'file:///private/data'}, {'source_url':'https://user:pass@example.org'},
    {'source_locator':' '}, {'source_content_sha256':'x'}, {'annotation_coverage':'all'},
    {'verified_by':'self'}, {'impurities':[{'smiles':'CCO'}]},
    {'impurities':[{'smiles':'CO'},{'smiles':'CO'}]}, {'assay_scope':''},
    {'reporting_limit':limit(-1)}, {'reporting_limit':limit(True)},
    {'reporting_limit':limit(float('nan'))}, {'reporting_limit':limit(101)},
    {'reporting_limit':limit(.1,'area_percent')},
    {'detection_limit':limit(.2),'quantitation_limit':limit(.1)}])
def test_invalid_host_annotation_rejected(change):
    with pytest.raises(ValueError):build_impurity_report(step(),annotations=[annotation(**change)])


def test_duplicate_ids_and_record_bounds_rejected():
    a=annotation()
    with pytest.raises(ValueError):build_impurity_report(step(),annotations=[a,a])
    with pytest.raises(ValueError):build_impurity_report(step(),annotations=[a]*101)
    with pytest.raises(ValueError):build_impurity_report(step(),annotations='bad')


def test_valid_empty_exhaustive_assay_does_not_claim_recall():
    a=annotation(annotation_coverage='complete_within_assay_scope',impurities=[])
    m=build_impurity_report(step(),prediction=prediction(),annotations=[a])['annotation_results'][0]['metrics']
    assert m['precision']==0 and m['recall'] is None and m['f1'] is None


def test_empty_prediction_against_known_annotation_zero_recall():
    m=build_impurity_report(step(),prediction=prediction(values=()),annotations=[annotation(annotation_coverage='complete_within_assay_scope')])['annotation_results'][0]['metrics']
    assert m['precision'] is None and m['recall']==0


def test_no_matches_with_complete_assay_has_zero_f1():
    m=build_impurity_report(step(),prediction=prediction(values=('N',)),annotations=[annotation(annotation_coverage='complete_within_assay_scope')])['annotation_results'][0]['metrics']
    assert m['f1']==0


def test_inputs_and_outputs_do_not_share_mutation():
    s,p,a=step(),prediction(),annotation();before=deepcopy((s,p,a))
    result=build_impurity_report(s,prediction=p,annotations=[a]);assert (s,p,a)==before
    result['annotation_results'][0]['impurities'][0]['smiles']='N';assert (s,p,a)==before
    row=ImpurityAnnotation.model_validate(a)
    with pytest.raises(ValueError):row.assay_method='changed'


def test_oversized_step_rejected():
    with pytest.raises(ValueError):build_impurity_report(step(conditions=['x'*1000001]))


def test_prediction_scope_does_not_imply_condition_inputs():
    r=build_impurity_report(step(),prediction=prediction())
    assert r['prediction_condition_scope']=='reaction_identity_only'


@pytest.mark.parametrize('reported', [limit(.3),limit(.1,'mg_per_L')])
def test_complete_assay_cannot_score_concentration_outside_reporting_scope(reported):
    a=annotation(annotation_coverage='complete_within_assay_scope',reporting_limit=reported,
        quantitation_limit=limit(.05),impurities=[{'smiles':'CO','concentration':limit(.2)}])
    with pytest.raises(ValueError,match='reporting'):build_impurity_report(step(),annotations=[a])


def test_quantitation_limit_above_reporting_limit_rejected():
    with pytest.raises(ValueError,match='reporting'):
        build_impurity_report(step(),annotations=[annotation(quantitation_limit=limit(.2))])
