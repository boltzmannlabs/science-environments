import json
import pytest
from synthesis_route_gym.tool_registry import ToolBinding, ToolRegistry


def binding(callback, **kwargs):
    return ToolBinding(callback=callback, version='fixture-v1', **kwargs)


def test_capabilities_have_schemas_and_explicit_availability():
    specs = ToolRegistry().describe()
    assert {s['name'] for s in specs} == {'expand','predict_conditions','retrieve_sources','forward_check','observe_condition','predict_impurities','compare_process','retrieve_biocatalysis','score_cn_conditions','predict_reaction_yield'}
    for spec in specs:
        assert spec['input_schema'] and spec['output_schema'] and spec['scope'] and spec['owner']
        assert spec['timeout_seconds'] > 0 and spec['availability'] == 'not_configured'
    result = ToolRegistry().invoke('retrosynthesis', {'smiles':'CCO'})
    assert result['status'] == 'unavailable' and result['capability'] == 'expand'
    assert result['usage']['backend_calls'] == 0


def test_aliases_canonical_inputs_and_host_controlled_provenance():
    seen = []
    def callback(args):
        seen.append(args)
        return {'status':'ok','predictions':[{'reactants':['C[OH:1]'], 'product':'OCC', 'score':.5,
            'source':{'tool':'forged','version':'wrong'}, 'evidence_status':'measured',
            'verified_by':'fake', 'raw_training_rows':[1]}], 'secret':'do not expose'}
    result = ToolRegistry({'expand': binding(callback)}).invoke('retrosynthesis', {'smiles':'OCC','top_k':1})
    assert seen == [{'smiles':'CCO','top_k':1}]
    row = result['data']['predictions'][0]
    assert row['reactants'] == ['CO'] and row['product'] == 'CCO'
    assert row['evidence_status'] == 'predicted' and row['source']['version'] == 'fixture-v1'
    assert 'fake' not in json.dumps(result) and 'secret' not in result
    assert result['usage']['backend_calls'] == 1
    assert result['provenance']['version_status'] == 'declared_not_artifact_verified'


@pytest.mark.parametrize('args', [{'smiles':'not chemical'}, {'smiles':'CCO','top_k':True},
    {'smiles':'CCO','path':'/private/evaluator.json'}, {'smiles':'CCO','top_k':101}])
def test_invalid_requests_do_not_call_backend(args):
    registry = ToolRegistry({'expand': binding(lambda _: pytest.fail('invalid call reached backend'))})
    result = registry.invoke('expand', args)
    assert result['status'] == 'error' and result['error']['code'] == 'invalid_request'
    assert result['usage']['backend_calls'] == 0


@pytest.mark.parametrize('raw', [None, {'status':'ok','predictions':[{'product':'CCO','reactants':['C'],'score':float('nan')}]},
    {'status':'ok','predictions':[{'product':'CCC','reactants':['C']}]}, {'status':'ok','predictions':'bad'}])
def test_malformed_or_wrong_product_is_not_a_prediction(raw):
    result = ToolRegistry({'expand':binding(lambda _:raw)}).invoke('expand', {'smiles':'CCO'})
    assert result['status'] == 'error' and result['data'] is None
    assert result['error']['code'] == 'invalid_result'


def test_callback_errors_are_sanitized():
    def failed(_): raise RuntimeError('password=private credential')
    result = ToolRegistry({'forward_check':binding(failed)}).invoke('forward_check', {'reactants':['C'],'product':'CC'})
    assert result['error']['code'] == 'backend_failed' and 'credential' not in json.dumps(result)


def test_cache_identity_covers_versions_snapshots_and_canonical_input():
    a = ToolRegistry({'expand':binding(lambda _: {}, model_version='model-1')}, stock_sha256='a'*64, evidence_sha256='b'*64)
    assert a.cache_identity('expand', {'smiles':'OCC'}) == a.cache_identity('retrosynthesis', {'smiles':'CCO'})
    b = ToolRegistry({'expand':binding(lambda _: {}, model_version='model-2')}, stock_sha256='a'*64, evidence_sha256='b'*64)
    c = ToolRegistry({'expand':binding(lambda _: {}, model_version='model-1')}, stock_sha256='c'*64, evidence_sha256='b'*64)
    assert len({r.cache_identity('expand', {'smiles':'CCO'}) for r in (a,b,c)}) == 3
    assert a.fingerprint != b.fingerprint


def test_unknown_alias_and_unversioned_callable_reject():
    assert ToolRegistry().invoke('terminal', {})['error']['code'] == 'unknown_capability'
    with pytest.raises(ValueError): ToolRegistry({'expand':lambda _: {}})
    with pytest.raises(ValueError): ToolBinding(lambda _: {}, version='')
    with pytest.raises(ValueError): ToolRegistry({'retrosynthesis':binding(lambda _: {})})


def test_observation_requires_explicit_host_replay_authority():
    with pytest.raises(ValueError): ToolRegistry({'observe_condition':binding(lambda _: {'yield_percent':55})})
    result = ToolRegistry({'observe_condition':binding(lambda _: {
        'candidate_id':'c','conditions':{'solvent':'O'},'yield_percent':55,
        'source_record_id':'source-1','dataset_sha256':'a'*64}, authority='measured_replay')}).invoke('observe_condition',{'candidate_id':'c'})
    assert result['status'] == 'ok' and result['evidence_kind'] == 'measured_dataset_replay'
    assert result['data']['new_experiment_performed'] is False


def test_forward_consistency_is_recomputed_not_trusted():
    result = ToolRegistry({'forward_check':binding(lambda _: {
        'predictions':[{'product':'CCO','score':.8}], 'feasible':True,'atom_balanced':True,
        'evidence_kind':'measured'})}).invoke('forward_check',{'reactants':['CC'],'product':'CCC'})
    assert result['status']=='ok' and result['data']['target_in_predictions'] is False
    assert result['data']['atom_balance_status'] == 'unknown_coproducts_not_provided'
    assert 'feasible' not in result['data']


def test_host_failures_are_uniform_and_availability_is_explicit():
    registry=ToolRegistry({'expand':binding(lambda _: {})})
    assert registry.available('retrosynthesis') is True
    assert registry.available('forward_check') is False
    result=registry.failure('expand','tool_timeout',backend_calls=1)
    assert result['status']=='error' and result['error']['code']=='tool_timeout'
    assert result['usage']['backend_calls']==1


def test_condition_predictions_preserve_bands_and_reject_id_or_band_errors():
    args={'candidates':[{'id':'c','aryl halide':'Clc1ccccc1','ligand':'P','additive':'O','base':'N'}]}
    row={'id':'c','predicted_yield_percent':50,'lower_yield_percent':30,'upper_yield_percent':70,
         'experimental_yield':99,'evidence_status':'measured'}
    result=ToolRegistry({'predict_conditions':binding(lambda _: {'predictions':[row]})}).invoke('conditions',args)
    assert result['status']=='ok'
    assert result['data']['predictions'][0]['evidence_status']=='predicted'
    assert result['data']['predictions'][0]['lower_yield_percent']==30
    assert 'experimental_yield' not in json.dumps(result)
    for change in ({'id':'other'}, {'lower_yield_percent':90}, {'predicted_yield_percent':True}):
        raw={'predictions':[{**row,**change}]}
        assert ToolRegistry({'predict_conditions':binding(lambda _:raw)}).invoke('conditions',args)['status']=='error'
    duplicate={'candidates':args['candidates']*2}
    assert ToolRegistry().invoke('conditions',duplicate)['error']['code']=='invalid_request'


def test_impurity_projection_deduplicates_excludes_product_and_drops_measurement_claims():
    raw={'predicted_smiles':['OCC','CO','OC'],'measured_impurities':['CO'],'metrics':{'precision':1},'concentration':8}
    result=ToolRegistry({'predict_impurities':binding(lambda _:raw)}).invoke('impurity_hypotheses',{'reactants':['CC'],'product':'CCO'})
    assert result['status']=='ok' and result['data']['predicted_smiles']==['CO']
    assert result['data']['metrics'] is None and result['data']['concentration'] is None


def test_source_projection_validates_digest_and_strips_host_review_status():
    from test_evidence_contracts import record,NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    corpus=FrozenEvidenceCorpus([record()],mode='evidence_retrieval',now=NOW)
    result=ToolRegistry({'retrieve_sources':binding(lambda args:corpus.retrieve(**args),authority='source_retrieval')}).invoke('source_retrieval',{'product':'CC=O'})
    assert result['status']=='ok' and result['data']['records'][0]['verification_status']=='not_attested'
    raw=corpus.retrieve()
    bad={**raw,'records':[{**raw['records'][0],'record_sha256':'f'*64}]}
    assert ToolRegistry({'retrieve_sources':binding(lambda _:bad,authority='source_retrieval')}).invoke('retrieve_sources',{})['status']=='error'
    closed=FrozenEvidenceCorpus([record()],mode='closed_information',now=NOW)
    denied=ToolRegistry({'retrieve_sources':binding(lambda args:closed.retrieve(**args),authority='source_retrieval')}).invoke('retrieve_sources',{})
    assert denied['status']=='unavailable' and denied['data'] is None


def test_process_comparison_requires_complete_common_basis_and_recomputes_pareto():
    common={'steps':2,'material_cost':12,'cost_currency':'USD','scale_mmol':1,'cost_basis':'supplied_feed_estimate',
            'cost_source_id':'quote-1','quoted_at':'2026-10-27','target':'CCO','price_status':'unverified_estimate',
            'inventory_sha256':'a'*64,'purity_basis':'pure','exclusions':['labor']}
    rows=[{'route_id':'a',**common},{'route_id':'b',**common,'material_cost':14}]
    registry=ToolRegistry({'compare_process':binding(lambda _: {'routes':rows,'pareto_route_ids':['b']},authority='estimate')})
    result=registry.invoke('compare_process',{'route_ids':['a','b']})
    assert result['status']=='ok' and result['data']['pareto_route_ids']==['a']
    assert result['data']['claims_manufacturing_savings'] is False
    rows[1]={**rows[1],'scale_mmol':2}
    unranked=registry.invoke('compare_process',{'route_ids':['a','b']})
    assert unranked['data']['unranked_route_ids']==['a','b']
    assert not unranked['data']['common_basis_known']


def test_biocatalysis_exact_product_is_recomputed_without_activity_or_yield_claim():
    raw={'candidates':[{'record_id':'r','enzyme_name':'recorded enzyme','source_url':'https://example.org/source',
        'source_locator':'record1','reactants':['CCO'],'products':['CC=O'],'match_kind':'exact_product',
        'experimental_yield':98,'claims_activity':True}]}
    registry=ToolRegistry({'retrieve_biocatalysis':binding(lambda _:raw,authority='source_retrieval')})
    result=registry.invoke('retrieve_biocatalysis',{'target_smiles':'CCO'})
    assert result['status']=='ok' and result['data']['candidates'][0]['match_kind']=='analogue'
    assert result['data']['candidates'][0]['experimental_yield'] is None
    assert result['data']['candidates'][0]['claims_activity'] is False


@pytest.mark.parametrize('change',[{'timeout_seconds':True},{'timeout_seconds':0},{'timeout_seconds':float('nan')},
    {'authority':'verified'},{'artifact_sha256':'bad'},{'configuration_version':''},{'callback':None}])
def test_malformed_bindings_reject(change):
    with pytest.raises(ValueError):
        ToolBinding(**{'callback':lambda _: {},'version':'v1',**change})


@pytest.mark.parametrize('raw',[{'status':'error','diagnostic':'SECRET'},{'status':'unavailable','secret':'SENSITIVE'},{'status':'pending'}])
def test_backend_error_messages_and_unknown_status_never_leak(raw):
    result=ToolRegistry({'expand':binding(lambda _:raw)}).invoke('expand',{'smiles':'CCO'})
    assert result['status'] in {'error','unavailable'}
    assert 'SECRET' not in json.dumps(result) and 'SENSITIVE' not in json.dumps(result)


def test_invalid_hosts_args_and_snapshots_reject():
    with pytest.raises(ValueError): ToolRegistry(stock_sha256='wrong')
    with pytest.raises(ValueError): ToolRegistry().canonical_name(3)
    assert ToolRegistry().invoke('expand',[])['error']['code']=='invalid_request'
    with pytest.raises(ValueError): ToolRegistry().failure('expand','INVALID!')
    with pytest.raises(ValueError): ToolRegistry().failure('expand','failure',message='')
    assert ToolRegistry().failure('expand','policy_blocked',message='Host policy denies access.')['error']['message']=='Host policy denies access.'


def test_descriptor_includes_full_envelope_schema_and_payload_scope():
    spec=ToolRegistry().describe()[0]
    assert spec['output_schema_scope']=='data'
    assert {'schema_version','capability','status','data','error','usage','provenance'} <= set(spec['result_schema']['properties'])


@pytest.mark.parametrize('anchor', ['binding','registry','both'])
def test_retrieval_rejects_response_from_a_different_corpus_snapshot(anchor):
    from test_evidence_contracts import record,NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    corpus=FrozenEvidenceCorpus([record()],mode='evidence_retrieval',now=NOW)
    raw=corpus.retrieve()
    bound=binding(lambda _:raw,authority='source_retrieval',artifact_sha256='b'*64 if anchor in {'binding','both'} else None)
    registry=ToolRegistry({'retrieve_sources':bound}, evidence_sha256='b'*64 if anchor in {'registry','both'} else None)
    result=registry.invoke('retrieve_sources',{})
    assert result['status']=='error' and result['error']['code']=='invalid_result'


def test_conflicting_host_corpus_snapshot_bindings_reject_at_construction():
    with pytest.raises(ValueError,match='snapshot'):
        ToolRegistry({'retrieve_sources':binding(lambda _: {},authority='source_retrieval',artifact_sha256='a'*64)},evidence_sha256='b'*64)


@pytest.mark.parametrize('query', [
    {'product':'CCO'}, {'reactants':['C']}, {'reactants':['CCO','CCO']}, {'query':'not-the-record'},
])
def test_source_callback_cannot_return_records_outside_requested_filters(query):
    from test_evidence_contracts import record,NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    corpus=FrozenEvidenceCorpus([record()],mode='evidence_retrieval',now=NOW)
    registry=ToolRegistry({'retrieve_sources':binding(lambda _:corpus.retrieve(),authority='source_retrieval',artifact_sha256=corpus.fingerprint)},evidence_sha256=corpus.fingerprint)
    result=registry.invoke('retrieve_sources',query)
    assert result['status']=='error' and result['data'] is None


def test_source_filter_canonical_aliases_and_duplicate_participants_are_preserved():
    from test_evidence_contracts import record,NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    corpus=FrozenEvidenceCorpus([record(reactants=['CCO','CCO'])],mode='evidence_retrieval',now=NOW)
    registry=ToolRegistry({'retrieve_sources':binding(lambda _:corpus.retrieve(),authority='source_retrieval',artifact_sha256=corpus.fingerprint)})
    assert registry.invoke('retrieve_sources',{'reactants':['OCC','CCO'],'product':'O=CC','query':'DOCUMENT-1'})['status']=='ok'
    assert registry.invoke('retrieve_sources',{'reactants':['OCC']})['status']=='error'


@pytest.mark.parametrize('quoted_at', ['not-a-date', '2026-99-27', ' 2026-10-27', '2026-02-30'])
def test_invalid_quote_date_keeps_process_comparison_unknown(quoted_at):
    raw={'routes':[{'route_id':'r','steps':1,'material_cost':12,'cost_currency':'USD','scale_mmol':1,
        'cost_basis':'supplied_feed_estimate','cost_source_id':'quote','quoted_at':quoted_at,'target':'CCO',
        'price_status':'unverified_estimate','inventory_sha256':'a'*64,'purity_basis':'pure'}]}
    result=ToolRegistry({'compare_process':binding(lambda _:raw,authority='estimate')}).invoke('compare_process',{'route_ids':['r']})
    assert result['status']=='ok'
    assert result['data']['common_basis_known'] is False
    assert result['data']['unranked_route_ids']==['r']
