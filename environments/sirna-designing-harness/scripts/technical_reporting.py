"""Portable, fail-closed technical reporting of recorded siRNA-Bench evidence.

Standard library only. Never generates sequences, dispatches models, edits inputs,
or upgrades a native Boolean with missing evidence into a biological pass.
"""
from __future__ import annotations
import csv, hashlib, json, math, re
from pathlib import Path

REQUIRED_GATES = ('sequence_integrity', 'reference_mapping', 'model_execution',
                  'configured_properties', 'native_filter_integrity', 'reproducibility', 'provenance')
METRICS = ('eff_RN.Ai-Predict', 'eff_RNAiSpline', 'guide_target_duplex_delta_g_kcal_mol',
           'target_site_mean_unpaired_prob', 'rank_score')
BUNDLE_INPUTS = {'references', 'candidates', 'bench_results', 'bench_gates',
                 'reproducibility_results', 'supplemental_annotations'}
POLICY_KEYS = {'schema_version', 'required_technical_gates', 'gc_min', 'gc_max',
               'min_RN_Ai_percent', 'min_RNAiSpline_probability', 'duplex_min_kcal_mol',
               'duplex_max_kcal_mol', 'max_native_guide_full_hits', 'max_seed_occurrence_fold',
               'max_native_POTS_percentile', 'min_guide_seed_viability_annotation',
               'reproducibility_absolute_tolerance', 'scope_note'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out: raise ValueError('Duplicate JSON key: ' + key)
        out[key] = value
    return out


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + value)))


def number(value):
    if isinstance(value, bool) or value is None or value == '': raise ValueError('Missing/non-numeric evidence')
    result = float(value)
    if not math.isfinite(result): raise ValueError('Nonfinite numeric evidence')
    return result


def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        if not fields or any(not x for x in fields) or len(fields) != len(set(fields)):
            raise ValueError('Nonempty unique CSV headers required: ' + str(path))
        rows = list(reader)
        if any(None in row or any(v is None for v in row.values()) for row in rows):
            raise ValueError('Malformed CSV row: ' + str(path))
        return rows


def keyed(rows):
    out = {}
    for row in rows:
        key = row.get('candidate_id', '')
        if not key or key in out: raise ValueError('Nonempty unique candidate_id required')
        out[key] = row
    if not out: raise ValueError('No candidate evidence supplied')
    return out


def relative_file(root, name):
    if not isinstance(name, str): raise ValueError('Relative evidence path required')
    p = Path(name)
    if not name or p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe evidence path: ' + name)
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink(): raise ValueError('Evidence symlink refused: ' + name)
    resolved = current.resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError('Evidence path missing or outside bundle: ' + name)
    return resolved


def policy_check(p):
    if set(p) != POLICY_KEYS or type(p.get('schema_version')) is not int or p['schema_version'] != 1:
        raise ValueError('Explicit technical policy schema/keys required')
    if p['required_technical_gates'] != list(REQUIRED_GATES):
        raise ValueError('Mandatory technical gates may not be removed or reordered')
    for key in POLICY_KEYS - {'schema_version', 'required_technical_gates', 'scope_note'}: number(p[key])
    if not 0 <= p['gc_min'] <= p['gc_max'] <= 1: raise ValueError('Invalid GC bounds')
    if not 0 <= p['min_RN_Ai_percent'] <= 100 or not 0 <= p['min_RNAiSpline_probability'] <= 1:
        raise ValueError('Invalid efficacy thresholds')
    if p['duplex_min_kcal_mol'] > p['duplex_max_kcal_mol']: raise ValueError('Reversed duplex bounds')
    for key in ('max_native_guide_full_hits', 'max_seed_occurrence_fold', 'reproducibility_absolute_tolerance'):
        if p[key] < 0: raise ValueError('Negative bound: ' + key)
    if not 0 <= p['max_native_POTS_percentile'] <= 100 or not 0 <= p['min_guide_seed_viability_annotation'] <= 100:
        raise ValueError('Invalid annotation threshold')
    return p


def references_check(data, bundle):
    if not isinstance(data, list) or not data: raise ValueError('Explicit reference records required')
    refs = {}
    for row in data:
        acc = row['transcript_id']
        if not re.fullmatch(r'NM_[0-9]+\.[0-9]+', acc) or acc in refs: raise ValueError('Invalid/duplicate exact reference token')
        if row.get('organism') != 'Homo sapiens' or row.get('orientation') != 'transcript_sense_5to3' or row.get('gene') != bundle.get('target_gene') or not bundle.get('target_gene'):
            raise ValueError('Unsupported organism/orientation or mismatched target-gene metadata')
        seq = row['sequence']; alphabet = row['alphabet']
        if alphabet not in ('DNA', 'RNA') or not seq or set(seq) - set('ACGT' if alphabet == 'DNA' else 'ACGU'):
            raise ValueError('Exact reference alphabet required; no normalization')
        if alphabet == 'DNA' and bundle.get('allow_DNA_reference_comparison') is not True:
            raise ValueError('Explicit DNA-reference comparison approval required')
        refs[acc] = seq.replace('T', 'U') if alphabet == 'DNA' else seq
    required = bundle['coverage_references']
    if not isinstance(required, list) or not required or len(required) != len(set(required)) or set(required) != set(refs):
        raise ValueError('Declared coverage references must equal supplied exact records')
    if bundle['primary_reference'] not in refs: raise ValueError('Primary reference absent')
    return refs


def status_from(gates):
    if any(g['status'] == 'FAILED' for g in gates): return 'FAILED_DECLARED_TECHNICAL_GATES'
    if any(g['status'] != 'PASSED' for g in gates): return 'BLOCKED_MISSING_TECHNICAL_EVIDENCE'
    return 'PASSED_DECLARED_TECHNICAL_GATES'


def evaluate(bundle_path, policy_path):
    bundle_path = Path(bundle_path).resolve(); root = bundle_path.parent
    b = load(bundle_path); p = policy_check(load(policy_path))
    if type(b.get('schema_version')) is not int or b['schema_version'] != 1: raise ValueError('Unsupported bundle schema')
    if b.get('evidence_origin') not in ('RECORDED_LOCAL_SIRNA_BENCH_RUN', 'SOFTWARE_FIXTURE_NOT_SCIENTIFIC_RESULT'):
        raise ValueError('Explicit recorded evidence or software-fixture origin required')
    if not b.get('experiment_id') or b.get('strand_orientation') != 'guide_and_passenger_5to3':
        raise ValueError('Experiment and strand orientation must be explicit')
    if not b.get('source_job') or not b.get('reproducibility_source_job') or b['source_job'] == b['reproducibility_source_job']:
        raise ValueError('Reproducibility requires a distinct declared earlier job')
    if set(b.get('inputs', {})) != BUNDLE_INPUTS: raise ValueError('Complete evidence input set required')
    paths = {}; binding = []
    for name, desc in b['inputs'].items():
        path = relative_file(root, desc['path'])
        if not re.fullmatch('[0-9a-f]{64}', desc.get('sha256', '')) or sha(path) != desc['sha256']:
            raise ValueError('Evidence checksum mismatch: ' + name)
        paths[name] = path; binding.append({'role': name, 'path': desc['path'], 'sha256': sha(path)})
    refs = references_check(load(paths['references']), b)
    candidates = keyed(read_csv(paths['candidates'])); native = keyed(read_csv(paths['bench_results']))
    previous = keyed(read_csv(paths['reproducibility_results'])); annotations = keyed(read_csv(paths['supplemental_annotations']))
    if set(candidates) != set(native) or not set(candidates) <= set(previous) or set(candidates) != set(annotations):
        raise ValueError('Evidence candidate cohorts do not match')
    if not 1 <= len(candidates) <= 100: raise ValueError('Technical interface supports1..100 explicit candidates')
    gate_rows = read_csv(paths['bench_gates']); by_gate = {}; outside = set()
    for row in gate_rows:
        cid = row['candidate_id']; key = (cid, row['gate'])
        if cid not in candidates or key in by_gate or row['passed'] not in ('True', 'False'):
            raise ValueError('Malformed/duplicate native gate or unknown candidate')
        by_gate[key] = row
    out = []
    for cid, c in candidates.items():
        n = native[cid]; old = previous[cid]; ann = annotations[cid]; gates = []; flags = []; props = {}
        def gate(name, status, detail):
            gates.append({'name': name, 'required': True, 'status': status, 'detail': detail})
        g, passenger = c.get('guide_sequence', ''), c.get('passenger_sequence', '')
        annotation_identity = ann.get('guide_sequence') == g and ann.get('passenger_sequence') == passenger
        paired = len(g) == len(passenger) == 19 and not set(g + passenger) - set('ACGU') and g.translate(str.maketrans('ACGU', 'UGCA'))[::-1] == passenger
        same = n.get('guide') == g and n.get('passenger') == passenger
        gate('sequence_integrity', 'PASSED' if paired and same else 'FAILED', 'Exact supplied19nt RNA pairing and native output identity')
        try:
            a, z = c['target_start'], c['target_end']
            if not re.fullmatch('[1-9][0-9]*', a) or not re.fullmatch('[1-9][0-9]*', z): raise ValueError('Literal positive integer coordinates required')
            a, z = int(a), int(z); target = refs[b['primary_reference']]
            unique = sum(target[i:i+19] == passenger for i in range(len(target)-18)) == 1
            mapped = z == a + 18 and target[a-1:z] == passenger and unique and a >= 20 and z + 19 <= len(target)
            mapped = mapped and c.get('transcript_id') == b['primary_reference'] and all(passenger in seq for seq in refs.values()) and n.get('target_start') == str(a) and n.get('target_end') == str(z)
            gate('reference_mapping', 'PASSED' if mapped else 'FAILED', 'Primary exact unique/full-flank mapping plus every declared coverage reference')
        except (KeyError, ValueError):
            gate('reference_mapping', 'FAILED', 'Invalid coordinate/reference evidence')
        model_ok = all(n.get('eff_' + model + '_status') == 'ok' for model in ('RN.Ai-Predict', 'RNAiSpline'))
        gate('model_execution', 'PASSED' if model_ok else 'BLOCKED_MISSING_EVIDENCE', 'Actual required-model statuses; not checkpoint presence')
        try:
            props = {key: number(n.get(key)) for key in (*METRICS, 'full_length_offtarget_hits', 'seed_occurrence_fold_over_expected', 'pots_seed_percentile', 'seed_tox_viability_avg_human')}
            gc = sum(x in 'GC' for x in g) / len(g) if g else -1
            bounds = [p['gc_min'] <= gc <= p['gc_max'], 0 <= props['eff_RN.Ai-Predict'] <= 100, 0 <= props['eff_RNAiSpline'] <= 1,
                      props['eff_RN.Ai-Predict'] >= p['min_RN_Ai_percent'], props['eff_RNAiSpline'] >= p['min_RNAiSpline_probability'],
                      p['duplex_min_kcal_mol'] <= props['guide_target_duplex_delta_g_kcal_mol'] <= p['duplex_max_kcal_mol'],
                      0 <= props['full_length_offtarget_hits'] <= p['max_native_guide_full_hits'],
                      0 <= props['seed_occurrence_fold_over_expected'] <= p['max_seed_occurrence_fold'],
                      0 <= props['pots_seed_percentile'] <= p['max_native_POTS_percentile'],
                      p['min_guide_seed_viability_annotation'] <= props['seed_tox_viability_avg_human'] <= 100,
                      0 <= props['target_site_mean_unpaired_prob'] <= 1]
            gate('configured_properties', 'PASSED' if all(bounds) else 'FAILED', 'Explicit operational property/annotation bounds; no clinical cutoffs inferred')
        except (ValueError, ZeroDivisionError):
            gate('configured_properties', 'BLOCKED_MISSING_EVIDENCE', 'Required finite property evidence missing')
        native_status = 'PASSED'; native_details = []
        for name in ('A_input_integrity', 'B_computational_suitability', 'B_seed_toxicity_flag'):
            r = by_gate.get((cid, name))
            if r is None:
                if native_status != 'FAILED': native_status = 'BLOCKED_MISSING_EVIDENCE'
                native_details.append(name + ': missing'); continue
            if r['passed'] != 'True' or r.get('failed_criteria'):
                native_status = 'FAILED'; native_details.append(name + ': ' + r.get('failed_criteria', 'native failure'))
            missing = r.get('missing_evidence', '')
            if missing:
                flags.append({'flag': 'NATIVE_MISSING_EVIDENCE', 'gate': name, 'detail': missing})
                explicitly_resolved = name == 'A_input_integrity' and missing == 'orientation_documentation' and paired and same
                optional_model = name == 'B_computational_suitability' and missing == 'siRNADiscovery: no pretrained checkpoint'
                if not (explicitly_resolved or optional_model) and native_status != 'FAILED': native_status = 'BLOCKED_MISSING_EVIDENCE'
        gate('native_filter_integrity', native_status, '; '.join(native_details) or 'Raw native Booleans, explicit failures and missing-evidence fields reviewed')
        try:
            repeated = old.get('guide') == g and old.get('passenger') == passenger
            repeated = repeated and all(old.get('eff_' + model + '_status') == 'ok' for model in ('RN.Ai-Predict', 'RNAiSpline'))
            diffs = {key: abs(number(n.get(key)) - number(old.get(key))) for key in METRICS}
            gate('reproducibility', 'PASSED' if repeated and all(v <= p['reproducibility_absolute_tolerance'] for v in diffs.values()) else 'FAILED',
                 'Recorded earlier-job comparison for identical candidate/reference endpoints; not independent efficacy validation')
        except ValueError:
            diffs = {}; gate('reproducibility', 'BLOCKED_MISSING_EVIDENCE', 'Earlier-job finite endpoint evidence absent')
        gate('provenance', 'PASSED' if annotation_identity else 'FAILED', 'SHA-256 bindings, source job identities and supplemental-to-candidate sequence identity checked')
        ridge_literal = c.get('source_Ridge_literal', '')
        if ridge_literal:
            if not re.fullmatch(r'[-+]?[0-9]+(?:\.[0-9]+)?\*?', ridge_literal): raise ValueError('Unsupported literal Ridge annotation')
            if ridge_literal.endswith('*') or not 0 <= number(ridge_literal.rstrip('*')) <= 100:
                flags.append({'flag': 'RIDGE_EXTRAPOLATION', 'detail': ridge_literal + ' retained, not clipped or treated as measured inhibition'})
        if ann.get('passenger_seed_viability_annotation', '') != '' and number(ann['passenger_seed_viability_annotation']) < 50:
            flags.append({'flag': 'PASSENGER_SEED_ANNOTATION_LT50', 'detail': ann['passenger_seed_viability_annotation'] + '; reused source-scaffold annotation, not exact-duplex toxicity'})
        near_keys = [s + '_unintended_' + str(mm) + 'mm_alignments' for s in ('guide', 'passenger') for mm in (1, 2)]
        if all(ann.get(key, '') != '' for key in near_keys):
            if any(number(ann[key]) > 0 for key in near_keys):
                flags.append({'flag': 'RECORDED_NEAR_MATCH_OPPORTUNITIES', 'detail': 'Reused guide1/2mm and passenger1/2mm transcript-alignment counts: ' + '/'.join(ann[key] for key in near_keys) + '; no fresh broader scan in this report'})
        else:
            flags.append({'flag': 'SUPPLEMENTAL_NEAR_MATCH_COUNTS_NOT_PROVIDED', 'detail': 'Absent supplemental counts are not treated as zero'})
        for r in gate_rows:
            if r['candidate_id'] == cid and r['gate'] in ('C_experimental_evidence', 'D_translational_evidence') and r.get('missing_evidence'):
                flags.append({'flag': 'SEPARATE_SCOPE_MISSING_EVIDENCE', 'gate': r['gate'], 'native_passed_literal': r['passed'], 'detail': r['missing_evidence']})
        flags.append({'flag': 'NATIVE_PRIORITY_POLICY_LIMITATION', 'detail': 'Native POTS percentile-direction convention retained; priority is operational, not calibrated efficacy'})
        out.append({'candidate_id': cid, 'guide_sequence': g, 'passenger_sequence': passenger,
                    'target_start': c['target_start'], 'target_end': c['target_end'], 'source_Ridge_literal': ridge_literal,
                    'technical_status': status_from(gates), 'gates': gates, 'properties': props,
                    'raw_model_statuses': {model: n.get('eff_' + model + '_status', 'NOT_RUN') for model in ('RN.Ai-Predict', 'RNAiSpline', 'siRNADiscovery')},
                    'raw_native_gate_records': [r for r in gate_rows if r['candidate_id'] == cid],
                    'reused_supplemental_annotations': ann, 'reproducibility_absolute_differences': diffs, 'review_flags': flags})
    statuses = [r['technical_status'] for r in out]
    overall = 'FAILED_DECLARED_TECHNICAL_GATES' if 'FAILED_DECLARED_TECHNICAL_GATES' in statuses else 'BLOCKED_MISSING_TECHNICAL_EVIDENCE' if 'BLOCKED_MISSING_TECHNICAL_EVIDENCE' in statuses else 'PASSED_DECLARED_TECHNICAL_GATES'
    return {'schema_version': 1, 'environment': 'siRNA Designing Harness', 'experiment_id': b['experiment_id'],
            'technical_status': overall, 'submitted_count': len(out), 'technical_pass_count': statuses.count('PASSED_DECLARED_TECHNICAL_GATES'),
            'evidence_origin': b['evidence_origin'], 'source_job': b['source_job'], 'reproducibility_source_job': b['reproducibility_source_job'],
            'execution_scope': 'Deterministic technical review of recorded evidence; zero new scientific jobs',
            'technical_scope': list(REQUIRED_GATES), 'policy': p, 'input_bindings': binding,
            'bundle_sha256': sha(bundle_path), 'policy_sha256': sha(policy_path),
            'scope_note': 'Technical validation covers declared computational checks; biological efficacy, safety and delivery are separate evaluation stages.',
            'candidates': out}


def write_report(bundle, policy, destination):
    result = evaluate(bundle, policy); destination = Path(destination).resolve()
    if destination.exists(): raise ValueError('Refuse report overwrite; choose a new output directory')
    destination.mkdir(parents=True)
    (destination / 'technical_report.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    fields = ['candidate_id', 'technical_status', 'guide_sequence', 'passenger_sequence', 'target_start', 'target_end',
              'source_Ridge_literal', *METRICS, 'review_flags']
    with (destination / 'technical_candidates.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in result['candidates']:
            writer.writerow({**{k: row[k] for k in fields if k in row}, **{k: row['properties'].get(k, '') for k in METRICS},
                             'review_flags': ';'.join(x['flag'] for x in row['review_flags'])})
    lines = ['# siRNA design and technical validation', '',
             f"{result['technical_pass_count']} of {result['submitted_count']} candidates passed the declared technical gates.",
             '', 'Status: ' + result['technical_status'], 'Evidence: ' + result['evidence_origin'],
             '', result['scope_note'], '', '## Predicted and calculated properties', '',
             '| Candidate | Technical status | RN.Ai predicted % | RNAiSpline P | Duplex kcal/mol | Accessibility | Priority |',
             '|---|---|---:|---:|---:|---:|---:|']
    for row in result['candidates']:
        v = row['properties']; lines.append('| ' + row['candidate_id'] + ' | ' + row['technical_status'] + ' | ' +
            ' | '.join(str(v.get(k, 'MISSING')) for k in ('eff_RN.Ai-Predict', 'eff_RNAiSpline', 'guide_target_duplex_delta_g_kcal_mol', 'target_site_mean_unpaired_prob', 'rank_score')) + ' |')
    lines += ['', '## Candidate-specific review flags', '']
    common = {}
    shared_names = {'NATIVE_MISSING_EVIDENCE', 'SEPARATE_SCOPE_MISSING_EVIDENCE', 'NATIVE_PRIORITY_POLICY_LIMITATION'}
    for row in result['candidates']:
        specific = []
        for flag in row['review_flags']:
            if flag['flag'] in shared_names:
                key = (flag['flag'], flag.get('gate', ''), flag['detail'])
                common[key] = common.get(key, 0) + 1
            else:
                specific.append(flag['flag'] + ' — ' + flag['detail'])
        specific += [g['name'] + ': ' + g['status'] + ' — ' + g['detail'] for g in row['gates'] if g['status'] != 'PASSED']
        lines.append('- ' + row['candidate_id'] + ': ' + ('; '.join(specific) or 'No additional candidate-specific review flag in this declared scope.'))
    lines += ['', '## Shared tool and scope notes', '']
    for (flag, gate, detail), count in common.items():
        lines.append('- ' + flag + (' [' + gate + ']' if gate else '') + ': ' + detail + f' ({count} candidate records).')
    lines += ['', '## Evidence boundaries and next stage', '',
              'Native gate rows, failed/missing fields and reused supplemental annotations remain in technical_report.json. Model predictions and calculated properties are not measured endpoints. Gene/seed search scope, passenger loading, final chemistry, intended assay and delivery remain separate review items.',
              'This command reads recorded results only; it does not execute generation, inference, folding or screening. Repeated outputs are a reproducibility check on the declared inputs, not an independent efficacy benchmark.']
    (destination / 'technical_report.md').write_text('\n'.join(lines) + '\n')
    manifest = {'schema_version': 1, 'files': [{'path': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(destination.iterdir()) if p.is_file()]}
    mp = destination / 'output_manifest.json'; mp.write_text(json.dumps(manifest, indent=2) + '\n')
    receipt = {'verification': 'PASSED', 'scope': 'Report serialization/checksums; technical gate outcome is separate',
               'technical_status': result['technical_status'], 'output_manifest_sha256': sha(mp), 'new_scientific_jobs': 0}
    (destination / 'verification_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    for item in manifest['files']:
        if sha(destination / item['path']) != item['sha256']: raise ValueError('Report readback hash mismatch')
    return {'status': result['technical_status'], 'submitted_count': result['submitted_count'],
            'technical_pass_count': result['technical_pass_count'], 'output_directory': str(destination), 'new_scientific_jobs': 0}


def verify_case(root):
    root = Path(root).resolve(); manifest = load(root / 'snapshot_manifest.json'); errors = []
    expected = set()
    for item in manifest['files']:
        path = relative_file(root, item['path']); expected.add(item['path'])
        if sha(path) != item['sha256'] or path.stat().st_size != item['bytes']: errors.append(item['path'])
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'snapshot_manifest.json'}
    if expected != actual: errors.append('unmanifested_or_missing_file')
    return {'status': 'FAILED' if errors else 'PASSED', 'files_verified': len(expected), 'errors': errors,
            'scope': 'Bounded recorded assessment snapshot integrity; not new model execution', 'new_scientific_jobs': 0}
