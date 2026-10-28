"""Pretrained yield adapters keep scientific inputs and artifact identities explicit."""
import hashlib
import json
import subprocess
import sys

import pytest

from synthesis_route_gym.public_yield import ReactionT5YieldPredictor, format_reaction
from synthesis_route_gym.reactiont5_worker import run_predictions

FILES = ('config.json', 'tokenizer.json', 'tokenizer_config.json',
         'special_tokens_map.json', 'model.safetensors')

@pytest.fixture
def manifest(tmp_path):
    model = tmp_path / 'model'
    model.mkdir()
    for name in FILES:
        (model / name).write_text('{}')
    data = {'schema_version':'srg-public-yield-model-v1', 'model_dir':'model',
            'python_executable':sys.executable,
            'files':{name:hashlib.sha256((model / name).read_bytes()).hexdigest() for name in FILES},
            'model_version':'test-yield-v1', 'model_revision':'a'*40,
            'source_url':'https://huggingface.co/sagawa/ReactionT5v2-yield', 'license':'MIT'}
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(data))
    return path


def candidate(**changes):
    return {'id':'c1', 'reactants':['OCC'], 'reagents':['[Na+].[OH-]'], 'product':'CC=O', **changes}


def fake_run(monkeypatch, payload=None, code=0):
    seen = {}
    def run(command, **kwargs):
        seen.update({'command':command, **kwargs})
        kwargs['stdout'].write(json.dumps(payload or {'predictions':[{'id':'c1','raw_yield_percent':42.0,'reason':None}]}).encode())
        return subprocess.CompletedProcess(command, code)
    monkeypatch.setattr(subprocess, 'run', run)
    return seen


def test_formats_roles_canonical_stereochemistry_and_salts():
    value = format_reaction(candidate(reactants=['N[C@@H](C)C(=O)O']))
    assert value.startswith('REACTANT:C[C@H](N)C(=O)OREAGENT:')
    assert value.endswith('PRODUCT:CC=O')
    assert '[Na+]' in value and '[OH-]' in value


def test_local_subprocess_predicts_and_pins_identity(manifest, monkeypatch):
    seen = fake_run(monkeypatch)
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    result = model.predict([candidate()])
    assert result[0]['predicted_yield_percent'] == 42.0
    assert result[0]['evidence_status'] == 'predicted'
    assert result[0]['uncertainty_kind'] == 'not_calibrated'
    assert result[0]['status'] == 'scored'
    assert seen['command'][1] == '-I'
    assert seen['env']['HF_HUB_OFFLINE'] == '1'
    assert 'shell' not in seen
    payload = json.loads(seen['input'])
    assert payload['rows'][0]['text'] == format_reaction(candidate())
    assert model.configuration['worker_sha256']
    copy = model.artifact
    copy['files']['config.json'] = 'bad'
    assert model.artifact['files']['config.json'] != 'bad'


@pytest.mark.parametrize('row', [candidate(yield_percent=42), candidate(product='invalid'),
    candidate(id=''), candidate(reactants=[]), candidate(reagents='O'), candidate(product=True)])
def test_invalid_or_label_bearing_inputs_fail_before_backend(manifest, monkeypatch, row):
    seen = fake_run(monkeypatch)
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    with pytest.raises(ValueError):
        model.predict([row])
    assert not seen


def test_duplicate_and_oversized_candidate_batches_rejected(manifest):
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    for rows in ([], [candidate(), candidate()], [candidate(id=str(i)) for i in range(101)]):
        with pytest.raises(ValueError):
            model.predict(rows)


def test_changed_model_assets_rejected_on_load_and_predict(manifest):
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    (manifest.parent / 'model' / 'model.safetensors').write_text('changed')
    with pytest.raises(ValueError, match='digest'):
        model.predict([candidate()])
    with pytest.raises(ValueError, match='digest'):
        ReactionT5YieldPredictor.from_manifest(manifest)


@pytest.mark.parametrize('change', [ {'files':{'../escape':'a'*64}}, {'device':'arbitrary'},
    {'timeout_seconds':float('nan')}, {'max_tokens':100000}, {'extra':'ignored'},
    {'model_revision':'main'}, {'source_url':'https://user:password@example.org/model'} ])
def test_invalid_manifest_rejected(manifest, change):
    original = json.loads(manifest.read_text())
    manifest.write_text(json.dumps({**original, **change}))
    with pytest.raises(ValueError):
        ReactionT5YieldPredictor.from_manifest(manifest)


@pytest.mark.parametrize('raw', [-1, 101])
def test_out_of_range_predictions_abstain_without_clipping(manifest, monkeypatch, raw):
    fake_run(monkeypatch, {'predictions':[{'id':'c1','raw_yield_percent':raw,'reason':None}]})
    result = ReactionT5YieldPredictor.from_manifest(manifest).predict([candidate()])[0]
    assert result['status'] == 'abstained'
    assert result['predicted_yield_percent'] is None
    assert result['raw_yield_percent'] == raw
    assert result['reason'] == 'prediction_out_of_range'


@pytest.mark.parametrize('payload', [ {'predictions':[]},
    {'predictions':[{'id':'other','raw_yield_percent':20,'reason':None}]},
    {'predictions':[{'id':'c1','raw_yield_percent':float('nan'),'reason':None}]},
    {'predictions':[{'id':'c1','raw_yield_percent':20,'reason':'token_limit_exceeded'}]} ])
def test_invalid_worker_output_rejected(manifest, monkeypatch, payload):
    fake_run(monkeypatch, payload)
    with pytest.raises(ValueError):
        ReactionT5YieldPredictor.from_manifest(manifest).predict([candidate()])


def test_backend_failures_and_timeouts_are_explicit(manifest, monkeypatch):
    fake_run(monkeypatch, code=1)
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    with pytest.raises(RuntimeError, match='failed'):
        model.predict([candidate()])
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 1)
    monkeypatch.setattr(subprocess, 'run', timeout)
    with pytest.raises(TimeoutError):
        model.predict([candidate()])


def test_worker_abstains_without_truncating_or_scoring_unknown_tokens():
    values = {'long':[1,2,3,4], 'unknown':[1,9], 'ok':[1,2]}
    calls = []
    def infer(ids):
        calls.append(ids)
        return 23.5
    rows = [{'id':key,'text':key} for key in values]
    result = run_predictions(rows, lambda text:values[text], infer, max_tokens=3, unknown_id=9)
    assert [row['reason'] for row in result] == ['token_limit_exceeded','unknown_token',None]
    assert calls == [[1,2]]
    assert result[-1]['raw_yield_percent'] == 23.5


def test_worker_nonfinite_predictions_abstain():
    result = run_predictions([{'id':'c1','text':'example'}], lambda _: [1],
                             lambda _: float('inf'), max_tokens=512, unknown_id=9)
    assert result == [{'id':'c1','raw_yield_percent':None,'reason':'nonfinite_prediction'}]


def test_missing_fields_and_non_records_fail_cleanly(manifest, monkeypatch):
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    seen = fake_run(monkeypatch)
    for row in (None, {}, {'reactants':['C']}, candidate(id=True)):
        with pytest.raises(ValueError):
            model.predict([row])
    assert not seen


def test_interpreter_symlink_keeps_environment_identity(manifest, tmp_path):
    path = tmp_path / 'python'
    path.symlink_to(sys.executable)
    data = json.loads(manifest.read_text())
    manifest.write_text(json.dumps({**data,'python_executable':str(path)}))
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    assert model.artifact['python_executable'] == str(path)


def test_worker_main_and_digest_validation(manifest, monkeypatch):
    import io
    from synthesis_route_gym import reactiont5_worker as worker
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    worker._verify(model.artifact)
    payload = {'manifest':model.artifact,'rows':[{'id':'c1','text':'reaction'}]}
    monkeypatch.setattr(worker.sys, 'stdin', type('Input', (), {'buffer':io.BytesIO(json.dumps(payload).encode())})())
    output = io.StringIO()
    monkeypatch.setattr(worker.sys, 'stdout', output)
    monkeypatch.setattr(worker,'load_backend',lambda _: (lambda _: [1,2],lambda _: 31.0,9))
    worker.main()
    assert json.loads(output.getvalue())['predictions'][0]['raw_yield_percent'] == 31
    changed = {**model.artifact,'files':{**model.artifact['files'],'config.json':'f'*64}}
    with pytest.raises(ValueError, match='digest'):
        worker._verify(changed)
    with pytest.raises(ValueError, match='version'):
        worker._verify({**model.artifact,'runtime_versions':{'pytest':'impossible'}})


def test_worker_main_rejects_unbounded_inputs(monkeypatch):
    import io
    from synthesis_route_gym import reactiont5_worker as worker
    for raw in (b'x'*2_000_001, json.dumps({'manifest':{},'rows':[]}).encode()):
        monkeypatch.setattr(worker.sys,'stdin',type('Input',(),{'buffer':io.BytesIO(raw)})())
        with pytest.raises(ValueError):
            worker.main()


def test_worker_abstentions_are_public_and_finite(manifest, monkeypatch):
    fake_run(monkeypatch, {'predictions':[{'id':'c1','raw_yield_percent':None,'reason':'unknown_token'}]})
    value = ReactionT5YieldPredictor.from_manifest(manifest).predict([candidate()])[0]
    assert value['status'] == 'abstained' and value['predicted_yield_percent'] is None


def test_runtime_mutation_and_unbounded_outputs_fail(manifest, monkeypatch):
    model = ReactionT5YieldPredictor.from_manifest(manifest)
    monkeypatch.setattr(model,'_configuration',{**model.configuration,'worker_sha256':'f'*64})
    with pytest.raises(ValueError, match='runtime digest'):
        model.predict([candidate()])
    fresh = ReactionT5YieldPredictor.from_manifest(manifest)
    def oversized(command, **kwargs):
        kwargs['stdout'].write(b'x'*2_000_001)
        return subprocess.CompletedProcess(command,0)
    monkeypatch.setattr(subprocess,'run',oversized)
    with pytest.raises(ValueError, match='size bound'):
        fresh.predict([candidate()])
