#!/usr/bin/env python3
"""Reproduce the artificial campaign/evaluator fixture without a model or service."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from leadopt_env.core import CampaignStore
from leadopt_env.evaluation import evaluate


def read(path):
    return json.loads((ROOT / path).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New output directory; never overwritten')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    store = CampaignStore(args.output / 'campaign.sqlite3')
    def call(op, payload=None):
        return store.dispatch(op, 'synthetic-demo', payload)
    call('create', {'task': read('tasks/synthetic/task.json')})
    call('attach', {'session_id':'synthetic-session'})
    for c in read('tasks/synthetic/candidates.json'):
        call('candidate', c)
    check = call('check', dict(id='check1',job='synthetic_assessment',candidate_ids=['candidate-a','candidate-b'],resource_requests={'scientific_submissions':1}))
    call('action', dict(id='action1',attempt_id='attempt1',job='synthetic_assessment',candidate_ids=['candidate-a','candidate-b'],status='completed',check_id='check1',source='Synthetic fixture; no remote submission',rationale='Exercise evidence reporting'))
    for record in read('tasks/synthetic/observations.json'):
        call('observation', record)
    call('usage', dict(id='usage1',unit='scientific_submissions',amount=1,category='observed',scope='campaign',source='Artificial fixture counter; actual remote submissions = 0'))
    call('usage', dict(id='unknown1',unit='remote_internal_evaluations',amount=None,category='unknown',scope='campaign',source='Not measured by this environment'))
    call('decision', dict(id='decision1',question='Does candidate-a improve the artificial endpoint?',outcome='supported',evidence_ids=['lead-fixture-search','candidate-a-fixture-search'],next_action='Freeze candidate-a',rationale='Artificial compatible score difference; no chemistry conclusion'))
    frozen = call('freeze', dict(id='final',candidate_ids=['candidate-a'],rationale='Synthetic endpoint improvement',stopping_reason='Software fixture complete'))
    evaluation = evaluate(frozen, read('tests/synthetic-reference.json'), frozen['digest'])
    for name, value in [('check',check),('report',call('report')),('submission',frozen),('evaluation',evaluation)]:
        (args.output / (name+'.json')).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    (args.output / 'submission.sha256').write_text(frozen['digest']+'\n')
    print(json.dumps({'status':'synthetic_fixture_completed','output':str(args.output.resolve()),'scientific_jobs_submitted':0,'model_calls':0,'submission_digest':frozen['digest']}))


if __name__ == '__main__':
    main()
