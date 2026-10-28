"""Replaceable, artifact-pinned local yield prediction without outcome-label inputs."""
from collections.abc import Mapping
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Protocol
from urllib.parse import urlsplit

from .chemistry import canonical_smiles

SCHEMA = 'srg-public-yield-model-v1'
FILES = frozenset({'config.json', 'tokenizer.json', 'tokenizer_config.json',
                   'special_tokens_map.json', 'model.safetensors'})
DOMAIN = 'ORD pretrained yield model; transfer domain and calibration not established'
MAX_JSON_BYTES = 2_000_000
WORKER = Path(__file__).with_name('reactiont5_worker.py')


class ReactionYieldPredictor(Protocol):
    """Replacement models implement the same public chemical input/output contract."""
    @property
    def artifact(self) -> dict: ...
    @property
    def metadata(self) -> dict: ...
    @property
    def configuration(self) -> dict: ...
    @property
    def timeout_seconds(self) -> float: ...
    def predict(self, candidates: list[dict]) -> list[dict]: ...


def _copy(value):
    return json.loads(json.dumps(value, allow_nan=False))


def _digest(path):
    hasher = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def _smiles(value):
    if not isinstance(value, str) or not 1 <= len(value) <= 10000:
        raise ValueError('Expected bounded molecular SMILES')
    return canonical_smiles(value)


def format_reaction(candidate):
    """Canonicalize complete molecular participants without erasing salts or stereo."""
    if not isinstance(candidate, Mapping) or set(candidate) != {'id','reactants','reagents','product'}:
        raise ValueError('Reaction input permits only id, reactants, reagents and product')
    if not isinstance(candidate['id'], str) or not 1 <= len(candidate['id'].strip()) <= 200:
        raise ValueError('Reaction candidate requires a bounded identifier')
    for role, minimum in (('reactants',1), ('reagents',0)):
        values = candidate[role]
        if not isinstance(values, (list,tuple)) or not minimum <= len(values) <= 100:
            raise ValueError('Reaction participant lists exceed allowed bounds')
    reactants = '.'.join(_smiles(value) for value in candidate['reactants'])
    reagents = '.'.join(_smiles(value) for value in candidate['reagents'])
    return f'REACTANT:{reactants}REAGENT:{reagents}PRODUCT:{_smiles(candidate["product"])}'


def _manifest(raw, base):
    required = {'schema_version','model_dir','python_executable','files','model_version',
                'model_revision','source_url','license'}
    optional = {'device','max_tokens','timeout_seconds','num_threads','runtime_versions'}
    if not isinstance(raw,dict) or not required <= set(raw) or set(raw)-required-optional:
        raise ValueError('Invalid public yield manifest fields')
    if raw['schema_version'] != SCHEMA:
        raise ValueError('Unsupported public yield manifest version')
    for key in ('model_version','license'):
        if not isinstance(raw[key],str) or not 1 <= len(raw[key].strip()) <= 200:
            raise ValueError('Invalid model metadata')
    if not isinstance(raw['model_revision'],str) or not re.fullmatch('[a-f0-9]{40}',raw['model_revision']):
        raise ValueError('Pin a full model revision digest')
    source = urlsplit(raw['source_url']) if isinstance(raw['source_url'],str) else None
    if not source or source.scheme != 'https' or not source.netloc or source.username or source.password:
        raise ValueError('Model source requires public HTTPS identity')
    files = raw['files']
    if (not isinstance(files,dict) or set(files) != FILES
            or any(not isinstance(v,str) or not re.fullmatch('[a-f0-9]{64}',v) for v in files.values())):
        raise ValueError('Pin exact required model asset digests')
    resolved = {}
    for field in ('model_dir','python_executable'):
        if not isinstance(raw[field],str) or not raw[field]:
            raise ValueError('Model and interpreter paths are required')
        value = Path(raw[field]).expanduser()
        resolved[field] = str((base / value).resolve()) if field == 'model_dir' else os.path.abspath(base / value)
    if not Path(resolved['model_dir']).is_dir() or not os.access(resolved['python_executable'], os.X_OK):
        raise ValueError('Local model directory and executable interpreter must exist')
    result = {**raw, **resolved, 'device':raw.get('device','cpu'),
              'max_tokens':raw.get('max_tokens',512), 'timeout_seconds':raw.get('timeout_seconds',300),
              'num_threads':raw.get('num_threads',4), 'runtime_versions':raw.get('runtime_versions',{})}
    if not isinstance(result['device'],str) or not re.fullmatch('cpu|cuda(:[0-9]+)?', result['device']):
        raise ValueError('Invalid inference device')
    for key,maximum in (('max_tokens',512), ('num_threads',32)):
        if type(result[key]) is not int or not 1 <= result[key] <= maximum:
            raise ValueError('Invalid bounded inference configuration')
    timeout = result['timeout_seconds']
    if type(timeout) not in (int,float) or not math.isfinite(timeout) or not 0 < timeout <= 3600:
        raise ValueError('Invalid model timeout')
    versions = result['runtime_versions']
    if (not isinstance(versions,dict) or set(versions)-{'torch','transformers','tokenizers','safetensors'}
            or any(not isinstance(v,str) or not 1 <= len(v) <= 100 for v in versions.values())):
        raise ValueError('Invalid runtime version pins')
    return _copy(result)


def _result(row, expected_id, version):
    if not isinstance(row,dict) or set(row) != {'id','raw_yield_percent','reason'} or row['id'] != expected_id:
        raise ValueError('Yield worker changed candidate identity or result fields')
    raw, reason = row['raw_yield_percent'], row['reason']
    allowed = {'token_limit_exceeded','unknown_token','nonfinite_prediction'}
    if raw is None:
        if reason not in allowed:
            raise ValueError('Yield worker omitted score without a known abstention reason')
    elif type(raw) not in (int,float) or not math.isfinite(raw) or reason is not None:
        raise ValueError('Yield worker returned invalid numeric output')
    elif not 0 <= raw <= 100:
        reason = 'prediction_out_of_range'
    return {'id':expected_id,'status':'scored' if reason is None else 'abstained',
            'predicted_yield_percent':float(raw) if reason is None else None,
            'raw_yield_percent':float(raw) if raw is not None else None,'reason':reason,
            'model_version':version,'domain':DOMAIN,'uncertainty_kind':'not_calibrated',
            'evidence_status':'predicted','endpoint_scope':'model_yield_not_experimental_feasibility'}


class ReactionT5YieldPredictor:
    """Local subprocess adapter. Loading never downloads or executes model-repository code."""
    def __init__(self, manifest):
        manifest = _manifest(manifest, Path.cwd())
        self._artifact = _copy(manifest)
        self._configuration = {'manifest':_copy(manifest), 'worker_sha256':_digest(WORKER),
            'adapter_sha256':_digest(__file__), 'python_sha256':_digest(manifest['python_executable'])}
        self._verify()

    @classmethod
    def from_manifest(cls, path):
        path = Path(path).resolve()
        if path.stat().st_size > 100000:
            raise ValueError('Public yield manifest exceeds size bound')
        return cls(_manifest(json.loads(path.read_text()), path.parent))

    @property
    def artifact(self):
        return _copy(self._artifact)

    @property
    def metadata(self):
        return {key:self._artifact[key] for key in ('model_version','model_revision','source_url','license')}

    @property
    def configuration(self):
        return _copy(self._configuration)

    @property
    def timeout_seconds(self):
        return self._artifact['timeout_seconds']

    def _verify(self):
        for name, expected in self._artifact['files'].items():
            if _digest(Path(self._artifact['model_dir']) / name) != expected:
                raise ValueError('Public yield model asset digest changed')
        for path, key in ((WORKER,'worker_sha256'), (__file__,'adapter_sha256'),
                          (self._artifact['python_executable'],'python_sha256')):
            if _digest(path) != self._configuration[key]:
                raise ValueError('Public yield runtime digest changed')

    def predict(self, candidates):
        if not isinstance(candidates,(list,tuple)) or not 1 <= len(candidates) <= 100:
            raise ValueError('Yield prediction requires 1 to 100 candidates')
        rows = [{'text':format_reaction(row), 'id':row['id']} for row in candidates]
        if len({row['id'] for row in rows}) != len(rows):
            raise ValueError('Yield candidate identifiers must be unique')
        payload = json.dumps({'manifest':self._artifact, 'rows':rows}, allow_nan=False).encode()
        if len(payload) > MAX_JSON_BYTES:
            raise ValueError('Yield prediction input exceeds serialized size bound')
        self._verify()
        output = self._run(payload)
        if not isinstance(output,dict) or set(output) != {'predictions'} or not isinstance(output['predictions'],list):
            raise ValueError('Invalid yield worker result')
        if len(output['predictions']) != len(rows):
            raise ValueError('Yield worker returned an incomplete candidate set')
        return [_result(value,row['id'],self.metadata['model_version'])
                for row,value in zip(rows, output['predictions'])]

    def _run(self, payload):
        environment = {**os.environ, 'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1',
                       'TOKENIZERS_PARALLELISM':'false'}
        command = [self._artifact['python_executable'],'-I',str(WORKER)]
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            try:
                result = subprocess.run(command, input=payload, stdout=stdout, stderr=stderr,
                                        timeout=self.timeout_seconds, env=environment, check=False)
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError('Local yield predictor exceeded its time budget') from exc
            if result.returncode:
                raise RuntimeError('Local yield predictor failed; verify pinned runtime and model assets')
            stdout.seek(0)
            data = stdout.read(MAX_JSON_BYTES+1)
        if len(data) > MAX_JSON_BYTES:
            raise ValueError('Yield worker result exceeds size bound')
        try:
            return json.loads(data)
        except (ValueError,UnicodeError) as exc:
            raise ValueError('Yield worker returned invalid JSON') from exc
