"""Local impurity adapter tests; mocked scores are software fixtures only."""
from pathlib import Path
import json
import subprocess
import sys

import pytest

from synthesis_route_gym.adapters.impurity_local import LocalImpurityAdapter, normalize_impurity_result


def make_repo(tmp_path):
    root = tmp_path / 'repo'
    checkpoint = root / 'retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model'
    checkpoint.mkdir(parents=True)
    for name in ['config.json', 'tokenizer.json', 'tokenizer_config.json', 'model.safetensors']:
        (checkpoint / name).write_text('{}')
    (root / 'retrosynthesis/eval_impurity_t5.py').write_text('# software fixture')
    return root


def test_input_validation_precedes_inference(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('Invalid input must not launch inference')
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker', forbidden)
    adapter = LocalImpurityAdapter(repo_root=tmp_path)
    assert adapter.predict('invalid smiles', 'CCO')['status'] == 'error'
    assert adapter.predict('CCO', 'CCO', top_k=0)['status'] == 'error'
    assert adapter.predict('CCO', 'CCO', top_k=True)['status'] == 'error'


def test_missing_checkpoint_is_unavailable(tmp_path):
    assert LocalImpurityAdapter(repo_root=tmp_path).predict('CCO', 'CC=O')['status'] == 'unavailable'


def test_bad_device_and_timeout_are_rejected(tmp_path):
    root = make_repo(tmp_path)
    assert LocalImpurityAdapter(repo_root=root, device='other').predict('CCO', 'CC=O')['status'] == 'error'
    assert LocalImpurityAdapter(repo_root=root, timeout_seconds=0).predict('CCO', 'CC=O')['status'] == 'error'


def test_live_contract_preserves_proxy_training_and_no_truth(tmp_path, monkeypatch):
    root = make_repo(tmp_path)
    received = []
    def worker(python, payload, timeout):
        received.append(payload)
        return {'status': 'ok', 'beams': [['CCO', 'CC=O'], ['OCC', 'CC(=O)O']],
                'checkpoint_sha256': 'a' * 64, 'elapsed_seconds': 0.1, 'device': 'cpu'}
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker', worker)
    result = LocalImpurityAdapter(repo_root=root, python_executable=sys.executable).predict('CCOC(C)=O.O', 'CCO', top_k=2)
    assert received[0]['top_k'] == 2
    assert result['predicted_smiles'] == ['CC=O', 'CC(=O)O']
    assert result['training_evidence_kind'] == 'proxy_multi_product_annotations'
    assert result['evaluation_status'] == 'no_measured_labels'
    assert result['metrics'] is None
    assert result['model_inference_performed'] is True


def test_normalizer_deduplicates_excludes_major_and_reports_invalid():
    result = normalize_impurity_result({'status': 'ok', 'beams': [['CCO', 'OCC', 'bad'], ['CC=O']]}, 'CCO', 5)
    assert result['predicted_smiles'] == ['CC=O']
    assert result['discarded_invalid_candidates'] == 1
    assert result['excluded_major_product_count'] == 2


def test_failure_never_becomes_empty_success():
    result = normalize_impurity_result({'status': 'unavailable', 'diagnostic': 'checkpoint absent'}, 'CCO', 5)
    assert result['status'] == 'unavailable'
    assert result['model_inference_performed'] is False
    assert result['predicted_smiles'] == []


def test_malformed_output_is_error():
    assert normalize_impurity_result({'status': 'ok', 'beams': 'invalid'}, 'CCO', 5)['status'] == 'error'


def test_worker_missing_python_returns_unavailable():
    from synthesis_route_gym.adapters.impurity_local import run_impurity_worker
    result = run_impurity_worker('/does/not/exist', {}, 1)
    assert result['status'] == 'unavailable'


def test_worker_invalid_json_is_error(tmp_path):
    from synthesis_route_gym.adapters.impurity_local import run_impurity_worker
    executable = tmp_path / 'invalid_worker'
    executable.write_text('#!/bin/sh\nprintf not-json\n')
    executable.chmod(0o755)
    assert run_impurity_worker(str(executable), {}, 1)['status'] == 'error'


def test_worker_timeout_is_bounded(tmp_path):
    from synthesis_route_gym.adapters.impurity_local import run_impurity_worker
    executable = tmp_path / 'slow_worker'
    executable.write_text('#!/bin/sh\nsleep 5\n')
    executable.chmod(0o755)
    result = run_impurity_worker(str(executable), {}, 0.05)
    assert result['status'] == 'error'
    assert 'timed out' in result['diagnostic']


def test_adapter_manifest_is_content_bound_and_dataclass_serializable(tmp_path):
    from dataclasses import asdict, FrozenInstanceError
    root=make_repo(tmp_path);adapter=LocalImpurityAdapter(repo_root=root)
    assert Path(adapter.repo_root).is_absolute() and Path(adapter.python_executable).is_absolute()
    assert len(adapter.artifact_sha256)==64 and adapter.model_version.startswith('rebolt-impurity-t5-')
    assert len(adapter.asset_manifest)==5
    assert all(len(row[2])==64 for row in adapter.asset_manifest)
    assert asdict(adapter)['asset_manifest']==adapter.asset_manifest
    assert LocalImpurityAdapter(repo_root=root).artifact_sha256==adapter.artifact_sha256
    with pytest.raises(FrozenInstanceError):adapter.asset_manifest=()
    config=adapter.configuration;config['repo_root']='elsewhere'
    assert adapter.configuration['repo_root']==str(root.resolve())


@pytest.mark.parametrize('asset',['config.json','tokenizer.json','tokenizer_config.json','model.safetensors','source'])
def test_same_path_asset_change_refuses_old_adapter_and_changes_new_identity(tmp_path,monkeypatch,asset):
    from synthesis_route_gym.scientific_bindings import _callback_metadata
    root=make_repo(tmp_path);old=LocalImpurityAdapter(repo_root=root)
    path=root/'retrosynthesis/eval_impurity_t5.py' if asset=='source' else root/'retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model'/asset
    path.write_text('changed')
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker',lambda *a:pytest.fail('Changed assets must not infer'))
    result=old.predict('CCO','CC=O')
    assert result['status']=='error' and 'changed' in result['diagnostic']
    new=LocalImpurityAdapter(repo_root=root)
    assert old.artifact_sha256!=new.artifact_sha256
    assert _callback_metadata(old.predict)!=_callback_metadata(new.predict)


@pytest.mark.parametrize('change',['add_optional','remove','retarget_symlink'])
def test_asset_set_or_path_change_is_refused(tmp_path,monkeypatch,change):
    root=make_repo(tmp_path);checkpoint=root/'retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model'
    adapter=LocalImpurityAdapter(repo_root=root)
    if change=='add_optional':(checkpoint/'generation_config.json').write_text('{}')
    elif change=='remove':(checkpoint/'tokenizer.json').unlink()
    else:
        other=tmp_path/'other_config';other.write_text('{}')
        (checkpoint/'config.json').unlink();(checkpoint/'config.json').symlink_to(other)
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker',lambda *a:pytest.fail('Changed assets must not infer'))
    assert adapter.predict('CCO','CC=O')['status']=='error'


def test_missing_at_construction_stays_unavailable_after_files_appear(tmp_path,monkeypatch):
    root=tmp_path/'repo';adapter=LocalImpurityAdapter(repo_root=root)
    assert adapter.artifact_sha256 is None
    make_repo(tmp_path)
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker',lambda *a:pytest.fail('Unbound assets must not infer'))
    assert adapter.predict('CCO','CC=O')['status']=='unavailable'
    assert LocalImpurityAdapter(repo_root=root).artifact_sha256 is not None


def test_environment_defaults_are_resolved_once(tmp_path,monkeypatch):
    root=make_repo(tmp_path);other=tmp_path/'other';other.mkdir()
    monkeypatch.setenv('REBOLT_ROOT',str(root));monkeypatch.setenv('REBOLT_PYTHON',sys.executable)
    adapter=LocalImpurityAdapter()
    monkeypatch.setenv('REBOLT_ROOT',str(other));monkeypatch.setenv('REBOLT_PYTHON','/unavailable/python')
    calls=[]
    def worker(python,payload,timeout):
        calls.append((python,payload));return {'status':'ok','beams':[['CO']]}
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker',worker)
    assert adapter.predict('CCO','CC=O')['status']=='ok'
    assert calls[0][0]==str(Path(sys.executable).resolve())
    assert calls[0][1]['repo_root']==str(root.resolve())
    assert calls[0][1]['asset_manifest']==[list(row)for row in adapter.asset_manifest]


def test_python_path_change_is_refused(tmp_path,monkeypatch):
    root=make_repo(tmp_path);python=tmp_path/'python';python.write_text('initial')
    adapter=LocalImpurityAdapter(repo_root=root,python_executable=python)
    python.write_text('changed')
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker',lambda *a:pytest.fail('Changed interpreter must not start'))
    assert adapter.predict('CCO','CC=O')['status']=='error'


def test_mid_inference_asset_change_discards_output(tmp_path,monkeypatch):
    root=make_repo(tmp_path);adapter=LocalImpurityAdapter(repo_root=root)
    def worker(*args):
        (root/'retrosynthesis/eval_impurity_t5.py').write_text('changed during call')
        return {'status':'ok','beams':[['CO']]}
    monkeypatch.setattr('synthesis_route_gym.adapters.impurity_local.run_impurity_worker',worker)
    result=adapter.predict('CCO','CC=O')
    assert result['status']=='error' and result['model_inference_performed'] is False


def test_worker_checks_pinned_bytes_before_loading_model(tmp_path):
    from synthesis_route_gym.adapters.impurity_local import run_impurity_worker
    root=make_repo(tmp_path);adapter=LocalImpurityAdapter(repo_root=root)
    manifest=[list(row)for row in adapter.asset_manifest];manifest[0][2]='0'*64
    result=run_impurity_worker(sys.executable,{'asset_manifest':manifest},3)
    assert result['status']=='error' and 'artifact' in result['diagnostic'].lower()
