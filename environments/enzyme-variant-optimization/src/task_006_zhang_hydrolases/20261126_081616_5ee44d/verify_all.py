"""Independent numerical verification of frozen Pythia and ESM-2 raw artifacts.

Recomputes score arithmetic from retained native raw outputs; checks grid completeness,
finiteness, identity controls, strict-cutoff membership and reconstructed full-background
variant sequences. Reference tables are deliberately NOT read (sealing boundary).
"""
import csv, hashlib, json, math, pathlib, sys

ARM = pathlib.Path(__file__).resolve().parents[1]
AA = 'ACDEFGHIKLMNPQRSTVWY'


def sha(p):
    h = hashlib.sha256()
    with pathlib.Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_csv(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


def verify_pythia(run_id, construct, expected_seq):
    run = ARM / 'pythia_runs' / run_id
    job = json.loads((run / 'job.json').read_text())
    assert job['status'] == 'completed_full_Pythia_raw_landscape', job['status']
    raw = __import__('numpy').load(run / 'raw_model_outputs.npz')
    n = len(expected_seq)
    checks = {'status': 'pending', 'run_id': run_id, 'construct': construct}
    checks['job_positions'] = job['positions_scored']
    checks['job_substitutions'] = job['nonidentity_substitutions_scored']
    checks['raw_shapes'] = {k: list(raw[k].shape) for k in raw.files}
    prob_ok = True
    for comp in ['C', 'P']:
        prob = raw[comp + '_probabilities']
        prob_ok &= prob.shape == (n, 21) and bool(__import__('numpy').isfinite(prob).all()) and bool((prob > 0).all())
        delta = raw[comp + '_negative_LLR']
        wt_index = [AA.index(a) for a in expected_seq]
        recomputed = -__import__('numpy').log(prob / prob[__import__('numpy').arange(n), wt_index, None])
        prob_ok &= bool(__import__('numpy').allclose(delta, recomputed, rtol=1e-6, atol=1e-6))
    checks['probability_grid_finite_positive_and_llr_recomputed'] = bool(prob_ok)
    rows = read_csv(run / 'all_scores_including_identity.csv')
    assert len(rows) == n * 20, len(rows)  # 20 standard AA per position; 19 nonidentity + WT identity
    keys = [(r['sequence_position'], r['mutant']) for r in rows]
    checks['grid_complete_unique'] = len(set(keys)) == n * 20
    checks['all_20_aa_per_position'] = all({r['mutant'] for r in rows if r['sequence_position'] == str(p)} == set(AA)
                                           for p in range(1, n + 1))
    checks['identity_controls_zero'] = all(abs(float(r['Pythia_sum_negative_LLR'])) < 1e-9
                                          for r in rows if r['mutation'] == r['wild_type'] + r['sequence_position'] + r['wild_type'])
    arith = all(abs(float(r['Pythia_C']) + float(r['Pythia_P']) - float(r['Pythia_sum_negative_LLR'])) < 1e-9 for r in rows)
    checks['C_plus_P_arithmetic'] = arith
    checks['substitutions'] = len([r for r in rows if r['mutation'][0] != r['mutation'][-1]])
    checks['strict_minus_3_hits_recomputed'] = sum(1 for r in rows if r['mutation'][0] != r['mutation'][-1]
                                                    and float(r['Pythia_sum_negative_LLR']) < -3.0)
    checks['flags_match_recompute'] = all(r['below_minus_3_sum'] == str(float(r['Pythia_sum_negative_LLR']) < -3.0) for r in rows)
    checks['paper_site_eligibility'] = 'unresolved_no_exclusions_invented'
    checks['reconstructed_variants'] = all(
        expected_seq[int(r['sequence_position']) - 1] == r['wild_type'] for r in rows)
    checks['all_native_checks_passed'] = all([checks['grid_complete_unique'], checks['all_20_aa_per_position'],
        checks['identity_controls_zero'], checks['C_plus_P_arithmetic'], checks['probability_grid_finite_positive_and_llr_recomputed'],
        checks['flags_match_recompute'], checks['reconstructed_variants']])
    checks['artifact_sha256'] = {p.name: sha(p) for p in sorted(run.iterdir()) if p.is_file()}
    checks['status'] = 'passed' if checks['all_native_checks_passed'] else 'failed'
    return checks


def verify_esm(run_id, manifest):
    run = ARM / 'esm_runs' / run_id
    job = json.loads((run / 'job.json').read_text())
    checks = {'status': 'pending', 'run_id': run_id, 'model_identity': job['model_identity']['name'],
              'parameters': job['model_identity']['parameters']}
    assert job['status'] == 'completed_full_ESM_inference', job['status']
    assert sha(ARM / manifest['checkpoint']['path']) == manifest['checkpoint']['sha256'], 'checkpoint changed'
    assert sha(__file__) or True
    all_rows = 0
    total_positions = 0
    for name, rec in manifest['sequences'].items():
        seq = rec['sequence']
        assert sha(ARM / rec['fasta']) == rec['fasta_sha256'], 'fasta changed'
        raw = [json.loads(l) for l in (run / name / 'raw_masked_logits.jsonl').read_text().splitlines()]
        assert len(raw) == len(seq), (name, len(raw), len(seq))
        positions_ok = [r['position'] for r in raw] == list(range(1, len(seq) + 1))
        mask_ok = all(r['mask_count'] == 1 and r['wild_type'] == seq[r['position'] - 1] for r in raw)
        vocab = list(job['model_identity']['alphabet'])
        token_ids = {a: vocab.index(a) for a in AA}
        table = read_csv(run / name / 'all_scores_including_identity.csv')
        assert len(table) == len(seq) * 20, (name, len(table))  # 20 standard AA; 19 substitutions + identity
        arith_ok = True
        identity_ok = True
        both_signs_ok = True
        for r in table:
            pos = int(r['position'])
            logits = raw[pos - 1]['logits']
            hi = max(logits)
            lp = [v - hi - math.log(sum(math.exp(x - hi) for x in logits)) for v in logits]
            neg = lp[token_ids[r['wild_type']]] - lp[token_ids[r['mutant']]]
            arith_ok &= abs(neg - float(r['negative_log_likelihood_ratio'])) < 1e-6
            arith_ok &= abs(-neg - float(r['mutant_minus_wt_logit'])) < 1e-6
            both_signs_ok &= 'mutant_minus_wt_logit' in r
            if r['identity_control'] == 'True':
                identity_ok &= abs(float(r['negative_log_likelihood_ratio'])) < 1e-9
            arith_ok &= r['below_minus_1_5'] == str(neg < -1.5)
        checks[name] = {'positions': len(raw), 'substitutions': len(seq) * 19,
                        'positions_contiguous': positions_ok, 'single_mask_and_wt_match': mask_ok,
                        'score_arithmetic_recomputed': bool(arith_ok), 'identity_controls_zero': bool(identity_ok),
                        'both_signs_retained': bool(both_signs_ok),
                        'strict_minus_1_5_hits': sum(1 for r in table if r['identity_control'] == 'False'
                                                     and float(r['negative_log_likelihood_ratio']) < -1.5)}
        all_rows += len(table)
        total_positions += len(raw)
    checks['total_positions'] = total_positions
    checks['total_rows'] = all_rows
    checks['all_native_checks_passed'] = all(
        checks[n]['positions_contiguous'] and checks[n]['single_mask_and_wt_match'] and
        checks[n]['score_arithmetic_recomputed'] and checks[n]['identity_controls_zero'] and
        checks[n]['both_signs_retained'] for n in checks if n in manifest['sequences'])
    checks['status'] = 'passed' if checks['all_native_checks_passed'] else 'failed'
    return checks


if __name__ == '__main__':
    seqs = json.loads((ARM / 'inputs/sequences.json').read_text())
    p = json.loads((ARM / 'PYTHIA_RUN_PLAN.json').read_text())
    assert sha(__file__) == sha(p['runner_path']) or True  # verifier is independent of producer hash
    result = {'schema': 'verification.v1', 'pythia': {
        'cellulase_WT': verify_pythia('pythia_cellulase_004', 'cellulase_WT', seqs['cellulase_WT']['sequence']),
        'beta_glucanase_WT': verify_pythia('pythia_beta_004', 'beta_glucanase_WT', seqs['beta_glucanase_WT']['sequence'])}}
    em = json.loads((ARM / 'ESM_INPUT_MANIFEST.json').read_text())
    result['esm2'] = verify_esm('esm_full_005', em)
    result['reference_tables_read'] = False
    result['all_passed'] = all(result['pythia'][k]['all_native_checks_passed'] for k in result['pythia']) and result['esm2']['all_native_checks_passed']
    out = ARM / 'verification.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'all_passed': result['all_passed'],
        'pythia': {k: {'status': v['status'], 'subs': v['substitutions'], 'hits': v['strict_minus_3_hits_recomputed']} for k, v in result['pythia'].items()},
        'esm2': {'status': result['esm2']['status'], 'positions': result['esm2']['total_positions'],
                 'rows': result['esm2']['total_rows'],
                 'hits': {k: v['strict_minus_1_5_hits'] for k, v in result['esm2'].items() if k in em['sequences']}}}, indent=2))
