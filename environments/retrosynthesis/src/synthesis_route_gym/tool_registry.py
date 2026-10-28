"""Host-owned scientific capability registry, with uniform public result envelopes."""
from dataclasses import dataclass
import hashlib
import json
import math
import re
import time
from types import MappingProxyType
from typing import Callable
from .tool_contracts import CONTRACT_VERSION, INPUT_MODELS, OUTPUT_MODELS, ToolEnvelope, envelope_schema
from .tool_normalization import normalize_output

ALIASES = MappingProxyType({'retrosynthesis':'expand','conditions':'predict_conditions',
    'source_retrieval':'retrieve_sources','forward_consistency':'forward_check',
    'condition_observation':'observe_condition','impurity_hypotheses':'predict_impurities',
    'process_comparison':'compare_process','biocatalytic_retrieval':'retrieve_biocatalysis'})
AUTHORITIES = {'retrieve_sources':'source_retrieval','retrieve_biocatalysis':'source_retrieval',
               'observe_condition':'measured_replay','compare_process':'estimate'}
KINDS = {'expand':'predicted','predict_conditions':'predicted','retrieve_sources':'retrieved_source_claims',
 'score_cn_conditions':'predicted_screen_hit',
 'predict_reaction_yield':'predicted_yield',
 'forward_check':'predicted_consistency','observe_condition':'measured_dataset_replay',
 'predict_impurities':'predicted_impurity_hypotheses','compare_process':'supplied_estimate',
 'retrieve_biocatalysis':'curated_transformation_retrieval'}
SCOPES = {'expand':'Predicted precursor candidates, not evidence of feasible synthesis.',
 'score_cn_conditions':'Source-scoped C-N screening-hit scores with explicit abstention; not yields or synthesis feasibility.',
 'predict_reaction_yield':'Uncalibrated reaction yield predictions with abstention; not measured yields or experimental feasibility.',
 'predict_conditions':'Host-declared condition-model domain; no general reaction feasibility claim.',
 'retrieve_sources':'Frozen public source claims; retrieval does not authenticate experimental support.',
 'forward_check':'Predicted product consistency; omitted coproduct balance remains unknown.',
 'observe_condition':'One allowed candidate from host-measured replay; no new experiment.',
 'predict_impurities':'Predicted impurity hypotheses; no concentration or measured occurrence claim.',
 'compare_process':'Comparable supplied cost estimates only; no manufacturing savings claim.',
 'retrieve_biocatalysis':'Documented small-molecule transformations; no inferred enzyme activity.'}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _hash_or_none(value):
    if value is not None and (not isinstance(value,str) or not re.fullmatch('[a-f0-9]{64}',value)):
        raise ValueError('Snapshot identity must be a lowercase SHA-256 digest')
    return value


@dataclass(frozen=True)
class ToolBinding:
    callback: Callable[[dict],dict]
    version: str
    configuration_version: str = '1'
    model_version: str = 'none'
    artifact_sha256: str | None = None
    authority: str = 'prediction'
    timeout_seconds: float = 60

    def __post_init__(self):
        if not callable(self.callback):
            raise ValueError('Tool callback must be callable')
        for field in ('version','configuration_version','model_version'):
            value=getattr(self,field)
            if not isinstance(value,str) or not value.strip() or len(value)>200:
                raise ValueError('Host must declare bounded nonempty tool/version identities')
        _hash_or_none(self.artifact_sha256)
        if self.authority not in {'prediction','source_retrieval','measured_replay','estimate'}:
            raise ValueError('Unknown host evidence authority')
        timeout=self.timeout_seconds
        if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not math.isfinite(timeout) or not 0<timeout<=3600:
            raise ValueError('Tool timeout must be finite and in (0,3600]')

    def identity(self):
        return {k:getattr(self,k) for k in ('version','configuration_version','model_version',
            'artifact_sha256','authority','timeout_seconds')}


class ToolRegistry:
    """Immutable configuration; host environment owns deadlines and durable usage.

    Callables are trusted host injections, not model-controlled imports. Declared
    artifact digests identify configuration; no claim of model execution is made.
    """
    def __init__(self, bindings=None, *, stock_sha256=None, evidence_sha256=None):
        bindings=dict(bindings or {})
        for name,binding in bindings.items():
            if name not in INPUT_MODELS or not isinstance(binding,ToolBinding):
                raise ValueError('Use canonical names and explicit ToolBinding records')
            if binding.authority != AUTHORITIES.get(name,'prediction'):
                raise ValueError('Binding does not have the required host evidence authority')
        self._bindings=MappingProxyType(bindings)
        self._stock_sha256=_hash_or_none(stock_sha256)
        self._evidence_sha256=_hash_or_none(evidence_sha256)
        source_binding=bindings.get('retrieve_sources')
        if (source_binding is not None and source_binding.artifact_sha256 is not None
                and self._evidence_sha256 is not None
                and source_binding.artifact_sha256 != self._evidence_sha256):
            raise ValueError('Conflicting source corpus snapshot identities')
        self._identity={'schema_version':CONTRACT_VERSION,
            'bindings':{key:value.identity() for key,value in sorted(bindings.items())},
            'stock_sha256':self._stock_sha256,'evidence_sha256':self._evidence_sha256}
        self.fingerprint=_digest(self._identity)

    @staticmethod
    def canonical_name(name):
        if not isinstance(name,str):
            raise ValueError('Capability name must be a string')
        canonical=ALIASES.get(name,name)
        if canonical not in INPUT_MODELS:
            raise ValueError('Unknown capability')
        return canonical

    def available(self,name):
        return self.canonical_name(name) in self._bindings

    def failure(self,name,code,message=None,*,status='error',backend_calls=0):
        name=self.canonical_name(name)
        if (not isinstance(code,str) or not re.fullmatch('[a-z][a-z0-9_]{0,79}',code)
                or status not in {'error','unavailable'} or type(backend_calls) is not int or not 0<=backend_calls<=1):
            raise ValueError('Invalid host failure contract')
        result=self._response(name,status,time.monotonic(),code=code,calls=backend_calls)
        if message is not None:
            if not isinstance(message,str) or not 1<=len(message)<=500:
                raise ValueError('Host failure message must be bounded text')
            result={**result,'error':{**result['error'],'message':message}}
        return result

    def validate_request(self,name,arguments):
        canonical=self.canonical_name(name)
        if not isinstance(arguments,dict):
            raise ValueError('Tool arguments must be an object')
        return INPUT_MODELS[canonical].model_validate(arguments).model_dump(mode='json',by_alias=True)

    def cache_identity(self,name,arguments):
        canonical=self.canonical_name(name)
        return _digest({'registry':self.fingerprint,'capability':canonical,
                        'arguments':self.validate_request(canonical,arguments)})

    def describe(self):
        return [{'name':name,'aliases':[a for a,c in ALIASES.items() if c==name],
            'version':CONTRACT_VERSION,'backend_version':self._bindings[name].version if name in self._bindings else None,
            'owner':'synthesis-route-gym environment/tool maintainer','scope':SCOPES[name],
            'evidence_kind':KINDS[name], 'availability':'configured' if name in self._bindings else 'not_configured',
            'execution_verified':False,'timeout_seconds':self._bindings[name].timeout_seconds if name in self._bindings else 60,
            'timeout_enforcement':'host_environment', 'accounting_unit':'condition_observation' if name=='observe_condition' else 'scientific_tool_call',
            'input_schema':INPUT_MODELS[name].model_json_schema(by_alias=True),
            'output_schema':OUTPUT_MODELS[name].model_json_schema(),
            'output_schema_scope':'data','result_schema':envelope_schema(name),
            'registry_fingerprint':self.fingerprint}
            for name in INPUT_MODELS]

    def _response(self,name,status,started,*,data=None,code=None,calls=0):
        binding=self._bindings.get(name)
        provenance={'registry_fingerprint':self.fingerprint,'stock_sha256':self._stock_sha256,
            'evidence_sha256':self._evidence_sha256,'binding':binding.identity() if binding else None,
            'version_status':'host_declared_artifact_digest' if binding and binding.artifact_sha256 else 'declared_not_artifact_verified'}
        messages={'unknown_capability':'Capability is not registered.','invalid_request':'Input does not match the capability contract.',
            'not_configured':'No host backend is configured.','backend_unavailable':'Configured backend is unavailable.',
            'backend_failed':'Configured backend failed.','invalid_result':'Backend result does not match the scientific contract.'}
        return ToolEnvelope.model_validate({'schema_version':CONTRACT_VERSION,'capability':name,'status':status,'data':data,
            'error':{'code':code,'message':messages.get(code, 'Scientific operation was not completed by the host.')} if code else None,'provenance':provenance,
            'usage':{'backend_calls':calls,'request_units':1,'elapsed_seconds':max(0,time.monotonic()-started),
                     'condition_observations':int(name=='observe_condition' and calls>0)},
            'evidence_kind':KINDS.get(name,'unavailable')}).model_dump(mode='json')

    def invoke(self,name,arguments):
        started=time.monotonic()
        try:
            name=self.canonical_name(name)
        except ValueError:
            return self._response('unknown','error',started,code='unknown_capability')
        try:
            args=self.validate_request(name,arguments)
        except (ValueError,TypeError,RecursionError):
            return self._response(name,'error',started,code='invalid_request')
        binding=self._bindings.get(name)
        if binding is None:
            return self._response(name,'unavailable',started,code='not_configured')
        try:
            raw=binding.callback(json.loads(json.dumps(args)))
        except Exception:
            return self._response(name,'error',started,code='backend_failed',calls=1)
        try:
            if not isinstance(raw,dict) or len(json.dumps(raw,allow_nan=False))>8_000_000:
                raise ValueError('Invalid result object')
            status=raw.get('status','ok')
            if status in {'error','unavailable'}:
                return self._response(name,status,started,code='backend_unavailable' if status=='unavailable' else 'backend_failed',calls=1)
            if status!='ok':
                raise ValueError('Invalid backend status')
            data=normalize_output(name,raw,args,binding)
            if (name=='retrieve_sources' and self._evidence_sha256 is not None
                    and data['corpus_sha256'] != self._evidence_sha256):
                raise ValueError('Retrieved corpus differs from registered evidence snapshot')
        except (ValueError,TypeError,KeyError,AttributeError,RecursionError):
            return self._response(name,'error',started,code='invalid_result',calls=1)
        return self._response(name,'ok',started,data=data,calls=1)
