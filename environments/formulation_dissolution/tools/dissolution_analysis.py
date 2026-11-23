"""Method-stratified descriptive dissolution analysis and QC abstention."""
from collections import defaultdict
from tools.dissolution_history import normalize


def comparable(a,b):
    """Require matching actual method, dosage, strength, dose basis and storage."""
    keys=('api','dosage_form','strength_value','strength_unit','method_id','batch_id','storage_condition','dose_basis')
    return all(a.get(k)==b.get(k) for k in keys) and bool(a.get('method_id'))


def analyze(rows, baseline_id=None, specification=None):
    """Analyze only original observations, without interpolation or fabricated QC limits."""
    groups=defaultdict(list)
    for row in rows:
        record=normalize(row)
        groups[row['profile_id']].append(record)
    summaries={}
    for pid,group in groups.items():
        summaries[pid]={'profile_id':pid,'method_id':group[0]['method_id'],
            'source_id':group[0]['source_id'],'evidence_label':group[0]['evidence_label'],
            'time_min':[r['derived_time_min'] for r in group if r['release_value'] is not None],
            'release_percent':[r['release_value'] for r in group if r['release_value'] is not None],
            'missing_points':sum(r['release_value'] is None for r in group),
            'raw_unit_variability':'unavailable' if not all(r.get('sample_id') for r in group) else 'available'}
    differences={}
    if baseline_id:
        if baseline_id not in groups: raise ValueError('baseline profile not found')
        base=groups[baseline_id]
        for pid,group in groups.items():
            if pid==baseline_id: continue
            if not comparable(group[0],base[0]):
                differences[pid]={'status':'not_evaluated','reason':'method/product/batch/storage mismatch or unspecified'}
                continue
            at={r['derived_time_min']:r['release_value'] for r in base}
            differences[pid]={'status':'derived','evidence_label':'derived','baseline_id':baseline_id,
                'differences_percentage_points':{str(r['derived_time_min']):r['release_value']-at[r['derived_time_min']]
                    for r in group if r['derived_time_min'] in at and r['release_value'] is not None and at[r['derived_time_min']] is not None}}
    qc={'status':'not_evaluated','reason':'product-specific approved specification and affected-lot unit measurements unavailable'}
    if specification:
        if not specification.get('verified') or not specification.get('source_id'):
            qc={'status':'not_evaluated','reason':'unverified specification'}
        else:
            qc={'status':'not_evaluated','reason':'requires source-linked affected-lot measurements and applicable stage/unit rules'}
    return {'status':'success','summaries':summaries,'baseline_differences':differences,
            'specification_attainment':qc,'affected_lot_baseline':'not_available',
            'conclusion':'insufficient_data'}
