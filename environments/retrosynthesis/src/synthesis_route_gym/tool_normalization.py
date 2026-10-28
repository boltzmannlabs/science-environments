"""Allowlisted projections from legacy backends to scientific tool contracts."""
from collections import Counter
from datetime import datetime
from .chemistry import canonical_smiles
from .tool_contracts import (OUTPUT_MODELS, ExpansionPrediction, ConditionPrediction, CNConditionPrediction,
    ReactionYieldPrediction, ForwardPrediction, ProcessRow, BioCandidate)


def _select(value, fields):
    if not isinstance(value, dict):
        raise ValueError('Expected record object')
    return {key:value[key] for key in fields if key in value}


def _rows(raw, key, maximum=10000):
    rows = raw.get(key)
    if not isinstance(rows, list) or len(rows) > maximum:
        raise ValueError('Invalid result collection')
    return rows


def _expansion(raw, args, binding):
    rows = [ExpansionPrediction(**{
        **_select(row, ('reactants','product','score')),
        'source':{'tool':'expand','version':binding.version},
    }).model_dump(mode='json') for row in _rows(raw, 'predictions')[:args['top_k']]]
    if any(row['product'] != args['smiles'] for row in rows):
        raise ValueError('Expansion product differs from query')
    return {'predictions':rows}


def _conditions(raw, args, binding):
    keys = ('id','predicted_yield_percent','lower_yield_percent','upper_yield_percent',
            'interval_kind','domain','unseen_components')
    rows = [ConditionPrediction(**{**_select(row, keys),
        'model_version':binding.model_version}).model_dump(mode='json')
        for row in _rows(raw, 'predictions', 1000)]
    if [row['id'] for row in rows] != [row['id'] for row in args['candidates']]:
        raise ValueError('Condition predictions must preserve requested IDs and order')
    return {'predictions':rows}


def _forward(raw, args, binding):
    rows = [ForwardPrediction(**_select(row, ('product','score'))).model_dump(mode='json')
            for row in _rows(raw, 'predictions')[:args['top_k']]]
    return {'predictions':rows, 'target_in_predictions':any(row['product']==args['product'] for row in rows)}


def _cn_conditions(raw, args, binding):
    keys = ('id','status','hit_score','raw_hit_score','reason','domain','calibration_kind')
    rows = [CNConditionPrediction(**{**_select(row, keys),
        'model_version':binding.model_version}).model_dump(mode='json')
        for row in _rows(raw, 'predictions', 1000)]
    if [row['id'] for row in rows] != [row['id'] for row in args['candidates']]:
        raise ValueError('C-N predictions must preserve requested IDs and order')
    return {'predictions':rows}


def _reaction_yield(raw, args, binding):
    keys = ('id','status','predicted_yield_percent','raw_yield_percent','reason','domain')
    rows = [ReactionYieldPrediction(**{**_select(row, keys),
        'model_version':binding.model_version}).model_dump(mode='json')
        for row in _rows(raw, 'predictions', 100)]
    if [row['id'] for row in rows] != [row['id'] for row in args['candidates']]:
        raise ValueError('Yield predictions must preserve requested IDs and order')
    return {'predictions':rows}


def _impurities(raw, args, binding):
    values = _rows(raw, 'predicted_smiles', 1000)
    values = list(dict.fromkeys(canonical_smiles(value) for value in values))
    return {'predicted_smiles':[v for v in values if v != args['product']][:args['top_k']]}


def _observation(raw, args, binding):
    result = _select(raw, ('candidate_id','conditions','yield_percent','source_record_id','dataset_sha256'))
    if result.get('candidate_id') != args['candidate_id']:
        raise ValueError('Observation differs from requested candidate')
    return result


def _valid_quote_date(value):
    if not isinstance(value,str) or not value or value != value.strip():
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def _basis(row):
    fields = ('target','scale_mmol','cost_currency','cost_basis','inventory_sha256','purity_basis')
    if (row.material_cost is None or any(getattr(row,key) is None for key in fields)
            or not _valid_quote_date(row.quoted_at) or not row.cost_source_id or row.price_status == 'unknown'):
        return None
    return tuple(getattr(row,key) for key in fields) + (tuple(sorted(row.exclusions)),)


def _process(raw, args, binding):
    keys = tuple(key for key in ProcessRow.model_fields if key not in {'comparison_eligible','cost_status'})
    rows = [ProcessRow(**_select(row, keys)) for row in _rows(raw,'routes',100)]
    if [row.route_id for row in rows] != args['route_ids']:
        raise ValueError('Process rows must match requested route IDs/order')
    bases = [_basis(row) for row in rows]
    common = bool(bases) and None not in bases and len(set(bases)) == 1
    if args.get('target_amount_mmol') is not None and any(row.scale_mmol != args['target_amount_mmol'] for row in rows):
        common = False
    def dominates(a,b):
        return a.material_cost <= b.material_cost and a.steps <= b.steps and (a.material_cost < b.material_cost or a.steps < b.steps)
    pareto = [r.route_id for r in rows if not any(dominates(other,r) for other in rows)] if common else []
    return {'routes':[{**row.model_dump(mode='json'),'comparison_eligible':common,
                       'cost_status':'unknown' if row.material_cost is None else 'supplied_estimate'} for row in rows],
        'pareto_route_ids':pareto, 'dominated_route_ids':[r.route_id for r in rows if r.route_id not in pareto] if common else [],
        'unranked_route_ids':[] if common else [r.route_id for r in rows], 'common_basis_known':common,
        'comparison_status':'comparable_supplied_estimates' if common else 'insufficient_common_basis'}


def _sources(raw, args, binding):
    from .evidence_contracts import SourceRecord, SourceProjection, public_projection
    if binding.artifact_sha256 is not None and raw.get('corpus_sha256') != binding.artifact_sha256:
        raise ValueError('Retrieved corpus differs from pinned source binding')
    projected=[]
    for row in _rows(raw,'records',20):
        parsed=SourceProjection.model_validate(row)
        source=SourceRecord.model_validate({k:v for k,v in parsed.model_dump().items() if k in SourceRecord.model_fields})
        if args.get('product') is not None and source.product != args['product']:
            raise ValueError('Retrieved source product differs from requested product')
        if args.get('reactants') is not None and Counter(source.reactants) != Counter(args['reactants']):
            raise ValueError('Retrieved source participants differ from requested participants')
        text=' '.join((source.record_id,source.document_id,source.locator)).casefold()
        if args.get('query') is not None and args['query'].casefold() not in text:
            raise ValueError('Retrieved source does not match the declared metadata query')
        expected=public_projection(source)
        if parsed.model_dump(mode='json') != expected:
            raise ValueError('Source record hash or projection mismatch')
        projected.append(expected)
    if len(projected) > args['limit'] or len({row['record_id'] for row in projected}) != len(projected):
        raise ValueError('Source retrieval exceeded limit')
    return {'records':projected, **_select(raw,('corpus_sha256','access_mode'))}


def _biocatalysis(raw, args, binding):
    from urllib.parse import urlsplit
    fields = ('record_id','enzyme_name','source_url','source_locator','reactants','products','cofactors','missing_reactants')
    rows=[]
    for value in _rows(raw,'candidates',20):
        selected=_select(value, fields)
        products=[canonical_smiles(p) for p in selected['products']]
        selected['match_kind']='exact_product' if args['target_smiles'] in products else 'analogue'
        row=BioCandidate(**selected)
        url=urlsplit(row.source_url)
        if url.scheme not in {'http','https'} or not url.netloc or url.username or url.password:
            raise ValueError('Biocatalytic source requires public HTTP(S) identity')
        rows.append(row.model_dump(mode='json'))
    if len(rows)>args['limit'] or len({r['record_id'] for r in rows}) != len(rows):
        raise ValueError('Invalid biocatalytic retrieval size or duplicate IDs')
    return {'candidates':rows}

_NORMALIZERS = {'expand':_expansion,'predict_conditions':_conditions,'forward_check':_forward,
 'score_cn_conditions':_cn_conditions,
 'predict_reaction_yield':_reaction_yield,
 'predict_impurities':_impurities,'observe_condition':_observation,'compare_process':_process,
 'retrieve_sources':_sources,'retrieve_biocatalysis':_biocatalysis}


def normalize_output(name, raw, arguments, binding):
    projected = _NORMALIZERS[name](raw, arguments, binding)
    return OUTPUT_MODELS[name].model_validate(projected).model_dump(mode='json')
