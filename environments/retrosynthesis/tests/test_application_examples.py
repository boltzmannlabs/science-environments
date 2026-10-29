"""Five local application examples exercise the shared CLI replay boundary."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
STEP = ROOT / 'artifacts/steps/srg-10'
LANES = ('inventory', 'conditions', 'impurities', 'process', 'biocatalysis')

# These reproduce archived Step 10 runs, including measured-data inputs that
# are deliberately absent from a source-only release. Core application tests
# in test_application_integration.py use self-contained synthetic fixtures.
ARCHIVE_INPUTS = (
    'prepare-examples.py', 'run-examples.py', 'inventory/fixture.json',
    *(f'conditions/example/{name}' for name in
      ('task.json', 'science-config.json', 'actions.json', 'provenance.json', 'route.json')),
    *(f'biocatalysis/{name}' for name in
      ('public-example.json', 'public-records.json', 'source-manifest.json',
       'rhea-58148.web.json', 'iubmb-3.1.1.113.web.json')),
)
if any(not (STEP / name).is_file() for name in ARCHIVE_INPUTS):
    pytest.skip('Optional archived Step 10 replay inputs are not bundled in the source-only release',
                allow_module_level=True)


def read(path): return json.loads(Path(path).read_bytes())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope='module')
def prepared(tmp_path_factory):
    folder=tmp_path_factory.mktemp('srg10-examples')/'examples'
    result=subprocess.run([sys.executable,str(STEP/'prepare-examples.py'),'--output-dir',str(folder)],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    return folder


def cli_replay(folder,lane,output):
    base=folder/lane
    return subprocess.run([sys.executable,'-m','synthesis_route_gym','replay',
      '--task',str(base/'task.json'),'--science-config',str(base/'science-config.json'),
      '--actions',str(base/'actions.json'),'--output',str(output)],cwd=ROOT,capture_output=True,text=True)


def test_preparation_is_idempotent_and_sources_are_hash_bound(prepared):
    manifest=read(prepared/'manifest.json')
    assert manifest['schema_version']=='srg10-application-examples-v1'
    assert {r['lane']for r in manifest['examples']}==set(LANES)
    for name,expected in manifest['source_inputs'].items(): assert sha(ROOT/name)==expected
    for name,expected in manifest['files'].items(): assert sha(prepared/name)==expected
    result=subprocess.run([sys.executable,str(STEP/'prepare-examples.py'),'--output-dir',str(prepared)],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert read(prepared/'manifest.json')==manifest


@pytest.mark.parametrize('lane',LANES)
def test_five_examples_run_through_shared_cli(prepared,tmp_path,lane):
    output=tmp_path/'run.json';result=cli_replay(prepared,lane,output)
    assert result.returncode==0,result.stderr
    episode=read(output);assert episode['terminated'] and not episode['truncated']
    reports=[e for e in episode['events']if e['action']=='application_report']
    assert len(reports)==1 and reports[0]['status']=='ok'
    report=reports[0]['result'];assert report['schema_version']=='srg-application-report-v1'
    assert report['claims_experimental_validation']is False
    assert report['route_references']
    expected=['ok']*len(episode['events'])
    if lane=='impurities':expected[1]='unavailable'
    assert [e['status']for e in episode['events']]==expected
    data=report['result']
    if lane=='inventory':
        assert data['eligible_route_ids']==['convergent']
        assert data['ineligible_route_ids']==['short','equipment']
    elif lane=='process':
        assert data['pareto_route_ids']==['convergent','direct']
        assert data['unranked_route_ids']==['incomplete_cost']
        assert [r['material_cost']for r in data['routes']]==[51,80,None]
        assert data['claims_manufacturing_savings']is False
    elif lane=='conditions':
        catalog=next(e['result']for e in episode['events']if e['action']=='condition_options')
        assert 'yield_percent'not in json.dumps(catalog)
        assert episode['scientific_usage']['observe_condition']==2
        assert data['route_step_yield_percent']is None
        assert len(data['observations'])==2
    elif lane=='impurities':
        assert data['prediction_status']=='unavailable'
        assert data['predicted_impurities']is None
        assert data['annotation_results']==[]
    elif lane=='biocatalysis':
        assert len(data['candidates'])==1
        assert data['candidates'][0]['match_kind']=='exact_substrates_product_projection'
        assert data['claims_experimental_validation']is False
        assert episode['scientific_usage']['retrieve_application_sources']==1


def test_preparation_refuses_changed_existing_inputs(prepared,tmp_path):
    result=subprocess.run([sys.executable,str(STEP/'prepare-examples.py'),'--output-dir',str(tmp_path/'examples')],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0
    target=tmp_path/'examples/inventory/task.json';target.write_text('{}')
    result=subprocess.run([sys.executable,str(STEP/'prepare-examples.py'),'--output-dir',str(tmp_path/'examples')],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode!=0
    assert target.read_text()=='{}'


def runner_module():
    spec=importlib.util.spec_from_file_location('srg10_example_runner',STEP/'run-examples.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def test_runner_rejects_unfrozen_source_or_existing_destination(prepared,tmp_path):
    runner=runner_module()
    with pytest.raises(ValueError):runner.verify_freeze({'files':{str(prepared/'manifest.json'):'0'*64}})
    with pytest.raises(ValueError):runner.verify_freeze({'files':{}})


def test_runner_failure_summary_preserves_unavailable_model(prepared,tmp_path):
    output=tmp_path/'impurities.json';result=cli_replay(prepared,'impurities',output);assert result.returncode==0
    runner=runner_module();summary=runner.summarize_episode('impurities',read(output))
    assert summary['scientific_validation']=='not_established'
    assert summary['failed_or_unavailable_actions']==1
    assert summary['model_inference_status']=='unavailable'
    assert summary['application_report_generated']is True


def synthetic_freeze(prepared,tmp_path):
    """Fake model bytes are frozen but never loaded; no scientific inference here."""
    repo=tmp_path/'fake-rebolt';checkpoint=repo/'retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model'
    checkpoint.mkdir(parents=True)
    model_files=[]
    for name in ('config.json','tokenizer.json','tokenizer_config.json','model.safetensors'):
        path=checkpoint/name;path.write_text('software-test-fixture-not-model');model_files.append(path)
    source=repo/'retrosynthesis/eval_impurity_t5.py';source.write_text('# software fixture only\n');model_files.append(source)
    manifest=read(prepared/'manifest.json')
    paths=[prepared/'manifest.json',STEP/'prepare-examples.py',STEP/'run-examples.py',Path(sys.executable).resolve(),
           *[prepared/name for name in manifest['files']],*[ROOT/name for name in manifest['source_inputs']],*model_files]
    freeze=tmp_path/'freeze.json';freeze.write_text(json.dumps({'files':{str(p):sha(p)for p in paths}}))
    return freeze,repo


def test_frozen_runner_executes_all_lanes_and_retains_unavailable_tool(prepared,tmp_path):
    runner=runner_module();freeze,repo=synthetic_freeze(prepared,tmp_path)
    def no_model_executor(command,**kwargs):
        return subprocess.run([s for s in command if s!='--impurity-model'],**kwargs)
    output=tmp_path/'run'
    result=runner.execute(prepared,freeze,output,repo_root=repo,chemistry_python=sys.executable,executor=no_model_executor)
    assert result['all_five_reports_generated'] and result['llm_calls']==0
    assert len(result['lanes'])==5
    assert next(r for r in result['lanes']if r['lane']=='impurities')['model_inference_status']=='unavailable'
    assert all(r['runner_failure']is None for r in result['lanes'])
    assert read(output/'summary.json')==result
    complete=read(output/'execution-complete.json');assert complete['summary_sha256']==sha(output/'summary.json')
    for name,expected in complete['files'].items():assert sha(output/name)==expected
    for lane in LANES:
        assert (output/lane/'application-report.json').is_file()
        assert (output/lane/'invocation.json').is_file()
    with pytest.raises(ValueError):
        runner.execute(prepared,freeze,output,repo_root=repo,chemistry_python=sys.executable,executor=no_model_executor)


@pytest.mark.parametrize('kind',['timeout','oserror','exit','malformed'])
def test_runner_preserves_cli_failures(prepared,tmp_path,kind):
    runner=runner_module();freeze,repo=synthetic_freeze(prepared,tmp_path)
    def fail(command,**kwargs):
        if kind=='timeout':raise subprocess.TimeoutExpired(command,1)
        if kind=='oserror':raise OSError('fixture')
        if kind=='malformed':Path(command[command.index('--output')+1]).write_text('{}')
        return subprocess.CompletedProcess(command,7 if kind=='exit'else 0,'fixture stdout','fixture stderr')
    result=runner.execute(prepared,freeze,tmp_path/'run',repo_root=repo,chemistry_python=sys.executable,executor=fail)
    assert not result['all_five_reports_generated']
    assert all(r['runner_failure'] for r in result['lanes'])
    assert all(r['scientific_validation']=='not_established'for r in result['lanes'])


def test_runner_missing_frozen_anchor_and_bad_configuration_fail_before_execution(prepared,tmp_path):
    runner=runner_module();freeze,repo=synthetic_freeze(prepared,tmp_path)
    value=read(freeze);value['files'].pop(str(STEP/'prepare-examples.py'));freeze.write_text(json.dumps(value))
    with pytest.raises(ValueError):runner.preflight(prepared,freeze,repo,sys.executable)
    for kwargs in ({'timeout':True},{'timeout':float('nan')},{'timeout':601},{'impurity_device':'remote'}):
        with pytest.raises(ValueError):runner.execute(prepared,freeze,tmp_path/'run',repo_root=repo,chemistry_python=sys.executable,**kwargs)


def prepare_module():
    spec=importlib.util.spec_from_file_location('srg10_examples_prepare',STEP/'prepare-examples.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def test_inprocess_preparer_validates_all_inputs_without_inference(tmp_path):
    module=prepare_module();folder=tmp_path/'prepared'
    value=module.prepare(folder)
    assert value['actual_model_inference_during_preparation']is False
    assert value['reserved_final_labels_opened']is False
    assert len(value['files'])==20
    assert module.prepare(folder)==value
    (folder/'inventory/task.json').write_text('{}')
    with pytest.raises(ValueError):module.prepare(folder)


def test_changed_condition_source_is_rejected_before_preparation(monkeypatch):
    module=prepare_module();original=module.sha
    monkeypatch.setattr(module,'sha',lambda p:'0'*64 if Path(p).name=='task.json'else original(p))
    with pytest.raises(ValueError):module.conditions_example()
