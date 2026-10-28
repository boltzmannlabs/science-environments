"""Bounded offline inference using the pod's existing direct impurity T5 model.

Its training labels originate from multi-product proxy annotations. Predictions
are hypotheses, not measured impurity occurrences or calibrated probabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time

from .common import canonical_smiles, response


_WORKER = r'''
import contextlib,hashlib,importlib.util,json,os,sys
from pathlib import Path

def sha256(path):
    digest=hashlib.sha256()
    with open(path,'rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()

def infer(request):
    manifest=request.get('asset_manifest')
    try:
        if not isinstance(manifest,list) or not manifest:
            raise ValueError('Missing pinned assets')
        for name,path,expected in manifest:
            if str(Path(path).resolve())!=path or sha256(path)!=expected:
                raise ValueError('Pinned asset differs')
    except (OSError,ValueError,TypeError,RuntimeError):
        return {'status':'error','diagnostic':'Pinned impurity artifacts changed or are unavailable.'}
    import torch
    from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
    torch.set_num_threads(1)
    torch.manual_seed(0)
    root=Path(request['repo_root'])
    source=Path(request['source_path'])
    spec=importlib.util.spec_from_file_location('pod_impurity_eval',source)
    legacy=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    checkpoint=Path(request['checkpoint'])
    tokenizer=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True)
    model=AutoModelForSeq2SeqLM.from_pretrained(checkpoint,local_files_only=True)
    device=request['device']
    if device=='cuda' and not torch.cuda.is_available():
        return {'status':'unavailable','diagnostic':'Requested CUDA device is unavailable.'}
    model=model.to(device)
    model.eval()
    input_text=f"REACTANT:{request['reactants']} REAGENT:{request['product']}"
    if len(tokenizer(input_text)['input_ids'])>256:
        return {'status':'error','diagnostic':'Input exceeds the existing model token limit; refusing silent truncation.'}
    legacy.NUM_BEAMS=2*((request['top_k']+1)//2)
    legacy.NUM_BEAM_GROUPS=2
    legacy.NUM_RETURN=request['top_k']
    legacy.MAX_GEN_LENGTH=96
    beams=legacy.predict_impurities(model,tokenizer,request['reactants'],request['product'],device)
    return {'status':'ok','beams':beams,'checkpoint_sha256':sha256(checkpoint/'model.safetensors'),
            'source_sha256':sha256(source),'source_method':'retrosynthesis/eval_impurity_t5.py:predict_impurities',
            'device':device,'usage':{'model_calls':1,'num_beams':legacy.NUM_BEAMS,
                                    'num_return_sequences':legacy.NUM_RETURN,'num_beam_groups':legacy.NUM_BEAM_GROUPS,'max_length':legacy.MAX_GEN_LENGTH},
            'torch_version':torch.__version__,'diagnostic':''}

try:
    request=json.loads(sys.stdin.read(100000))
    with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sys.stderr):
        result=infer(request)
except (ImportError,FileNotFoundError) as error:
    result={'status':'unavailable','diagnostic':'Existing impurity model dependency or artifact unavailable ('+type(error).__name__+').'}
except Exception as error:
    result={'status':'error','diagnostic':'Existing impurity model inference failed ('+type(error).__name__+').', 'error_detail':str(error)[:500]}
sys.stdout.write(json.dumps(result,allow_nan=False))
'''


def run_impurity_worker(python_executable: str, payload: dict, timeout_seconds: float) -> dict:
    """Run offline with a fixed argv and terminate the entire group on timeout."""
    started = time.monotonic()
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 600:
        return response('error', 'timeout_seconds must be positive and at most 600.')
    env = {key: value for key, value in os.environ.items() if key in {
        'PATH', 'HOME', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH', 'CUDA_VISIBLE_DEVICES'}}
    env.update({'PYTHONDONTWRITEBYTECODE': '1', 'HF_HUB_OFFLINE': '1',
                'TRANSFORMERS_OFFLINE': '1', 'HF_HUB_DISABLE_TELEMETRY': '1',
                'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'TOKENIZERS_PARALLELISM': 'false'})
    try:
        process = subprocess.Popen([str(python_executable), '-c', _WORKER], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env, start_new_session=True)
        try:
            stdout, _ = process.communicate(json.dumps(payload), timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            return response('error', 'Impurity inference timed out.', elapsed_seconds=time.monotonic() - started)
    except (OSError, ValueError):
        return response('unavailable', 'Configured impurity Python worker could not start.',
                        elapsed_seconds=time.monotonic() - started)
    if process.returncode != 0 or len(stdout) > 1_000_000:
        return response('error', 'Impurity worker failed or exceeded output limits.', elapsed_seconds=time.monotonic() - started)
    try:
        result = json.loads(stdout)
        if not isinstance(result, dict) or result.get('status') not in {'ok', 'error', 'unavailable'}:
            raise ValueError('Invalid response')
    except (ValueError, TypeError):
        return response('error', 'Impurity worker returned an invalid response.', elapsed_seconds=time.monotonic() - started)
    return {**result, 'elapsed_seconds': time.monotonic() - started}


def normalize_impurity_result(result: dict, product: str, top_k: int) -> dict:
    """Preserve raw beam fragments and exclude the known major product from hypotheses."""
    base = {'application': 'impurity_analysis', 'predicted_smiles': [],
            'evidence_kind': 'predicted_impurity_hypotheses',
            'training_evidence_kind': 'proxy_multi_product_annotations',
            'evaluation_status': 'no_measured_labels', 'metrics': None,
            'measured_impurities': None, 'model_inference_performed': result.get('status') == 'ok'}
    if result.get('status') != 'ok':
        return {**base, **result, 'model_inference_performed': False}
    beams = result.get('beams')
    if not isinstance(beams, list) or len(beams) > 100 or any(not isinstance(beam, list) or len(beam) > 100 for beam in beams):
        return {**base, 'status': 'error', 'diagnostic': 'Invalid impurity beam contract.',
                'model_inference_performed': False}
    major = canonical_smiles(product)
    candidates, invalid, major_count = [], 0, 0
    for beam in beams:
        for candidate in beam:
            try:
                normalized = canonical_smiles(candidate)
            except ValueError:
                invalid += 1
                continue
            if normalized == major:
                major_count += 1
            elif normalized not in candidates:
                candidates.append(normalized)
    return {**result, **base, 'predicted_smiles': candidates[:top_k],
            'discarded_invalid_candidates': invalid, 'excluded_major_product_count': major_count,
            'score_kind': 'beam_order_only', 'scientific_review_status': 'pending',
            'limitations': ['Existing model learned proxy multi-product labels, not validated impurity measurements.',
                           'Beam alternatives and fragments are impurity hypotheses requiring chemical review.',
                           'No calibrated probability, impurity concentration, precision, or recall is available.',
                           'Beam outputs can be chemically implausible; no reaction or atom-balance acceptance has been applied.',
                           'The reused evaluator removes invalid raw strings before returning beam fragments.']}


def _file_digest(path):
    try:
        with Path(path).open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    except OSError:
        return None


def _asset_manifest(root):
    """Include optional checkpoint assets too, so additions cannot change loading."""
    checkpoint = root / 'retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model'
    required = {'config.json', 'tokenizer.json', 'tokenizer_config.json', 'model.safetensors'}
    try:
        names = required | {str(path.relative_to(checkpoint)) for path in checkpoint.rglob('*') if not path.is_dir()}
    except OSError:
        names = required | {'__unreadable_directory__'}
    paths = [(f'checkpoint/{name}', checkpoint / name) for name in sorted(names)]
    paths += [('source/eval_impurity_t5.py', root / 'retrosynthesis/eval_impurity_t5.py')]
    records = []
    for name, path in paths:
        try:
            resolved = str(path.resolve())
        except (OSError, RuntimeError):
            resolved = str(path.absolute())
        records.append((name, resolved, _file_digest(path)))
    return tuple(records)


@dataclass(frozen=True)
class LocalImpurityAdapter:
    repo_root: Path | str | None = None
    python_executable: Path | str | None = None
    timeout_seconds: float = 120.0
    device: str = 'cpu'
    checkpoint_path: str = field(init=False)
    source_path: str = field(init=False)
    asset_manifest: tuple[tuple[str, str, str | None], ...] = field(init=False)
    artifact_sha256: str | None = field(init=False)
    model_version: str = field(init=False)
    python_sha256: str | None = field(init=False)

    def __post_init__(self):
        root = Path(self.repo_root or os.environ.get('REBOLT_ROOT') or Path(__file__).parents[4]).resolve()
        python = str(self.python_executable or os.environ.get('REBOLT_PYTHON') or sys.executable)
        python = str(Path(shutil.which(python) or python).resolve())
        manifest = _asset_manifest(root)
        content = [(name, digest) for name, _, digest in manifest]
        artifact = (hashlib.sha256(json.dumps(content, separators=(',', ':')).encode()).hexdigest()
                    if all(row[2] is not None for row in manifest) else None)
        values = {'repo_root': str(root), 'python_executable': python, 'asset_manifest': manifest,
            'artifact_sha256': artifact, 'python_sha256': _file_digest(python),
            'checkpoint_path': str((root / 'retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model').resolve()),
            'source_path': str((root / 'retrosynthesis/eval_impurity_t5.py').resolve()),
            'model_version': f'rebolt-impurity-t5-{artifact[:16]}' if artifact else 'unavailable'}
        for name, value in values.items():
            object.__setattr__(self, name, value)

    @property
    def configuration(self):
        return {'repo_root': self.repo_root, 'python_executable': self.python_executable,
                'checkpoint_path': self.checkpoint_path, 'source_path': self.source_path,
                'asset_manifest': [list(row) for row in self.asset_manifest],
                'python_sha256': self.python_sha256, 'device': self.device,
                'timeout_seconds': self.timeout_seconds}

    def _unchanged(self):
        return (_asset_manifest(Path(self.repo_root)) == self.asset_manifest
                and _file_digest(self.python_executable) == self.python_sha256)

    def predict(self, reactants: str, product: str, top_k: int = 5) -> dict:
        try:
            reactants, product = canonical_smiles(reactants), canonical_smiles(product)
            if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= 10:
                raise ValueError('top_k must be an integer between 1 and 10.')
            if self.device not in {'cpu', 'cuda'}:
                raise ValueError('device must be cpu or cuda.')
            if isinstance(self.timeout_seconds, bool) or not isinstance(self.timeout_seconds, (int, float)) or not math.isfinite(self.timeout_seconds) or not 0 < self.timeout_seconds <= 600:
                raise ValueError('timeout_seconds must be positive and at most 600.')
        except ValueError as error:
            return normalize_impurity_result(response('error', str(error)), '', 0)
        if self.artifact_sha256 is None:
            return normalize_impurity_result(response('unavailable', 'Impurity assets were absent or unreadable at initialization; create a new host binding after setup.'), product, top_k)
        if not self._unchanged():
            return normalize_impurity_result(response('error', 'Pinned impurity assets or interpreter changed; refusing inference.'), product, top_k)
        payload = {'repo_root': self.repo_root, 'checkpoint': self.checkpoint_path,
                   'source_path': self.source_path, 'artifact_sha256': self.artifact_sha256,
                   'asset_manifest': [list(row) for row in self.asset_manifest],
                   'reactants': reactants, 'product': product, 'top_k': top_k, 'device': self.device}
        result = run_impurity_worker(self.python_executable, payload, self.timeout_seconds)
        if not self._unchanged():
            return normalize_impurity_result(response('error', 'Pinned impurity assets or interpreter changed during inference; result discarded.'), product, top_k)
        return {**normalize_impurity_result(result, product, top_k),
                'input': {'reactants': reactants, 'product': product},
                'model_name': 'existing_rebolt_direct_impurity_t5',
                'model_version': self.model_version, 'artifact_sha256': self.artifact_sha256}
