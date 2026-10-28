"""Host wrappers never expose backend dictionaries or evaluator optima."""
import json
import pytest
from test_core import make_task, make_route, make_step
from synthesis_route_gym.scientific_bindings import build_default_registry
from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy


def test_expansion_reuses_callback_and_projects_raw_private_fields():
    seen = []
    def expand(smiles, top_k):
        seen.append((smiles, top_k))
        return {'status': 'ok', 'predictions': [{'reactants': ['CCO','CC(=O)O'],
            'product':'CCOC(C)=O','score':.3,'source':{'tool':'fake','version':'1'},
            'evidence_status':'measured','hidden_reference':'NO'}], 'private_training_rows':['NO']}
    result = build_default_registry(make_task(), expand=expand).invoke('expand', {'smiles':'CCOC(C)=O','top_k':2})
    assert result['status'] == 'ok'
    assert seen == [('CCOC(C)=O',2)]
    assert 'NO' not in json.dumps(result)
    assert result['data']['predictions'][0]['evidence_status'] == 'predicted'


def test_missing_models_remain_unavailable():
    registry = build_default_registry(make_task())
    assert registry.invoke('expand', {'smiles':'CCO','top_k':1})['status'] == 'unavailable'
    assert registry.invoke('forward_check', {'reactants':['CCO'],'product':'CCO'})['status'] == 'unavailable'


def test_condition_observation_reveals_only_queried_record():
    study = FiniteConditionStudy((ConditionRecord('one', (('ligand','P'),), 10),
        ConditionRecord('two', (('ligand','N'),), 99)), (), 1,
        'https://example.org/data', 'table1', 'a'*64, 'CCO')
    result = build_default_registry(make_task(), condition_study=study).invoke('observe_condition', {'candidate_id':'one'})
    assert result['status'] == 'ok'
    assert result['data']['yield_percent'] == 10
    assert 'optimum' not in json.dumps(result)
    assert 'two' not in json.dumps(result)
    assert study.observed_ids == ()


def test_condition_dataset_content_changes_registry_fingerprint():
    def study(value):
        return FiniteConditionStudy((ConditionRecord('one', (('ligand','P'),), value),), (), 1,
            'https://example.org/data', 'table1', 'a'*64, 'CCO')
    first = build_default_registry(make_task(), condition_study=study(10))
    second = build_default_registry(make_task(), condition_study=study(11))
    assert first.fingerprint != second.fingerprint


def test_process_comparison_uses_stored_routes_and_retains_unknown_prices():
    registry = build_default_registry(make_task(), route_lookup=lambda rid: make_route(route_id=rid))
    result = registry.invoke('compare_process', {'route_ids':['r1']})
    assert result['status'] == 'ok'
    assert result['data']['unranked_route_ids'] == ['r1']
    assert result['data']['routes'][0]['material_cost'] is None
    assert result['data']['claims_manufacturing_savings'] is False


def test_process_cannot_accept_agent_supplied_costs_or_paths():
    registry = build_default_registry(make_task(), route_lookup=lambda rid: make_route(route_id=rid))
    for args in ({'route_ids':['r1'],'cost':0},{'route_ids':['r1'],'path':'/private/evaluator.json'}):
        assert registry.invoke('compare_process', args)['status'] == 'error'


def test_unknown_condition_id_is_error_without_disclosing_records():
    study = FiniteConditionStudy((ConditionRecord('one', (('ligand','P'),), 99),), (), 1,
        'https://example.org/data', 'table1', 'a'*64, 'CCO')
    result = build_default_registry(make_task(), condition_study=study).invoke('observe_condition',{'candidate_id':'missing'})
    assert result['status'] == 'error'
    assert '99' not in json.dumps(result.get('data'))


def test_conditions_forward_and_impurities_use_typed_public_outputs():
    class Predictor:
        metadata = {'model_version':'fixture-1'}
        def predict(self, rows):
            return [{'predicted_yield_percent':12,'evidence_status':'measured','private':'NO'} for row in rows]
    class Impurity:
        def predict(self, reactants, product, top_k):
            return {'status':'ok','predicted_smiles':['CCO',product], 'measured_impurities':['CCO'], 'private':'NO'}
    study = FiniteConditionStudy((ConditionRecord('one',(('ligand','P'),),10),),(),1,'https://example.org','row1','a'*64,'CCO')
    registry = build_default_registry(make_task(), condition_ranker=Predictor(), impurity=Impurity(),
        condition_study=study, forward=lambda args:{'predictions':[{'product':args['product'],'score':.4}]})
    result = registry.invoke('predict_conditions', {'candidates':[{'id':'c1','aryl halide':'Clc1ccccc1','ligand':'P','additive':'O','base':'N'}]})
    assert result['status'] == 'ok'
    assert result['data']['predictions'][0]['model_version'] == 'fixture-1'
    assert 'NO' not in json.dumps(result)
    assert registry.invoke('forward_check', {'reactants':['CCO'],'product':'CCO'})['data']['target_in_predictions']
    result = registry.invoke('predict_impurities', {'reactants':['CCO','CC(=O)O'],'product':'CCOC(C)=O'})
    assert result['status'] == 'ok'
    assert result['data']['measured_impurities'] is None
    assert result['data']['predicted_smiles'] == ['CCO']


def test_incomplete_prediction_set_is_explicit_error():
    class Predictor:
        def predict(self, rows): return []
    result = build_default_registry(make_task(),condition_ranker=Predictor()).invoke('predict_conditions',
        {'candidates':[{'id':'c1','aryl halide':'Clc1ccccc1','ligand':'P','additive':'O','base':'N'}]})
    assert result['status'] == 'error'


def test_frozen_source_corpus_obeys_closed_and_retrieval_tracks():
    from test_evidence_contracts import record, NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    source = record()
    closed = build_default_registry(make_task(),evidence_corpus=FrozenEvidenceCorpus([source],now=NOW))
    assert closed.invoke('retrieve_sources', {'product':'CC=O'})['status'] == 'unavailable'
    open_registry = build_default_registry(make_task(), evidence_corpus=FrozenEvidenceCorpus([source],mode='evidence_retrieval',now=NOW))
    result = open_registry.invoke('retrieve_sources', {'product':'CC=O'})
    assert result['status'] == 'ok'
    assert result['data']['records'][0]['verification_status'] == 'not_attested'
    assert closed.fingerprint != open_registry.fingerprint


def test_known_process_cost_requires_explicit_common_basis():
    from synthesis_route_gym.schemas import InventoryItem, MaterialUse
    task = make_task(target_amount_mmol=1, inventory=(
        InventoryItem(smiles='CCO',available_mmol=2,price_per_mmol=1,currency='USD',source='fixturequote',quoted_at='2026-10-01'),
        InventoryItem(smiles='CC(=O)O',available_mmol=2,price_per_mmol=2,currency='USD',source='fixturequote',quoted_at='2026-10-01')))
    route = make_route(steps=(make_step(product_amount_mmol=1,reactants=(MaterialUse(smiles='CCO',amount_mmol=1),MaterialUse(smiles='CC(=O)O',amount_mmol=1))),))
    registry = build_default_registry(task,route_lookup=lambda ident:route,
        process_basis={'purity_basis':'declared_pure_target_mmol','exclusions':['workup','energy']})
    result = registry.invoke('compare_process', {'route_ids':['r1']})
    assert result['status'] == 'ok'
    assert result['data']['routes'][0]['material_cost'] == 3
    assert result['data']['pareto_route_ids'] == ['r1']
    assert not result['data']['claims_manufacturing_savings']
    assert registry.invoke('compare_process',{'route_ids':['r1'],'target_amount_mmol':2})['status'] == 'error'


def _bio_record():
    return {'record_id':'b1','enzyme_name':'reported alcohol dehydrogenase',
        'source_url':'https://example.org/fixture','source_locator':'synthetic test fixture',
        'evidence_kind':'curated_database','reactants':['CCO'],'products':['CC=O'],'cofactors':['O'],
        'experimental_yield':99,'private_training':'NO'}


def test_biocatalytic_records_are_inaccessible_in_closed_track():
    registry = build_default_registry(make_task(),biocatalytic_records=[_bio_record()])
    assert registry.invoke('retrieve_biocatalysis',{'target_smiles':'CC=O'})['status'] == 'unavailable'


def test_biocatalytic_retrieval_tracks_cofactors_without_activity_claims():
    registry = build_default_registry(make_task(),biocatalytic_records=[_bio_record()],source_access_mode='evidence_retrieval')
    result = registry.invoke('retrieve_biocatalysis',{'target_smiles':'CC=O'})
    assert result['status'] == 'ok'
    row = result['data']['candidates'][0]
    assert row['experimental_yield'] is None and row['claims_activity'] is False
    assert row['missing_reactants'] == ['O']
    assert 'NO' not in json.dumps(result)


@pytest.mark.parametrize('versions', [{'typo':{}},{'expand':{'authority':'measured_replay'}},['expand']])
def test_invalid_host_version_configuration_rejects(versions):
    with pytest.raises((ValueError,TypeError)):
        build_default_registry(make_task(),expand=lambda *args:{},backend_versions=versions)


@pytest.mark.parametrize('change', [
    {'budget':0}, {'observed_ids':('missing',)}, {'dataset_sha256':'bad'},
    {'_records':(ConditionRecord('one',(('ligand','P'),),True),)},
    {'_records':(ConditionRecord('one',(('ligand','P'),('ligand','N')),10),)},
])
def test_invalid_finite_study_configuration_rejects_before_registration(change):
    from dataclasses import replace
    study = FiniteConditionStudy((ConditionRecord('one',(('ligand','P'),),10),),(),1,
        'https://example.org','row1','a'*64,'CCO')
    with pytest.raises(ValueError):
        build_default_registry(make_task(),condition_study=replace(study,**change))


def test_source_policy_configuration_cannot_conflict_with_corpus():
    from test_evidence_contracts import NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    for mode in ('invalid','evidence_retrieval'):
        with pytest.raises(ValueError):
            build_default_registry(make_task(),evidence_corpus=FrozenEvidenceCorpus(now=NOW),source_access_mode=mode)


def test_biocatalytic_retrieval_preserves_participant_multiplicities():
    record = {**_bio_record(), 'reactants':['OCC','CCO'], 'products':['CC=O','O=CC']}
    registry = build_default_registry(make_task(), biocatalytic_records=[record], source_access_mode='evidence_retrieval')
    row = registry.invoke('retrieve_biocatalysis', {'target_smiles':'CC=O'})['data']['candidates'][0]
    assert row['reactants'] == ['CCO','CCO']
    assert row['products'] == ['CC=O','CC=O']


@pytest.mark.parametrize('quoted_at', ['not-a-date', '2026-99-99', ' ', '2026'])
def test_invalid_quote_dates_keep_process_cost_unknown(quoted_at):
    from synthesis_route_gym.schemas import InventoryItem, MaterialUse
    task = make_task(target_amount_mmol=1, inventory=(
        InventoryItem(smiles='CCO',available_mmol=2,price_per_mmol=1,currency='USD',source='fixturequote',quoted_at=quoted_at),
        InventoryItem(smiles='CC(=O)O',available_mmol=2,price_per_mmol=2,currency='USD',source='fixturequote',quoted_at='2026-10-01')))
    route = make_route(steps=(make_step(product_amount_mmol=1,reactants=(MaterialUse(smiles='CCO',amount_mmol=1),MaterialUse(smiles='CC(=O)O',amount_mmol=1))),))
    registry = build_default_registry(task, route_lookup=lambda ident:route,
        process_basis={'purity_basis':'declared_pure_target_mmol','exclusions':['workup']})
    result = registry.invoke('compare_process', {'route_ids':['r1']})
    assert result['status'] == 'ok'
    assert result['data']['routes'][0]['material_cost'] is None
    assert result['data']['unranked_route_ids'] == ['r1']
