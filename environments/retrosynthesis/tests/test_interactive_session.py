"""Normal optional sessions preserve Agent Scientist's workflow ownership."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
from synthesis_route_gym.interactive_session import InteractiveSessions
from synthesis_route_gym.schemas import Budget
from test_core import make_task, make_route


def expand(target_smiles, top_k=10):
    return {'status':'ok','version':'synthetic-test-1','predictions':[
        {'product':target_smiles,'reactants':['CCO','CC(=O)O'],'score':0.8}]}


def call(host, action, arguments=None, session_id=None, profile='a'):
    return host.handle({'profile':profile,'action':action,'arguments':arguments or {},'session_id':session_id})


def reset(host, **kwargs):
    return call(host,'reset',{'task':make_task(**kwargs).model_dump(mode='json')})['session_id']


def test_reset_unbudgeted_has_no_expiry_and_is_profile_owned():
    now=[1.0]
    host=InteractiveSessions(clock=lambda:now[0])
    sid=reset(host,budget=Budget.unbudgeted())
    now[0]=10**10
    assert call(host,'inspect',session_id=sid)['observation']['status']=='ok'
    with pytest.raises(ValueError,match='Unknown'):
        call(host,'inspect',session_id=sid,profile='b')
    assert call(host,'close',session_id=sid)['closed']
    with pytest.raises(ValueError):call(host,'inspect',session_id=sid)


def test_finite_session_expires_without_resetting_budget():
    now=[1.0];host=InteractiveSessions(clock=lambda:now[0]);sid=reset(host)
    now[0]=20000
    with pytest.raises(ValueError,match='expired'):call(host,'inspect',session_id=sid)


@pytest.mark.parametrize('bad',[None,[],{'task':{}},{'task':make_task().model_dump(mode='json'),'seed':True},
    {'task':make_task().model_dump(mode='json'),'executable':'bad'}])
def test_reset_input_validation(bad):
    host=InteractiveSessions()
    with pytest.raises(ValueError):host.handle({'profile':'a','action':'reset','arguments':bad})


@pytest.mark.parametrize('algorithm',['breadth_first','best_first','synthchem_astar','synthchem_mcts','synthchem_portfolio'])
def test_search_keeps_session_open_for_agent_revision_and_submit(algorithm):
    host=InteractiveSessions(expand=expand);sid=reset(host)
    result=call(host,'generate_routes',{'search_policy':algorithm,'expansion_top_k':2},sid)
    assert result['submitted'] is False
    assert result['route_ids']
    state=call(host,'inspect',session_id=sid)['observation']
    assert state['status']=='ok'
    assert result['search_policy']==algorithm
    assert not host.sessions[('a',sid)][0].inspect()['terminated']
    for route_id in result['route_ids']:
        assert call(host,'validate',{'route_id':route_id},sid)['observation']['status']=='ok'
    submitted=call(host,'submit',{'route_ids':result['route_ids'][:1]},sid)
    assert submitted['observation']['status']=='ok'
    assert host.sessions[('a',sid)][0].inspect()['terminated']


@pytest.mark.parametrize('arguments',[{'search_policy':'unknown'},{'expansion_top_k':True},
    {'expansion_top_k':0},{'max_frontier_states':False},{'python':'/tmp/malicious'}])
def test_search_rejects_invalid_or_executable_arguments(arguments):
    host=InteractiveSessions(expand=expand);sid=reset(host)
    with pytest.raises(ValueError):call(host,'generate_routes',arguments,sid)


def test_import_then_rank_and_submit_preserves_predicted_evidence():
    host=InteractiveSessions();sid=reset(host)
    response=call(host,'import_routes',{'format':'srg-route-candidates-v1',
        'payload':[make_route().model_dump(mode='json')],
        'provenance':{'job_name':'retrosynthesis','doc_id':'synthetic-1'}},sid)
    assert response['import_report']['evidence_status']=='predicted'
    assert response['route_ids']==['r1']
    assert call(host,'rank_routes',{'route_ids':['r1']},sid)['observation']['status']=='ok'
    assert call(host,'submit',{'route_ids':['r1']},sid)['observation']['result']['accepted_route_ids']==['r1']


def test_capacity_is_explicit_and_close_releases_slot():
    host=InteractiveSessions(capacity=1);sid=reset(host)
    with pytest.raises(ValueError,match='capacity'):reset(host)
    call(host,'close',session_id=sid)
    assert reset(host)


def test_unknown_actions_profile_and_envelope_fail_closed():
    host=InteractiveSessions()
    for request in ({'profile':'a','action':'terminal','arguments':{}},
        {'profile':None,'action':'reset','arguments':{}},
        {'profile':'a','action':'inspect','arguments':{},'extra':1}):
        with pytest.raises(ValueError):host.handle(request)


def plugin():
    spec=importlib.util.spec_from_file_location('normal_plugin',Path(__file__).parents[1]/'integrations/agent_scientist/__init__.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_plugin_uses_installed_profile_runtime_without_shell_exports(tmp_path, monkeypatch):
    module=plugin()
    root=tmp_path/'package';(root/'src/synthesis_route_gym').mkdir(parents=True)
    runtime=tmp_path/'chemistry';runtime.write_text('python');runtime.chmod(0o755)
    model=tmp_path/'model';model.mkdir()
    heavy=tmp_path/'heavy';heavy.write_text('python')
    plugin_dir=tmp_path/'profile-plugin';plugin_dir.mkdir()
    (plugin_dir/'runtime.json').write_text(json.dumps({
        'SRG_PACKAGE_ROOT':str(root), 'SRG_CHEMISTRY_PYTHON':str(runtime),
        'REBOLT_ROOT':str(model), 'REBOLT_PYTHON':str(heavy),
        'SRG_BACKEND_TIMEOUT_SECONDS':'300'}))
    monkeypatch.setattr(module,'__file__',str(plugin_dir/'__init__.py'))
    for key in ('SRG_PACKAGE_ROOT','SRG_CHEMISTRY_PYTHON','REBOLT_ROOT','REBOLT_PYTHON',
                'SRG_BACKEND_TIMEOUT_SECONDS'):
        monkeypatch.delenv(key,raising=False)
    captured={}
    monkeypatch.setattr(module.subprocess,'Popen',lambda args,**kw:captured.update(args=args,**kw))
    module._ChemistryClient()._start()
    assert captured['args'][0]==str(runtime)
    assert captured['args'][-1]==str(root/'src')
    assert captured['env']['REBOLT_ROOT']==str(model)
    assert captured['env']['REBOLT_PYTHON']==str(heavy)
    assert captured['env']['SRG_BACKEND_TIMEOUT_SECONDS']=='300'


def test_plugin_rejects_unexpected_profile_runtime_fields(tmp_path,monkeypatch):
    module=plugin();plugin_dir=tmp_path/'profile-plugin';plugin_dir.mkdir()
    (plugin_dir/'runtime.json').write_text(json.dumps({'SRG_CHEMISTRY_PYTHON':'/usr/bin/python3',
        'unexpected':'do not execute'}))
    monkeypatch.setattr(module,'__file__',str(plugin_dir/'__init__.py'))
    with pytest.raises(RuntimeError,match='configuration'):
        module._ChemistryClient()._start()


def test_plugin_accepts_profile_runtime_without_localretro(tmp_path,monkeypatch):
    module=plugin();plugin_dir=tmp_path/'profile-plugin';plugin_dir.mkdir()
    root=tmp_path/'package';(root/'src/synthesis_route_gym').mkdir(parents=True)
    python=tmp_path/'python';python.write_text('test');python.chmod(0o755)
    (plugin_dir/'runtime.json').write_text(json.dumps({
        'SRG_PACKAGE_ROOT':str(root),'SRG_CHEMISTRY_PYTHON':str(python),
        'SRG_BACKEND_TIMEOUT_SECONDS':'120'}))
    monkeypatch.setattr(module,'__file__',str(plugin_dir/'__init__.py'))
    for key in module.RUNTIME_KEYS:monkeypatch.delenv(key,raising=False)
    captured={};monkeypatch.setattr(module.subprocess,'Popen',lambda args,**kw:captured.update(args=args,**kw))
    module._ChemistryClient()._start()
    assert captured['args'][0]==str(python)
    assert 'REBOLT_ROOT' not in captured['env']
    assert 'REBOLT_PYTHON' not in captured['env']


def test_plugin_rejects_partial_localretro_runtime(tmp_path,monkeypatch):
    module=plugin();plugin_dir=tmp_path/'profile-plugin';plugin_dir.mkdir()
    (plugin_dir/'runtime.json').write_text(json.dumps({
        'SRG_PACKAGE_ROOT':'/tmp/package','SRG_CHEMISTRY_PYTHON':'/usr/bin/python3',
        'SRG_BACKEND_TIMEOUT_SECONDS':'120','REBOLT_ROOT':'/tmp/model'}))
    monkeypatch.setattr(module,'__file__',str(plugin_dir/'__init__.py'))
    with pytest.raises(RuntimeError,match='configuration'):
        module._ChemistryClient()._start()


def test_plugin_normal_cross_runtime_preserves_other_tools(monkeypatch):
    module=plugin()
    monkeypatch.setenv('SRG_CHEMISTRY_PYTHON',sys.executable)
    monkeypatch.setitem(sys.modules,'sci_constants',SimpleNamespace(sci_home_key=lambda:'normal-a'))
    registered={'existing_retrosynthesis':object()}
    ctx=SimpleNamespace(register_tool=lambda **kw:registered.update({kw['name']:kw}))
    module.register(ctx)
    try:
        tool=registered['srg_action'];handler=tool['handler']
        result=json.loads(handler({'action':'reset','arguments':{'task':make_task().model_dump(mode='json')}}))
        assert result['session_id']
        sid=result['session_id']
        imported=json.loads(handler({'action':'import_routes','session_id':sid,'arguments':{
            'format':'srg-route-candidates-v1','payload':[make_route().model_dump(mode='json')]}}))
        assert imported['route_ids']==['r1']
        result=json.loads(handler({'action':'submit','session_id':sid,'arguments':{'route_ids':['r1']}}))
        assert result['observation']['status']=='ok'
        assert 'existing_retrosynthesis' in registered
        assert {'import_routes','generate_routes'}<=set(tool['schema']['parameters']['properties']['action']['enum'])
        assert json.loads(handler({'action':'terminal'}))['success'] is False
    finally:module._close_clients()


def test_plugin_bad_runtime_and_invalid_arguments_are_explicit(monkeypatch):
    module=plugin();monkeypatch.setenv('SRG_CHEMISTRY_PYTHON','/no/such/interpreter')
    monkeypatch.setitem(sys.modules,'sci_constants',SimpleNamespace(sci_home_key=lambda:'a'))
    ctx=SimpleNamespace(register_tool=lambda **kw:setattr(module,'tool',kw));module.register(ctx)
    for value in (None,[],{'action':'reset','arguments':[]},{'action':'reset','extra':1}):
        assert json.loads(module.tool['handler'](value))['success'] is False
    failed=json.loads(module.tool['handler']({'action':'reset','arguments':{'task':make_task().model_dump(mode='json')}}))
    assert failed['success'] is False
    assert 'runtime' in failed['error'].lower()
    module._close_clients()


def test_host_protocol_handles_multiple_requests_errors_and_eof(monkeypatch):
    import io
    import synthesis_route_gym.interactive_session as module
    requests=[{'profile':'a','action':'reset','arguments':{'task':make_task().model_dump(mode='json')}},
              {'profile':'a','action':'terminal','arguments':{}},
              {'profile':'a','action':'inspect','arguments':{'invalid':float('nan')}}]
    incoming=io.BytesIO(b''.join(json.dumps(row).encode()+b'\n' for row in requests))
    outgoing=io.BytesIO()
    monkeypatch.setattr(module.sys,'stdin',SimpleNamespace(buffer=incoming))
    monkeypatch.setattr(module.sys,'stdout',SimpleNamespace(buffer=outgoing))
    monkeypatch.setattr(module,'_configured_host',lambda:InteractiveSessions())
    module.main()
    responses=[json.loads(line) for line in outgoing.getvalue().splitlines()]
    assert responses[0]['session_id']
    assert responses[1]['success'] is False
    assert responses[2]['error_type']=='ValueError'


@pytest.mark.parametrize('data',[b'x'*30,b'no-newline'])
def test_host_protocol_rejects_oversize_and_incomplete_frames(monkeypatch,data):
    import io
    import synthesis_route_gym.interactive_session as module
    output=io.BytesIO()
    monkeypatch.setattr(module,'MAX_FRAME_BYTES',20)
    monkeypatch.setattr(module.sys,'stdin',SimpleNamespace(buffer=io.BytesIO(data)))
    monkeypatch.setattr(module.sys,'stdout',SimpleNamespace(buffer=output))
    monkeypatch.setattr(module,'_configured_host',lambda:InteractiveSessions())
    module.main()
    assert output.getvalue()==b''


def test_host_backend_only_uses_trusted_operator_environment(monkeypatch):
    import synthesis_route_gym.interactive_session as module
    import synthesis_route_gym.adapters as adapters
    captured=[]
    monkeypatch.setenv('REBOLT_ROOT','/operator/rebolt')
    monkeypatch.setenv('REBOLT_PYTHON','/operator/python')
    monkeypatch.setattr(adapters,'LocalRetroAdapter',lambda **kw:(captured.append(kw) or SimpleNamespace(expand=expand)))
    host=module._configured_host()
    assert host.expand is expand
    assert captured==[{'repo_root':'/operator/rebolt','python_executable':'/operator/python','timeout_seconds':120}]


def test_closed_episode_and_unbudgeted_search_caps_are_rejected():
    host=InteractiveSessions(expand=expand);sid=reset(host,budget=Budget.unbudgeted())
    with pytest.raises(ValueError,match='ceiling'):
        call(host,'generate_routes',{'max_frontier_states':10000},sid)
    call(host,'submit',{'route_ids':[]},sid)
    with pytest.raises(ValueError,match='closed'):call(host,'generate_routes',{},sid)
    with pytest.raises(ValueError):InteractiveSessions(capacity=False)


def test_import_duplicate_ids_and_malformed_arguments_are_explicit():
    host=InteractiveSessions();sid=reset(host)
    args={'format':'srg-route-candidates-v1','payload':[make_route().model_dump(mode='json')]}
    assert call(host,'import_routes',args,sid)['complete']
    with pytest.raises(ValueError,match='already exist'):call(host,'import_routes',args,sid)
    with pytest.raises(ValueError):call(host,'import_routes',{'payload':[]},sid)
    with pytest.raises(ValueError):call(host,'close',{'extra':1},sid)


def test_transport_does_not_forward_credentials_and_does_not_restart_lost_session(monkeypatch):
    import io
    module=plugin();captured=[]
    process=SimpleNamespace(stdin=io.BytesIO(),stdout=io.BytesIO(b'{"ok":true}\n'),poll=lambda:None)
    monkeypatch.setenv('OPENAI_API_KEY','synthetic-secret-not-real')
    monkeypatch.setenv('SCI_HOME','/synthetic/profile')
    monkeypatch.setenv('SRG_CHEMISTRY_PYTHON',sys.executable)
    monkeypatch.setattr(module.subprocess,'Popen',lambda *a,**kw:(captured.append(kw) or process))
    client=module._ChemistryClient()
    assert client.request({'profile':'a','action':'inspect'})=={'ok':True}
    assert 'OPENAI_API_KEY' not in captured[0]['env'] and 'SCI_HOME' not in captured[0]['env']
    process.poll=lambda:3
    with pytest.raises(RuntimeError,match='stopped'):client.request({'action':'inspect'})
    assert len(captured)==1
    client.close()


def test_transport_rejects_oversize_requests_and_invalid_response(monkeypatch):
    import io
    module=plugin();client=module._ChemistryClient()
    monkeypatch.setattr(module,'MAX_FRAME_BYTES',20)
    with pytest.raises(ValueError,match='capacity'):client.request({'argument':'x'*100})
    client.process=SimpleNamespace(stdin=io.BytesIO(),stdout=io.BytesIO(b'[]\n'),poll=lambda:0)
    # A response from a running but invalid protocol endpoint is rejected.
    client.process.poll=lambda:None
    monkeypatch.setattr(client,'close',lambda:None)
    with pytest.raises(RuntimeError,match='communication'):client.request({})


def test_plugin_closes_only_its_own_host_on_unload():
    module=plugin();callbacks=[]
    ctx=SimpleNamespace(register_tool=lambda **kw:None,on_unload=callbacks.append)
    module.register(ctx)
    assert len(callbacks)==1
    callbacks[0]()
    module._close_clients()


def test_transport_invalid_operator_source_fails_without_fallback(monkeypatch):
    module=plugin();monkeypatch.setenv('SRG_CHEMISTRY_PYTHON',sys.executable)
    monkeypatch.setenv('SRG_PACKAGE_ROOT','/no/such/checkout')
    with pytest.raises(RuntimeError,match='source unavailable'):
        module._ChemistryClient().request({})


@pytest.mark.parametrize('reply',[b'',b'{"ok":true}',b'x'*32,b'not-json\n'])
def test_transport_capacity_and_dead_host_are_explicit(monkeypatch,reply):
    import io
    module=plugin();client=module._ChemistryClient()
    monkeypatch.setattr(module,'MAX_REPLY_BYTES',24)
    client.process=SimpleNamespace(stdin=io.BytesIO(),stdout=io.BytesIO(reply),poll=lambda:None)
    closed=[];monkeypatch.setattr(client,'close',lambda:closed.append(True))
    with pytest.raises(RuntimeError):client.request({})
    assert closed


def test_bound_benchmark_cannot_enable_normal_only_actions(monkeypatch):
    from synthesis_route_gym.agent_runner import bind_executor
    module=plugin();ctx=SimpleNamespace(register_tool=lambda **kw:setattr(module,'tool',kw))
    module.register(ctx)
    with bind_executor(lambda *_:{'unsafe':True}):
        result=json.loads(module.tool['handler']({'action':'generate_routes'}))
    assert result['success'] is False
    assert 'not allowed' in result['error']
    module._close_clients()


def test_import_reports_budget_limited_partial_storage_without_success_claim():
    host=InteractiveSessions();sid=reset(host,budget=Budget(max_actions=2))
    other=make_route(route_id='r2').model_dump(mode='json')
    result=call(host,'import_routes',{'format':'srg-route-candidates-v1',
        'payload':[make_route().model_dump(mode='json'),other]},sid)
    assert result['complete'] is False
    assert result['route_ids']==['r1']
    assert result['observations'][-1]['status']=='closed'
    assert result['observations'][-1]['truncated'] is True


def test_configured_backend_timeout_matches_inner_worker_and_outer_registry(monkeypatch):
    import synthesis_route_gym.interactive_session as module
    import synthesis_route_gym.adapters as adapters
    captured=[]
    monkeypatch.setenv('REBOLT_ROOT','/operator/rebolt')
    monkeypatch.setenv('SRG_BACKEND_TIMEOUT_SECONDS','300')
    monkeypatch.setattr(adapters,'LocalRetroAdapter',lambda **kw:(captured.append(kw) or SimpleNamespace(expand=expand)))
    host=module._configured_host();sid=reset(host)
    description=host.sessions[('a',sid)][0]._scientific_tools.describe()
    assert captured[0]['timeout_seconds']==300
    assert next(d for d in description if d['name']=='expand')['timeout_seconds']==305


@pytest.mark.parametrize('value',['nan','inf','0','-1','3596','not-a-number'])
def test_bad_operator_backend_timeout_rejected(monkeypatch,value):
    import synthesis_route_gym.interactive_session as module
    monkeypatch.setenv('REBOLT_ROOT','/operator/rebolt')
    monkeypatch.setenv('SRG_BACKEND_TIMEOUT_SECONDS',value)
    with pytest.raises(ValueError):module._configured_host()


def test_empty_search_after_failed_prediction_is_not_frontier_success():
    host=InteractiveSessions(expand=lambda target_smiles,top_k=10: {'status':'unavailable','predictions':[],
        'diagnostic':'synthetic backend unavailable'})
    sid=reset(host)
    result=call(host,'generate_routes',{},sid)
    assert result['route_ids']==[]
    assert result['stop_reason']=='backend_failure'
    assert result['backend_failures']
    assert result['search_stop_reason']=='frontier_exhausted'


def test_configured_localretro_pins_assets_and_route_prediction_version(monkeypatch,tmp_path):
    import hashlib
    import synthesis_route_gym.interactive_session as module
    import synthesis_route_gym.adapters as adapters
    files=('req_data/LocalRetro_boltz_USPTO_MIT.pth','req_data/USPTO_MIT/atom_templates.csv',
        'req_data/USPTO_MIT/bond_templates.csv','req_data/USPTO_MIT/template_infos.csv',
        'rebolt_update_opt/localretro/LocalRetro/default_config.json',
        'rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py')
    for name in files:
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('synthetic-asset')
    digest=hashlib.sha256(b'synthetic-asset').hexdigest()
    def backend(**kwargs):return {**expand(**kwargs),'checkpoint_sha256':digest}
    monkeypatch.setenv('REBOLT_ROOT',str(tmp_path))
    monkeypatch.setattr(adapters,'LocalRetroAdapter',lambda **kw:SimpleNamespace(expand=backend))
    host=module._configured_host()
    result=call(host,'reset',{'task':make_task().model_dump(mode='json')})
    assert result['backend_assets']['checkpoint_sha256']==digest
    assert result['backend_assets']['status']=='complete'
    sid=result['session_id']
    predictions=call(host,'expand',{'smiles':make_task().target},sid)['observation']['result']
    assert predictions['predictions'][0]['source']['version']=='LocalRetro:sha256:'+digest
    assert predictions['tool_result']['provenance']['binding']['model_version']=='sha256:'+digest
    assert predictions['tool_result']['provenance']['binding']['artifact_sha256']==digest


def test_backend_identity_mismatch_rejected():
    import synthesis_route_gym.interactive_session as module
    checked=module._verified_localretro_expand(SimpleNamespace(expand=lambda **kw:{**expand(**kw),
        'checkpoint_sha256':'0'*64}),'1'*64)
    assert checked(target_smiles=make_task().target)['status']=='error'


def test_missing_assets_remain_unavailable_not_pinned(tmp_path):
    import synthesis_route_gym.interactive_session as module
    assets=module.localretro_asset_attestation(tmp_path)
    assert assets['status']=='incomplete'
    assert assets['checkpoint_sha256'] is None
    assert assets['missing']


def test_failed_expansion_keeps_nested_backend_error_code():
    host=InteractiveSessions(expand=lambda target_smiles,top_k=10:{'status':'unavailable','predictions':[]})
    sid=reset(host)
    result=call(host,'generate_routes',{},sid)
    assert result['backend_failures'][0]['code']=='backend_unavailable'
