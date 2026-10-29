"""Pure critic advice stays bound to canonical host facts and source identities."""
import copy
import json
import subprocess
import sys
import pytest
from synthesis_route_gym.route_critic import (
    MAX_BYTES, build_context, context_fingerprint, parse_report, hydrate_report,
)

RESOURCES = {'remaining_model_calls':5,'remaining_tool_calls':10,
             'remaining_tokens':50000,'remaining_seconds':120.0}


def packet():
    route = {'route_id':'r1','target':'CCO','parent_route_id':None,'steps':[
        {'step_id':'s1','product':'CCO','reactants':[{'smiles':'CCBr','amount_mmol':None}],
         'reagents':[],'product_amount_mmol':None,'source_tool':'fixture','source_version':'v1',
         'proposal_score':None,'predicted_yield':None,'conditions':[],'condition_inputs':None,
         'evidence_ids':['source-1'],'required_equipment':[],'operations':[],
         'conditions_complete':False}]}
    assessment = {'route_id':'r1','graph_valid':True,'inventory_complete':False,
        'quantity_status':'not_requested','constraint_compliant':True,'acquisition_only':False,
        'evidence_status':{'s1':'proxy'},'conditions_evidence':{'s1':'unknown'},
        'cost':{'total':None,'known_subtotal':0.0,'currency':None,'missing_materials':['CCBr'],
                'scope':'starting_materials_and_reagents'},
        'findings':[{'code':'material_unavailable','severity':'error','message':'Unavailable input','step_id':None}],
        'unstocked':['CCBr'],'weak_steps':['s1'],'review_status':'pending','solved':False}
    source = {'record_id':'source-1','document_id':'source-doc','source_url':'https://example.org/source',
        'locator':'reaction 1','reactants':['CCBr'],'product':'CCO','claim_kind':'proxy',
        'conditions_scope':'unknown','conditions':[],'retrieved_at':'2026-01-01T00:00:00Z',
        'source_content_sha256':'1'*64,'visibility':'public_source','stereochemistry_scope':'as_encoded',
        'record_sha256':'2'*64,'reaction_sha256':'3'*64,'evidence_status':'source_claim',
        'verification_status':'not_attested','atom_balance_status':'unknown'}
    return {'schema_version':'srg-route-review-v1','task_sha256':'a'*64,
        'task':{'task_id':'task','target':'CCO','target_amount_mmol':None,'constraints':{
            'max_steps':8,'forbidden_smiles':[],'forbidden_smarts':[],'available_equipment':[],
            'forbidden_operations':[],'require_complete_conditions':False}},
        'routes':[route],'assessments':[assessment], 'inventory':[], 'sources':[source],
        'tool_results':[],
        'facts':[{'fact_id':'fact-stock','route_id':'r1','step_id':None,'category':'missing_materials',
                  'severity':'error','authority':'deterministic','source_record_ids':[],
                  'code':'material_unavailable','message':'Unavailable input'},
                 {'fact_id':'fact-source','route_id':'r1','step_id':'s1','category':'unsupported_transformation',
                  'severity':'review','authority':'source_consistency','source_record_ids':['source-1'],
                  'code':'source_scope','message':'Source connectivity is not experimental proof.'}],
        'recheck_menu':[{'recheck_id':'check-r1','action':'validate','arguments':{'route_id':'r1'}}]}


def context():return build_context(packet(),RESOURCES)


def finding(**changes):
    return {'route_id':'r1','step_id':None,'category':'missing_materials','severity':'error',
        'supporting_fact_ids':['fact-stock'],'source_record_ids':[],
        'requested_revision':'revise_route','rationale':'Resolve the declared missing input.',**changes}


def report(current,**changes):
    return {'schema_version':'srg-route-critic-report-v1','context_sha256':context_fingerprint(current),
        'findings':[finding()],'recommended_recheck_id':'check-r1','evidence_status':'agent_proposal',**changes}


def parse(current=None,**changes):
    current=current or context();return parse_report(json.dumps(report(current,**changes)),current)


def test_round_trip_hydrates_only_canonical_host_evidence():
    current=context(); result=parse(current)
    assert result==report(current)
    hydrated=hydrate_report(result,current)
    assert hydrated['findings'][0]['supporting_facts']==current['packet']['facts'][:1]
    assert hydrated['findings'][0]['source_records']==[]
    assert hydrated['recommended_recheck']==current['packet']['recheck_menu'][0]
    assert hydrated['evidence_status']=='agent_proposal'


def test_source_and_uncited_review_concerns_do_not_gain_error_authority():
    current=context()
    soft=finding(step_id='s1',category='unsupported_transformation',severity='review',
        supporting_fact_ids=['fact-source'],source_record_ids=['source-1'],requested_revision='retain_uncertainty')
    hydrated=hydrate_report(parse(current,findings=[soft]),current)
    assert hydrated['findings'][0]['source_records']==current['packet']['sources']
    assert parse(current,findings=[{**soft,'supporting_fact_ids':[],'source_record_ids':[]}])
    with pytest.raises(ValueError):parse(current,findings=[{**soft,'severity':'error'}])
    with pytest.raises(ValueError):parse(current,findings=[finding(supporting_fact_ids=[])])


def test_empty_report_and_no_recheck_are_valid_abstention():
    parsed=parse(findings=[],recommended_recheck_id=None)
    assert hydrate_report(parsed,context())['recommended_recheck'] is None


def test_outputs_detached_from_all_inputs():
    raw=packet(); resources=copy.deepcopy(RESOURCES); old=copy.deepcopy((raw,resources))
    current=build_context(raw,resources);parsed=parse(current);hydrated=hydrate_report(parsed,current)
    hydrated['findings'][0]['supporting_facts'][0]['message']='changed'
    current['packet']['routes'][0]['target']='O'
    assert (raw,resources)==old
    assert parsed['findings'][0]==finding()


@pytest.mark.parametrize('changes',[
    {'route_id':'unknown'}, {'step_id':'unknown'}, {'step_id':'s1'},
    {'category':'route_structure'}, {'supporting_fact_ids':['unknown']},
    {'source_record_ids':['unknown']}, {'supporting_fact_ids':['fact-stock','fact-stock']},
    {'source_record_ids':['source-1','source-1']}, {'rationale':' '}, {'rationale':'x'*601},
    {'severity':'fatal'},{'requested_revision':'deploy'}, {'supporting_facts':[]},
])
def test_invalid_finding_rejected(changes):
    with pytest.raises(ValueError):parse(findings=[finding(**changes)])


@pytest.mark.parametrize('changes',[
    {'context_sha256':'0'*64},{'recommended_recheck_id':'unknown'},
    {'evidence_status':'measured'}, {'findings':[finding(),finding()]},
    {'findings':[finding()]*9},{'extra':'not allowed'},
])
def test_invalid_report_rejected(changes):
    with pytest.raises(ValueError):parse(**changes)


def test_changed_context_cannot_reuse_report():
    current=context();raw=json.dumps(report(current))
    for edit in [lambda c:c['resources'].update(remaining_tokens=49999),
                 lambda c:c['packet']['facts'][0].update(message='Different host finding')]:
        changed=copy.deepcopy(current);edit(changed)
        assert context_fingerprint(current)!=context_fingerprint(changed)
        with pytest.raises(ValueError):parse_report(raw,changed)


@pytest.mark.parametrize('raw',[
    '[]','null','```json\n{}\n```','{"x":1,"x":2}','{"x":{"a":1,"a":2}}',
    '{"x":NaN}','{"x":Infinity}','x'*(MAX_BYTES+1),None,
])
def test_non_strict_json_rejected(raw):
    with pytest.raises(ValueError):parse_report(raw,context())


@pytest.mark.parametrize('key,value',[
    ('remaining_model_calls',-1),('remaining_tool_calls',True),('remaining_tokens',1.5),
    ('remaining_seconds',float('nan')),('remaining_seconds',float('inf')),
])
def test_invalid_resources_rejected(key,value):
    with pytest.raises(ValueError):build_context(packet(),{**RESOURCES,key:value})


@pytest.mark.parametrize('key',list(RESOURCES))
def test_exhausted_resources_suppress_context(key):
    assert build_context(packet(),{**RESOURCES,key:0}) is None


@pytest.mark.parametrize('edit',[
    lambda p:p.update(labels={'r1':False}),
    lambda p:p['sources'][0].update(verified_by='forged'),
    lambda p:p['sources'][0].update(verification_status='attested'),
    lambda p:p['routes'][0].update(hidden_label=True),
    lambda p:p['facts'][0].update(authority='chemical_truth'),
    lambda p:p['facts'][0].update(authority='source_consistency'),
    lambda p:p['facts'][0].update(route_id='other'),
    lambda p:p['facts'][1].update(step_id='other'),
    lambda p:p['facts'][1].update(source_record_ids=['other']),
    lambda p:p['facts'].append(copy.deepcopy(p['facts'][0])),
    lambda p:p['sources'].append(copy.deepcopy(p['sources'][0])),
    lambda p:p['routes'].append(copy.deepcopy(p['routes'][0])),
    lambda p:p['routes'][0]['steps'].append(copy.deepcopy(p['routes'][0]['steps'][0])),
    lambda p:p['assessments'][0].update(route_id='other'),
    lambda p:p['recheck_menu'][0].update(action='terminal'),
    lambda p:p['recheck_menu'][0]['arguments'].update(route_id='other'),
])
def test_malformed_or_private_host_packet_rejected(edit):
    raw=packet();edit(raw)
    with pytest.raises(ValueError):build_context(raw,RESOURCES)


def test_cross_route_fact_or_source_laundering_rejected():
    raw=packet();r=copy.deepcopy(raw['routes'][0]);r['route_id']='r2';r['steps'][0]['evidence_ids']=[]
    a=copy.deepcopy(raw['assessments'][0]);a['route_id']='r2';raw['routes'].append(r);raw['assessments'].append(a)
    current=build_context(raw,RESOURCES)
    for f in [finding(route_id='r2'),finding(route_id='r2',step_id='s1',severity='review',
                 supporting_fact_ids=[],source_record_ids=['source-1'])]:
        with pytest.raises(ValueError):parse(current,findings=[f])


def test_context_and_packet_overflow_rejected():
    raw=packet();raw['routes'][0]['steps'][0]['conditions']=['x'*2000]*100
    with pytest.raises(ValueError):build_context(raw,RESOURCES)
    current=context();current['resources']['secret']=42
    with pytest.raises(ValueError):context_fingerprint(current)


def test_import_never_loads_rdkit_or_chemistry():
    script='''import sys
class Block:
 def find_spec(self, fullname, *args):
  if fullname.startswith("rdkit") or fullname in {"synthesis_route_gym.schemas","synthesis_route_gym.chemistry"}:
   raise RuntimeError("Forbidden chemistry import")
sys.meta_path.insert(0,Block())
import synthesis_route_gym.route_critic
'''
    result=subprocess.run([sys.executable,'-c',script],capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def tool_result():
    return {'tool_result_id':'tool-1','action':'forward_check',
        'arguments':{'reactants':['CCBr'],'product':'CCO','top_k':1},
        'result':{'schema_version':'srg-scientific-tool-v1','capability':'forward_check',
            'status':'ok','data':{'predictions':[],'target_in_predictions':False,
                'atom_balance_status':'unknown_coproducts_not_provided',
                'scope':'model_consistency_not_experimental_feasibility'},
            'error':None,'provenance':{'registry_fingerprint':'a'*64,'stock_sha256':None,
                'evidence_sha256':None,'binding':None,'version_status':'declared_not_artifact_verified'},
            'usage':{'backend_calls':0,'request_units':1,'elapsed_seconds':0.0,'condition_observations':0},
            'evidence_kind':'predicted'}}


def test_tool_metadata_and_inventory_remain_public_and_identity_bound():
    raw=packet();raw['tool_results']=[tool_result()]
    item={'smiles':'CCBr','available_mmol':3.0,'price_per_mmol':None,'currency':None,'source':None,'quoted_at':None}
    raw['inventory']=[{'smiles':'CCBr','item':item}]
    current=build_context(raw,RESOURCES)
    assert current['packet']==raw
    raw['inventory'][0]['item']['smiles']='O'
    with pytest.raises(ValueError):build_context(raw,RESOURCES)


@pytest.mark.parametrize('edit',[
    lambda t:t.update(action='terminal'),
    lambda t:t['result'].update(capability='predict_conditions'),
    lambda t:t['result'].update(status='error'),
    lambda t:t['result'].update(error={'code':'failed','message':'Failed'}),
    lambda t:t['result'].update(status='error',error={'code':'failed','message':'Failed'}),
    lambda t:t.update(private_labels={'r1':False}),
])
def test_invalid_tool_public_projection_rejected(edit):
    raw=packet();t=tool_result();edit(t);raw['tool_results']=[t]
    with pytest.raises(ValueError):build_context(raw,RESOURCES)


def test_failed_scientific_tool_is_not_hidden_or_promoted():
    raw=packet();t=tool_result();t['result'].update(status='unavailable',data=None,
        error={'code':'unavailable','message':'Model unavailable'})
    raw['tool_results']=[t]
    assert build_context(raw,RESOURCES)['packet']['tool_results'][0]['result']['data']is None


@pytest.mark.parametrize('url',['file:///private/source','https://user:pass@example.org/source',
    'https://example.org/bad space','https://example.org:bad/source'])
def test_source_url_policy_rejects_private_or_malformed_locator(url):
    raw=packet();raw['sources'][0]['source_url']=url
    with pytest.raises(ValueError):build_context(raw,RESOURCES)


def test_source_time_requires_timezone_and_packet_is_finite_json():
    raw=packet();raw['sources'][0]['retrieved_at']='2026-01-01T00:00:00'
    with pytest.raises(ValueError):build_context(raw,RESOURCES)
    for value in [object(),float('inf')]:
        raw=packet();raw['task']['target_amount_mmol']=value
        with pytest.raises(ValueError):build_context(raw,RESOURCES)


@pytest.mark.parametrize('changed',[{},[],{'schema_version':'other','packet':{},'resources':{}}])
def test_invalid_context_envelope_rejected(changed):
    with pytest.raises(ValueError):context_fingerprint(changed)


def test_existing_context_cannot_exhaust_resources_after_hashing():
    current=context();current['resources']['remaining_model_calls']=0
    with pytest.raises(ValueError):context_fingerprint(current)


def test_real_host_packet_round_trip():
    from synthesis_route_gym.schemas import Task,RouteCandidate
    from synthesis_route_gym.validation import assess_route
    from synthesis_route_gym.route_review import build_route_review
    from synthesis_route_gym.evidence_contracts import SourceRecord,public_projection
    from datetime import datetime,timezone
    task=Task.model_validate({'task_id':'host-fixture','target':'CCO','inventory':[{'smiles':'CCBr'}]})
    route=RouteCandidate.model_validate(packet()['routes'][0])
    source=SourceRecord(record_id='source-1',document_id='fixture',source_url='https://example.org/fixture',
        locator='row 1',reactants=('CCBr',),product='CCO',claim_kind='proxy',
        retrieved_at=datetime(2026,1,1,tzinfo=timezone.utc),source_content_sha256='1'*64)
    host=build_route_review(task,[route],[assess_route(task,route)],sources=[public_projection(source)])
    current=build_context(host,RESOURCES)
    assert current['packet']==host
    for fact in host['facts']:
        concern=finding(route_id=fact['route_id'],step_id=fact['step_id'],category=fact['category'],
            severity=fact['severity'],supporting_fact_ids=[fact['fact_id']],source_record_ids=fact['source_record_ids'])
        parsed=parse(current,findings=[concern],recommended_recheck_id=host['recheck_menu'][0]['recheck_id'])
        assert hydrate_report(parsed,current)['findings'][0]['supporting_facts']==[fact]
