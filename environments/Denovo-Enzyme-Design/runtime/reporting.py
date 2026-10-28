"""Materialize the documented result bundle from reviewed, current artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import uuid

from contracts import load_json, object_hash, verify_artifact


def archive_replaced_exports(root: Path, out: Path, signature: str) -> None:
    manifest = out / 'manifest.json'
    if manifest.exists() and load_json(manifest).get('export_signature') == signature:
        return
    if not any((out / name).exists() for name in ('structures', 'chemistry')):
        return
    history_root = root / 'result_history'
    if history_root.is_symlink():
        raise ValueError('Result history must be a local directory, not a symlink')
    history_root.mkdir(exist_ok=True)
    history = history_root / uuid.uuid4().hex
    shutil.copytree(out, history, symlinks=True)
    (history / 'SUPERSEDED.json').write_text(json.dumps({
        'status': 'SUPERSEDED',
        'reason': 'Qualified candidates or accepted artifact versions changed',
        'scope': 'Historical export only; read qualification from the current 08_results bundle.'
    }, indent=2) + '\n')
    for name in ('structures', 'chemistry'):
        path = out / name
        if path.is_symlink():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)


def write_bundle(root: Path, state: dict, summary: dict) -> None:
    out = root / '08_results'
    if out.is_symlink():
        raise ValueError('Result bundle must be a local directory, not a symlink')
    out.mkdir(exist_ok=True)
    refs = summary['artifacts']
    export_signature = object_hash({'qualified_ids': summary['qualified_candidates'], 'artifacts': refs})
    archive_replaced_exports(root, out, export_signature)

    def read(kind, default):
        if kind not in refs:
            return default
        try:
            return load_json(verify_artifact(refs[kind], root))
        except (ValueError, OSError):
            return default

    def write(name, value):
        path = out / name
        temp = path.with_suffix(path.suffix + '.tmp')
        temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        temp.replace(path)

    request = read('resolved_request', {})
    candidates = read('candidate_manifest', {'candidates': []})['candidates']
    models = []
    fold = state['stages']['fold']
    if fold['status'] == 'accepted':
        for ref in fold['artifacts']:
            if ref['kind'] == 'stage_evidence':
                models = load_json(verify_artifact(ref, root)).get('assessment_models', [])
    assessed = {m['candidate_id']: m['structure'] for m in models}
    qualified = set(summary['qualified_candidates'])
    if not qualified.issubset(assessed):
        raise ValueError('Qualified export requires a reviewed assessment model for every selected candidate')
    write('assessment_models.json', {'models': models,
          'scope': 'Reviewed computational assessment models; generated scaffolds remain in the candidate manifest.'})
    evaluation = read('evaluation', {'candidates': [], 'unresolved': [summary['reason']]})
    evaluation.update(run_id=state['run_id'], status=summary['status'], stop_reason=summary['reason'],
                      requested_count=request.get('execution', {}).get('final_count'),
                      generated_count=len(state.get('candidate_history', {})),
                      qualified_count=len(qualified), qualified_ids=summary['qualified_candidates'])
    write('evaluation.json', evaluation)
    assemblies = []
    metric_rows = {row['candidate_id']: {r['rule_id']: r for r in row.get('rules', [])}
                   for row in evaluation.get('candidates', [])}
    metric_names = sorted({name for identity in qualified for name in metric_rows.get(identity, {})})
    with (out / 'designed_sequences.fasta').open('w') as fasta, (out / 'shortlist.csv').open('w', newline='') as table:
        writer = csv.writer(table)
        writer.writerow(['rank', 'candidate_id', 'sequence_id', 'structure', 'rule_evidence', *metric_names])
        by_id = {c['candidate_id']: c for c in candidates}
        for rank, identity in enumerate(summary['qualified_candidates'], 1):
            candidate = by_id[identity]
            key = 'candidate_' + object_hash(identity)[:16]
            seq = []
            for line in verify_artifact(candidate['sequence'], root).read_text().splitlines():
                if line.startswith('>'):
                    if seq:
                        break
                elif line.strip():
                    seq.append(line.strip())
            fasta.write(f'>{key}\n' + ''.join(seq) + '\n')
            selected = assessed[identity]
            source = verify_artifact(selected, root)
            target = out / 'structures' / (key + source.suffix)
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, target)
            mapping = load_json(verify_artifact(candidate['assembly_map'], root))
            assemblies.append({'candidate_id': identity, 'sequence_id': key, 'mapping': mapping,
                               'structure': str(target.relative_to(out)),
                               'sequence_sha256': candidate['sequence']['sha256'],
                               'structure_sha256': selected['sha256'],
                               'generated_structure': candidate['structure']})
            values = [json.dumps(metric_rows.get(identity, {}).get(name, {}).get('value'), allow_nan=False)
                      for name in metric_names]
            writer.writerow([rank, identity, key, str(target.relative_to(out)), 'evaluation.json', *values])
    write('assemblies.json', {'assemblies': assemblies})
    if qualified:
        (out / 'chemistry').mkdir(exist_ok=True)
        profile = read('qualified_profile', {})
        chemical_rules = {r['rule_id'] for r in profile.get('rules', []) if r['group'] in
                          {'reaction_identity', 'reactive_geometry', 'protonation_and_stabilization', 'states_and_chemical_steps'}}
        write('chemistry/evidence.json', {'candidates': {identity: {name: value for name, value in
              metric_rows.get(identity, {}).items() if name in chemical_rules} for identity in qualified}})
    write('manifest.json', {'run_id': state['run_id'], 'condition': state['condition'],
          'export_signature': export_signature,
          'input_files': state['inputs'], 'policy_sha256': state['policy_sha256'],
          'implementation_sha256': state['implementation_sha256'], 'accepted_artifacts': refs,
          'assessment_models': models,
          'execution_approval_block': summary.get('execution_approval_block'),
          'seed': request.get('execution', {}).get('seed'), 'usage': state['usage'],
          'outstanding_jobs': summary['outstanding_jobs'], 'unreconciled_call': summary['unreconciled_call']})
    (out / 'report.md').write_text(
        '# Denovo Enzyme Design — run report\n\n'
        f"Status: **{summary['status']}**. Qualified candidates: **{len(qualified)}**.\n\n"
        + summary['reason'] + '\n\n'
        'Results are computational. Unfinished assessments and development fixtures do not establish catalysis.\n\n'
        'See evaluation.json for rule evidence, state.json in the run root for stage progress, '
        'and manifest.json for provenance, resource scope and outstanding jobs.\n')
    if (root / 'trajectory.jsonl').exists():
        shutil.copyfile(root / 'trajectory.jsonl', out / 'trajectory.jsonl')
