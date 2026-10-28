"""Host-controlled wrappers; no imported launcher or evaluator reports."""
from dataclasses import asdict, is_dataclass
from datetime import datetime
import hashlib
import inspect
import json
import math
import re
from pathlib import Path
from .chemistry import canonical_smiles
from .ranking import COMPONENTS
from .schemas import RouteCandidate
from .validation import assess_route


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _plain(value):
    def default(item):
        if isinstance(item, Path):
            return str(item)
        raise TypeError('Host configuration must be JSON serializable')
    return json.loads(json.dumps(value, default=default, allow_nan=False))


def _callback_metadata(callback):
    """Pin inspectable code/configuration; external weights remain explicitly unknown."""
    obj = getattr(callback, '__self__', None)
    try:
        source = inspect.getsourcefile(callback)
    except (TypeError, OSError):
        source = None
    source_hash = hashlib.sha256(Path(source).read_bytes()).hexdigest() if source and Path(source).is_file() else None
    return {'callable': f'{getattr(callback, "__module__", "unknown")}:{getattr(callback, "__qualname__", type(callback).__name__)}',
            'source_sha256': source_hash,
            'configuration': _plain(asdict(obj)) if obj is not None and is_dataclass(obj) else None,
            'external_artifacts': 'unknown_unless_host_pinned'}


def _binding(callback, name, versions, timeout, *, authority='prediction', artifact=None, model_version='unknown', config=None):
    from .tool_registry import ToolBinding
    metadata = dict(versions.get(name, {}))
    allowed = {'version', 'configuration_version', 'model_version', 'artifact_sha256', 'timeout_seconds'}
    if set(metadata) - allowed:
        raise ValueError('Unknown host backend version field')
    return ToolBinding(callback=callback, version=metadata.get('version', 'srg-wrapper-v1'),
        configuration_version=metadata.get('configuration_version', _hash(config or {})),
        model_version=metadata.get('model_version', model_version),
        artifact_sha256=metadata.get('artifact_sha256', artifact), authority=authority,
        timeout_seconds=metadata.get('timeout_seconds', timeout))


def _condition_callback(study):
    from .portfolio_conditions import FiniteConditionStudy
    if not isinstance(study, FiniteConditionStudy) or not study.source_url or not study.source_locator:
        raise ValueError('A sourced host FiniteConditionStudy is required')
    if ((study.budget is not None and (type(study.budget) is not int or study.budget < 1))
            or not re.fullmatch('[a-f0-9]{64}',study.dataset_sha256)
            or not 1 <= len(study._records) <= 100000):
        raise ValueError('Invalid bounded condition study metadata')
    if len({row.candidate_id for row in study._records}) != len(study._records):
        raise ValueError('Condition study candidate IDs must be unique')
    if (len(set(study.observed_ids)) != len(study.observed_ids)
            or set(study.observed_ids) - {row.candidate_id for row in study._records}
            or (study.budget is not None and len(study.observed_ids) > study.budget)):
        raise ValueError('Invalid initial observation identities')
    for row in study._records:
        if (not 1 <= len(row.conditions) <= 100
                or len({key for key,_ in row.conditions}) != len(row.conditions)):
            raise ValueError('Invalid or duplicate condition factors')
        if type(row.yield_percent) not in {int,float} or not math.isfinite(row.yield_percent) or not 0 <= row.yield_percent <= 100:
            raise ValueError('Condition study contains an invalid measured outcome')
    fingerprint = _hash(asdict(study))
    def observe(args):
        key = args['candidate_id']
        if key in study.observed_ids:
            raise ValueError('Candidate belongs to initial observations')
        row = next((row for row in study._records if row.candidate_id == key), None)
        if row is None:
            raise ValueError('Unknown registered observation candidate')
        return {'status': 'ok', 'candidate_id': key, 'conditions': dict(row.conditions),
                'yield_percent': row.yield_percent, 'source_record_id': f'study:{study.dataset_sha256}:{_hash(key)[:20]}',
                'dataset_sha256': study.dataset_sha256}
    return observe, fingerprint


def _valid_quote_date(value):
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def _process_callback(task, route_lookup, inventory_hash, process_basis):
    basis = dict(process_basis or {})
    if set(basis) - {'purity_basis', 'exclusions'}:
        raise ValueError('Unknown process comparison basis field')
    purity, exclusions = basis.get('purity_basis'), basis.get('exclusions')
    if purity is not None and (not isinstance(purity, str) or not purity.strip()):
        raise ValueError('Invalid process purity basis')
    if exclusions is not None and (not isinstance(exclusions, (list, tuple)) or any(not isinstance(x, str) or not x for x in exclusions)):
        raise ValueError('Invalid process cost exclusions')
    def compare(args):
        if args.get('target_amount_mmol') is not None and args['target_amount_mmol'] != task.target_amount_mmol:
            raise ValueError('Cannot silently rescale supplied route amounts')
        rows = []
        for ident in args['route_ids']:
            raw = route_lookup(ident)
            route = raw if isinstance(raw, RouteCandidate) else RouteCandidate.model_validate(raw)
            if route.route_id != ident or route.target != task.target:
                raise ValueError('Process route differs from registered identity')
            checked = assess_route(task, route)
            feeds = {use.smiles for step in route.steps for use in step.reactants + step.reagents}
            stock = [item for item in task.inventory if item.smiles in feeds]
            quoted = bool(stock) and all(item.source and _valid_quote_date(item.quoted_at) for item in stock)
            comparable = (checked.graph_valid and checked.inventory_complete and checked.constraint_compliant
                and checked.quantity_status == 'complete' and task.target_amount_mmol is not None
                and checked.cost.total is not None and quoted and purity is not None and exclusions is not None)
            rows.append({'route_id': ident, 'target': route.target, 'steps': len(route.steps),
                'material_cost': checked.cost.total if comparable else None,
                'cost_currency': checked.cost.currency, 'scale_mmol': task.target_amount_mmol,
                'cost_basis': 'declared_starting_materials_and_reagents' if comparable else 'incomplete_basis',
                'cost_source_id': _hash([item.model_dump(mode='json') for item in stock]) if quoted else None,
                'quoted_at': min((item.quoted_at for item in stock), default=None) if quoted else None,
                'price_status': 'supplied_estimate' if comparable else 'unknown',
                'inventory_sha256': inventory_hash, 'purity_basis': purity,
                'exclusions': list(exclusions) if exclusions is not None else []})
        return {'status':'ok', 'routes':rows}
    return compare


def _bio_callback(task, raw_records):
    from .portfolio import _bio_record
    def preserve_participants(raw):
        copied = _plain(raw)
        checked = _bio_record(copied)
        return {**checked, 'reactants':[canonical_smiles(value) for value in copied['reactants']],
                'products':[canonical_smiles(value) for value in copied['products']]}
    records = tuple(preserve_participants(row) for row in raw_records)
    if len({row['record_id'] for row in records}) != len(records):
        raise ValueError('Duplicate biocatalytic record IDs')
    fingerprint = _hash(records)
    def retrieve(args):
        target = canonical_smiles(args['target_smiles'])
        inventory = {item.smiles for item in task.inventory if item.available_mmol != 0}
        candidates = []
        for row in records:
            if target not in row['products']:
                continue
            cofactors = [canonical_smiles(value) for value in row.get('cofactors', [])]
            candidates.append({'record_id':row['record_id'], 'enzyme_name':row['enzyme_name'],
                'source_url':row['source_url'], 'source_locator':row['source_locator'],
                'reactants':row['reactants'], 'products':row['products'], 'cofactors':cofactors,
                'match_kind':'exact_product', 'missing_reactants':sorted(set(row['reactants'] + cofactors) - inventory),
                'enzyme_availability':'unknown','conditions_status':'unknown','experimental_yield':None,
                'claims_activity':False})
        return {'status':'ok', 'candidates':candidates[:args.get('limit',10)]}
    return retrieve, fingerprint


def build_default_registry(task, *, expand=None, condition_ranker=None, route_lookup=None,
                           evidence_corpus=None, condition_study=None, impurity=None,
                           biocatalytic_records=None, forward=None, backend_versions=None,
                           timeout_seconds=60, process_basis=None, source_access_mode=None,
                           cn_condition_model=None, reaction_yield_predictor=None):
    """Bind existing host tools; the environment owns durable observation budgets."""
    from .tool_registry import ToolRegistry
    versions = _plain(backend_versions or {})
    allowed_versions = {'expand', 'predict_conditions', 'forward_check', 'predict_impurities',
                        'retrieve_sources', 'observe_condition', 'compare_process', 'retrieve_biocatalysis',
                        'score_cn_conditions', 'predict_reaction_yield'}
    if not isinstance(versions, dict) or set(versions) - allowed_versions:
        raise ValueError('Unknown host backend capability version')
    inventory_hash = _hash([item.model_dump(mode='json') for item in task.inventory])
    mode = source_access_mode or (evidence_corpus.public_manifest()['access_mode'] if evidence_corpus is not None else 'closed_information')
    if mode not in {'closed_information', 'evidence_retrieval'}:
        raise ValueError('Unknown source access mode')
    if evidence_corpus is not None and mode != evidence_corpus.public_manifest()['access_mode']:
        raise ValueError('Source corpus and global source-access modes differ')
    bindings = {}
    if expand is not None:
        bindings['expand'] = _binding(lambda args: expand(args['smiles'], args.get('top_k',10)),
            'expand', versions, timeout_seconds, config=_callback_metadata(expand))
    if condition_ranker is not None:
        def predict(args):
            candidates = args['candidates']
            rows = [{key: row[key] for key in COMPONENTS} for row in candidates]
            results = condition_ranker.predict(rows)
            if len(results) != len(candidates):
                raise ValueError('Predictor returned an incomplete candidate set')
            return {'status':'ok','predictions':[{**row,'id':candidate['id']} for candidate,row in zip(candidates,results)]}
        artifact = getattr(condition_ranker, '_artifact', None)
        bindings['predict_conditions'] = _binding(predict, 'predict_conditions', versions, timeout_seconds,
            artifact=_hash(artifact) if artifact is not None else None,
            model_version=getattr(condition_ranker, 'metadata', {}).get('model_version','unknown'),
            config=_callback_metadata(condition_ranker.predict))
    if forward is not None:
        bindings['forward_check'] = _binding(forward, 'forward_check', versions, timeout_seconds,
                                             config=_callback_metadata(forward))
    if cn_condition_model is not None:
        def score_cn(args):
            from .cn_model import CN_ROLES
            candidates = args['candidates']
            rows = [{key: row[key] for key in CN_ROLES} for row in candidates]
            results = cn_condition_model.predict(rows)
            if len(results) != len(candidates):
                raise ValueError('C-N predictor returned an incomplete candidate set')
            return {'status':'ok','predictions':[{**row,'id':candidate['id']}
                for candidate,row in zip(candidates,results)]}
        artifact = getattr(cn_condition_model, 'artifact', getattr(cn_condition_model, '_artifact', None))
        bindings['score_cn_conditions'] = _binding(score_cn, 'score_cn_conditions', versions, timeout_seconds,
            artifact=_hash(artifact) if artifact is not None else None,
            model_version=getattr(cn_condition_model, 'metadata', {}).get('model_version','unknown'),
            config=_callback_metadata(cn_condition_model.predict))
    if reaction_yield_predictor is not None:
        def predict_yield(args):
            results = reaction_yield_predictor.predict(args['candidates'])
            if not isinstance(results, list) or len(results) != len(args['candidates']):
                raise ValueError('Yield predictor returned an incomplete candidate set')
            return {'status':'ok','predictions':results}
        artifact = getattr(reaction_yield_predictor, 'artifact', None)
        bindings['predict_reaction_yield'] = _binding(predict_yield, 'predict_reaction_yield', versions,
            getattr(reaction_yield_predictor, 'timeout_seconds', timeout_seconds),
            artifact=_hash(artifact) if artifact is not None else None,
            model_version=getattr(reaction_yield_predictor, 'metadata', {}).get('model_version','unknown'),
            config={'callback':_callback_metadata(reaction_yield_predictor.predict),
                    'runtime':_plain(getattr(reaction_yield_predictor, 'configuration', {}))})
    if impurity is not None:
        callback = impurity.predict if hasattr(impurity,'predict') else impurity
        bindings['predict_impurities'] = _binding(
            lambda args, predictor=callback: predictor('.'.join(args['reactants']), args['product'], args.get('top_k',5)),
            'predict_impurities',versions,getattr(impurity,'timeout_seconds',timeout_seconds),
            artifact=getattr(impurity,'artifact_sha256',None),
            model_version=getattr(impurity,'model_version','unknown'),
            config={'callback':_callback_metadata(callback),'runtime':_plain(getattr(impurity,'configuration',{}))})
    if evidence_corpus is not None:
        bindings['retrieve_sources'] = _binding(lambda args: evidence_corpus.retrieve(**args),
            'retrieve_sources',versions,timeout_seconds,authority='source_retrieval',
            artifact=evidence_corpus.fingerprint,model_version='none')
    if condition_study is not None:
        callback, fingerprint = _condition_callback(condition_study)
        bindings['observe_condition'] = _binding(callback,'observe_condition',versions,timeout_seconds,
            authority='measured_replay',artifact=fingerprint,model_version='none')
    if route_lookup is not None:
        bindings['compare_process'] = _binding(_process_callback(task,route_lookup,inventory_hash,process_basis),
            'compare_process',versions,timeout_seconds,authority='estimate',model_version='none',
            config={'task_sha256':_hash(task.model_dump(mode='json')),'basis':process_basis})
    if biocatalytic_records is not None and mode == 'evidence_retrieval':
        callback, fingerprint = _bio_callback(task,biocatalytic_records)
        bindings['retrieve_biocatalysis'] = _binding(callback,'retrieve_biocatalysis',versions,timeout_seconds,
            authority='source_retrieval',artifact=fingerprint,model_version='none')
    return ToolRegistry(bindings,stock_sha256=inventory_hash,
        evidence_sha256=evidence_corpus.fingerprint if evidence_corpus is not None else None)
