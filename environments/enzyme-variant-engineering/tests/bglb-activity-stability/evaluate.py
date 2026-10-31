"""Evaluate this case's saved designs, not molecular-tool inputs or predictions."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

ENV = Path(__file__).resolve().parents[2]
PARENT = ENV / 'tasks/bglb-activity-stability/parent.fasta'
REFERENCE = ENV / 'results/bglb-activity-stability/reference/s1.csv'
REFERENCE_SHA256 = '3d94ee8b73d4b67cc7c1f6def54b00a40bdacc6f1eaf1b53bcd01294fe58b619'
PARENT_SHA256 = '5595c3d42a0dfb9f365c84b05c993991e4cc7930f2d16160e09187e1329d6619'
FIELDS = ['candidate_id', 'rank', 'mutation', 'sequence']
AA = 'ACDEFGHIKLMNPQRSTVWY'
PROTECTED = {164, 295, 353}
DETECTION_LIMIT = 10.0  # M^-1 min^-1, from the paper; not an invented zero.


def parent_sequence():
    sequence = ''.join(line.strip() for line in PARENT.read_text().splitlines() if not line.startswith('>'))
    if len(sequence) != 445 or set(sequence) - set(AA):
        raise ValueError('The case parent must be the supplied 445-residue modelling core')
    if hashlib.sha256(sequence.encode()).hexdigest() != PARENT_SHA256:
        raise ValueError('The source-qualified case parent sequence changed')
    if [sequence[i-1] for i in sorted(PROTECTED)] != ['E', 'Y', 'E']:
        raise ValueError('Parent functional sites disagree with the case numbering')
    return sequence


def validate_selection(rows, parent):
    if len(rows) > 5:
        raise ValueError('This task returns at most five selected designs')
    ids, sequences, ranks = set(), set(), set()
    for row in rows:
        if set(row) != set(FIELDS) or any(not isinstance(v, str) for v in row.values()):
            raise ValueError('Selection rows need exactly candidate_id,rank,mutation,sequence')
        cid, sequence = row['candidate_id'], row['sequence']
        if not cid.strip() or cid != cid.strip() or cid in ids:
            raise ValueError('Candidate identifiers must be nonempty and unique')
        if len(sequence) != len(parent) or set(sequence) - set(AA):
            raise ValueError('Design sequence has invalid residues or length')
        changed = [i+1 for i, (a, b) in enumerate(zip(parent, sequence)) if a != b]
        if len(changed) != 1 or changed[0] in PROTECTED:
            raise ValueError('Each design needs one substitution outside protected sites')
        position = changed[0]
        if row['mutation'] != f'{parent[position-1]}{position}{sequence[position-1]}':
            raise ValueError('Mutation label disagrees with the actual study-numbered sequence')
        if sequence in sequences:
            raise ValueError('Duplicate sequences cannot fill the shortlist')
        if re.fullmatch(r'[1-9][0-9]*', row['rank']) is None or int(row['rank']) in ranks:
            raise ValueError('Ranks must be unique positive whole numbers')
        ids.add(cid); sequences.add(sequence); ranks.add(int(row['rank']))
    if ranks != set(range(1, len(rows)+1)):
        raise ValueError('Ranks must be contiguous from one')
    return sorted(rows, key=lambda row: int(row['rank']))


def number(value):
    if value is None or value.strip().upper() in {'', 'NA', 'N/A'}:
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Nonfinite source measurement')
    return result


def published_reference(path=REFERENCE):
    path = Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise ValueError('Published S1 source checksum changed; qualify a new version explicitly')
    with path.open(newline='') as handle:
        records = list(csv.DictReader(handle))
    indexed = {row['mutant']: row for row in records}
    if len(indexed) != len(records) or 'BglB' not in indexed:
        raise ValueError('Source mutant identities are duplicated or the reference is missing')
    parent = parent_sequence()
    for mutation in set(indexed) - {'BglB'}:
        match = re.fullmatch(r'(['+AA+r'])([1-9][0-9]*)(['+AA+r'])', mutation)
        if not match or not 1 <= int(match[2]) <= len(parent) or parent[int(match[2])-1] != match[1]:
            raise ValueError('Source mutation does not match the study-numbered parent')
    return indexed


def summarize(rows, reference):
    """Attach published values only; unknown/censored values are not fabricated."""
    parent = reference['BglB']
    wt_eff, wt_tm = number(parent['kcatkm']), number(parent['tm'])
    if wt_eff is None or wt_eff <= DETECTION_LIMIT or wt_tm is None:
        raise ValueError('Comparable source reference endpoints are missing')
    output, ratios, tm_deltas = [], [], []
    for row in rows:
        source = reference.get(row['mutation'])
        result = {'candidate_id': row['candidate_id'], 'rank': int(row['rank']),
                  'mutation': row['mutation'], 'published_match': source is not None,
                  'joint_point_rule': 'unknown', 'source_measurements': None}
        if source is not None:
            expression = number(source['expression'])
            tm = number(source['tm'])
            reported_efficiency = source['kcatkm'].strip()
            censored = reported_efficiency in {'<10','<=10'}
            efficiency = None if censored else number(reported_efficiency)
            kcat, km = number(source['kcat']), number(source['km'])
            if expression not in {0.0, 1.0}:
                raise ValueError('Source expression indicator must be zero or one')
            censored = censored or efficiency is not None and efficiency <= DETECTION_LIMIT
            if any(value is not None and value < 0 for value in (efficiency, kcat, km)):
                raise ValueError('Negative kinetic endpoint in source data')
            ratio = efficiency / wt_eff if efficiency is not None and not censored else None
            delta = tm - wt_tm if tm is not None else None
            if ratio is not None: ratios.append(ratio)
            if delta is not None: tm_deltas.append(delta)
            if (expression == 0 or censored or efficiency is not None and efficiency <= wt_eff
                    or tm is not None and tm < wt_tm):
                result['joint_point_rule'] = 'not_met'
            elif efficiency is not None and tm is not None:
                result['joint_point_rule'] = 'met'
            result['source_measurements'] = {
                'evidence': 'published_measurement_not_a_new_assay', 'expression': int(expression),
                'reported_efficiency_text': reported_efficiency,
                'functional_tm_c': tm, 'functional_tm_delta_c': delta,
                'kcat_per_min': kcat, 'km_mM': km,
                'kcat_per_s': None if kcat is None else kcat/60,
                'km_M': None if km is None else km*0.001,
                'kcat_over_km_M_inverse_min_inverse': None if censored else efficiency,
                'kcat_over_km_M_inverse_s_inverse': None if censored or efficiency is None else efficiency/60,
                'at_or_below_detection_limit': censored,
                'efficiency_ratio_to_parent': ratio,
            }
        output.append(result)
    return {'selected_count': len(rows), 'empty_shortlist': not rows,
            'published_match_count': sum(r['published_match'] for r in output),
            'not_in_published_table_count': sum(not r['published_match'] for r in output),
            'joint_point_rule_counts': {s: sum(r['joint_point_rule'] == s for r in output)
                                        for s in ('met', 'not_met', 'unknown')},
            'mean_efficiency_ratio': statistics.mean(ratios) if ratios else None,
            'mean_efficiency_ratio_denominator': len(ratios),
            'mean_functional_tm_delta_c': statistics.mean(tm_deltas) if tm_deltas else None,
            'mean_functional_tm_delta_denominator': len(tm_deltas),
            'reference_efficiency_M_inverse_min_inverse': wt_eff, 'reference_functional_tm_c': wt_tm,
            'candidates': output, 'new_experimental_validation': False,
            'statistically_significant_improvement_established': False,
            'comparison_mode': 'open_literature_retrospective_not_blinded',
            'limitation': 'Point rules are descriptive. Unknown designs are not measured improvements. Review method/artifact/assay comparability separately.'}


def evaluate(selection, reference_path=REFERENCE):
    selection = Path(selection)
    with selection.open(newline='') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError('Expected CSV header: '+','.join(FIELDS))
        rows = list(reader)
    rows = validate_selection(rows, parent_sequence())
    result = summarize(rows, published_reference(reference_path))
    result.update(selection_sha256=hashlib.sha256(selection.read_bytes()).hexdigest(),
                  reference_sha256=REFERENCE_SHA256,
                  parent_sequence_sha256=hashlib.sha256(parent_sequence().encode()).hexdigest(),
                  design_constraints_valid=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--reference', type=Path, default=REFERENCE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.selection, args.reference)
    with args.output.open('x') as handle:
        json.dump(report, handle, indent=2, allow_nan=False); handle.write('\n')
