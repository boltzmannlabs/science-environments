"""Controller integration with real subprocesses and explicitly synthetic evidence.

These tests validate execution/recovery contracts, never enzyme design or chemistry.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ENVIRONMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENVIRONMENT / 'runtime'))
from controller import Controller, initialize, check_poll_response
from contracts import GROUPS, object_hash
from test_assessment import assessment_fixture
from reporting import write_bundle


FIXTURE_SCRIPT = r'''
import hashlib,json,sys
from pathlib import Path
task=json.loads(Path(sys.argv[1]).read_text())
response_path=Path(sys.argv[2]); role=sys.argv[3]
fixture_dir=Path(sys.argv[4]); mode=sys.argv[5]
bundle=json.loads((fixture_dir/'bundle.json').read_text())
root=Path(task['run_dir']); stage=task['stage']
with (root/'fixture_calls.jsonl').open('a') as f:
    f.write(json.dumps({'role':role,'stage':stage,'mode':task.get('mode'),
                        'condition':task['condition']})+'\n')
usage={'external_cpu_core_hours':0,'gpu_hours':0,'service_spend_usd':0}
question_modes={'routine_question','misclassified_question','essential_question',
                'access_question','persistent_question'}
asking=mode in question_modes and (not (root/'repair_complete').exists() or mode=='persistent_question')
input_request=None
if mode in {'misclassified_question','essential_question','access_question'}:
    access=mode=='access_question'
    input_request={
        'reason_code':('required_access_or_resources_outside_existing_authorization' if access
                       else 'essential_goal_or_reaction_ambiguity_unresolvable_from_evidence'),
        'item':('pH' if mode=='misclassified_question' else 'tool_access' if access else 'substrate'),
        'question':'Synthetic unresolved input question',
        'why_unresolved':'Synthetic evidence cannot resolve this explicit choice or access boundary',
        'resolution_attempts':[{'source':'synthetic request and policy',
                                'finding':'Two incompatible alternatives or unavailable required access'}]}
if mode=='approval_reviewer' and role=='reviewer' or mode=='approval_repair' and role=='repair':
    result={'status':'blocked','artifacts':[],'usage':usage,
            'failure':{'category':'execution_approval','message':'Synthetic gate timeout',
                       'blocked_command':['synthetic-never-executed'], 'approval_request_id':'fixture-only'}}
elif role=='repair':
    if task.get('mode')=='reconcile':
        receipt_path=Path(task['interrupted_call']['directory'])/'receipt.json'
        receipt=json.loads(receipt_path.read_text())
        result={'status':'reconciled','safe_to_retry':True,'job_handles':[],
                'completed_response':receipt['response'],'usage':usage,
                'artifacts':[{'path':str(receipt_path),
                    'sha256':hashlib.sha256(receipt_path.read_bytes()).hexdigest()}]}
    else:
        (root/'repair_complete').write_text('software fixture repaired')
        result={'status':'repaired','summary':'Software-only adapter correction',
                'artifacts':[],'usage':usage}
elif role=='reviewer':
    decision='accept'
    if (mode=='sequence_only' or mode.startswith('independent_')) and stage=='generate': decision='accept_sequence_only'
    if mode=='repair_once' and not (root/'repair_complete').exists(): decision='repair'
    if mode=='approval_repair': decision='repair'
    if mode=='blocked_chemistry' and stage=='chemistry': decision='blocked'
    if mode=='technical_reject': decision='reject'
    if asking: decision='needs_input'
    result={'decision':decision,'reason':'Synthetic controller test decision, not science',
            'reviewed_sha256':task['output_sha256'],'usage':usage}
    if input_request: result['input_request']=input_request
else:
    if mode=='approval_block':
        result={'status':'blocked','artifacts':[],'usage':usage,
                'failure':{'category':'execution_approval','message':'Synthetic tool-gate timeout; command did not run',
                           'blocked_command':['synthetic-never-executed'], 'approval_request_id':'fixture-only'}}
    elif asking:
        result={'status':'needs_input','artifacts':[],'usage':usage,
                'failure':{'category':'routine_setting','message':'Synthetic unresolved setting'}}
        if input_request: result['input_request']=input_request
    elif mode=='repair_once' and stage=='prepare' and not (root/'repair_complete').exists():
        result={'status':'failed','artifacts':[], 'usage':usage,
                'failure':{'category':'technical','message':'Deliberate recoverable fixture error'}}
    elif mode=='technical_reject':
        result={'status':'failed','artifacts':[],'usage':usage,
                'failure':{'category':'technical','message':'No design work executed'}}
    elif mode.startswith('pending_') and stage=='generate' and task.get('mode')!='poll':
        result={'status':'pending','artifacts':[],'usage':usage,
                'job_handles':[{'provider':'software_fixture','id':'test_job_1'}]}
    elif (mode=='pending_once' and stage=='generate' and task.get('mode')=='poll'
          and not (root/'poll_failed').exists()):
        (root/'poll_failed').write_text('transient local transport failure')
        sys.exit(7)
    elif mode=='blocked_chemistry' and stage=='chemistry':
        result={'status':'blocked','artifacts':[], 'usage':usage,
                'failure':{'category':'capability','message':'No scientific chemistry backend in a software test'}}
    else:
        candidate_ref=bundle['candidate_manifest']
        if mode=='changed_candidate' and stage=='sequence_screen':
            candidates=json.loads(Path(candidate_ref['path_or_uri']).read_text())
            candidate=candidates['candidates'][0]
            seq_path=response_path.parent/'changed_sequence.fasta'
            seq_path.write_text('>software_changed\nACE\n')
            candidate['sequence']={'path':str(seq_path),
                'sha256':hashlib.sha256(seq_path.read_bytes()).hexdigest()}
            candidate['revision']=2
            manifest_path=response_path.parent/'changed_candidates.json'
            manifest_path.write_text(json.dumps(candidates))
            candidate_ref={'kind':'candidate_manifest','path':str(manifest_path),
                'sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest()}
        if stage=='prepare': artifacts=bundle['prepare']
        elif stage=='generate':
            artifacts=[candidate_ref]
            if mode in {'sequence_only','wrong_full_accept'} or mode.startswith('independent_'):
                scope_path=response_path.parent/'generation_scope.json'
                scope_path.write_text(json.dumps({'geometry_status':'unresolved',
                    'sequence_only_eligible':True,'note':'software-only fixture; no structural certification'}))
                artifacts.append({'kind':'stage_report','path':str(scope_path),
                    'sha256':hashlib.sha256(scope_path.read_bytes()).hexdigest()})
        elif stage=='evaluate': artifacts=[bundle['evaluation']]
        else:
            evidence_path=response_path.parent/'stage_evidence.json'
            evidence={'stage':stage,
                'candidate_manifest_sha256':candidate_ref['sha256'],'checks':[
                {'rule_id':'software_fixture','status':'UNRESOLVED',
                 'reason':'No molecular calculation runs in controller tests'}]}
            if mode.startswith('independent_') and stage=='fold':
                evidence.update(assessment_models=bundle['assessment_models'],structural_integrity_ready=True)
            if mode.startswith('independent_') and stage not in {'sequence_screen','fold'}:
                evidence['assessment_models_sha256']=hashlib.sha256(json.dumps(
                    bundle['assessment_models'],sort_keys=True,allow_nan=False).encode()).hexdigest()
                if mode=='independent_stale_downstream': evidence['assessment_models_sha256']='0'*64
            evidence_path.write_text(json.dumps(evidence))
            artifacts=[candidate_ref,{
                'kind':'stage_evidence','path':str(evidence_path),
                'sha256':hashlib.sha256(evidence_path.read_bytes()).hexdigest()}]
        if mode=='invalid_hash' and stage=='prepare':
            artifacts=[dict(a) for a in artifacts]
            artifacts[0]['sha256']='0'*64
        if mode=='override_frozen' and stage=='sequence_screen':
            artifacts.append(bundle['prepare'][0])
        result={'status':'completed','summary':'Software-only stage output',
                'artifacts':artifacts,'usage':usage,'job_handles':[]}
if role=='executor' and task.get('mode')=='poll':
    result['polled_job_handles']=task['job_handles']
    if mode=='pending_approval_block':
        result={'status':'blocked','artifacts':[],'usage':usage,'job_handles':[],
                'failure':{'category':'execution_approval','message':'Synthetic polling approval timeout',
                           'blocked_command':['synthetic-read-only-poll']}}
    if mode=='pending_wrong_job':
        result['polled_job_handles']=[{'provider':'software_fixture','id':'different_job'}]
    if mode=='pending_wrong_provider':
        result['polled_job_handles']=[{'provider':'different_provider','id':'test_job_1'}]
    if mode=='pending_missing_receipt':
        result.pop('polled_job_handles')
response_path.write_text(json.dumps(result))
'''


class ControllerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / 'fixture'
        self.fixture.mkdir()
        self.script = self.fixture / 'harness.py'
        self.script.write_text(FIXTURE_SCRIPT)
        self.make_bundle()

    def artifact(self, name, content, kind=None):
        path = self.fixture / name
        path.write_text(content if isinstance(content, str) else json.dumps(content))
        ref = {'path_or_uri': str(path),
               'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'description': 'SOFTWARE TEST ONLY; no scientific qualification'}
        return {**ref, 'kind': kind} if kind else ref

    def config(self, mode='late_unresolved'):
        return {'backend': 'command', 'argv': [sys.executable, str(self.script),
                '{task_file}', '{response_file}', '{role}', str(self.fixture), mode]}

    def create_run(self, mode='late_unresolved', policy=None, condition='agent_selected', name='run'):
        run = self.root / name
        initialize(run, 'SOFTWARE TEST ONLY: exercise a fictional workflow', [],
                   self.config(mode), {'active_seconds': 90, 'call_timeout_seconds': 5,
                                      'poll_seconds': 0, **(policy or {})}, condition)
        return run

    def calls(self, run):
        path = run / 'fixture_calls.jsonl'
        return [json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []

    def make_bundle(self, request_budget=None):
        evidence = self.artifact('software_evidence.txt', 'Software fixture, not molecular evidence.')
        request = json.loads((ENVIRONMENT / 'tasks/request.example.json').read_text())
        request['task_id'] = 'software_controller_fixture'
        request['constraints']['length'] = {'min': 3, 'max': 3}
        request['execution'].update(final_count=1, max_generated=1, max_chemistry_candidates=1,
                                    max_refinements_per_lineage=0)
        request['execution']['budget'] = request_budget or {'wall_time_hours': 2, 'cpu_core_hours': 16, 'gpu_hours': 1}
        generation = {
            'schema_version': '1.1', 'request_sha256': object_hash(request),
            'profile_id': 'software_fixture', 'version': 'test-only',
            'status': 'ready', 'reaction': evidence, 'motif': evidence, 'motif_map': evidence,
            'generator_conditions': evidence, 'generation_constraints': evidence,
            'tool_lock': [{'tool_id': 'software_fixture', 'code_commit': 'a' * 40,
                           'model_weights': [], 'dataset_snapshots': [],
                           'license_access_record': evidence}],
            'readiness_evidence': [evidence],
            'assembly': {'kind': 'monomer', 'subunit_count': 1, 'unique_sequence_count': 1,
                         'sequence_groups': [{'sequence_id': 'test_sequence', 'chain_ids': ['A']}],
                         'reference_assembly': evidence, 'chain_map': evidence,
                         'assembly_evidence': [evidence], 'design_symmetry': 'C1',
                         'active_sites': [{'site_id': 'test_site', 'chain_ids': ['A'],
                                           'catalytic_map': evidence}],
                         'generation_state_policy': evidence},
        }
        plan = {'required_groups': sorted(GROUPS), 'calibration_basis': 'reference_controls_only',
                'target_objective': 'SOFTWARE TEST ONLY', 'request_sha256': object_hash(request)}
        sequence = self.artifact('software_sequence.fasta', '>software_only\nACD\n')
        structure = self.artifact('software_structure.pdb',
                                  'REMARK SOFTWARE TEST ONLY, NOT A MOLECULAR MODEL\nEND\n')
        candidate = {'candidate_id': 'software_candidate', 'revision': 1,
                     'generation_kind': 'de_novo', 'sequence_designed': True,
                     'status': 'exploratory', 'sequence': sequence, 'structure': structure}
        self.bundle = {
            'prepare': [self.artifact('request.json', request, 'resolved_request'),
                        self.artifact('generation.json', generation, 'generation_profile'),
                        self.artifact('evaluation_plan.json', plan, 'evaluation_plan')],
            'candidate_manifest': self.artifact('candidates.json', {'candidates': [candidate]},
                                                'candidate_manifest'),
            'stage_evidence': self.artifact('stage_evidence.json',
                {'scope': 'software fixture only', 'chemistry': 'UNRESOLVED'}, 'stage_evidence'),
            'evaluation': self.artifact('evaluation.json',
                {'qualification_requested': False, 'candidates': [],
                 'evaluation_plan_sha256': hashlib.sha256((self.fixture/'evaluation_plan.json').read_bytes()).hexdigest(),
                 'unresolved': ['No chemistry calculation exists in this software fixture.']},
                'evaluation'),
        }
        self.bundle['assessment_models'] = [assessment_fixture(self.fixture, candidate,
                                                  self.bundle['prepare'][2]['sha256'])]
        (self.fixture / 'bundle.json').write_text(json.dumps(self.bundle))

    def test_automatic_repair_and_resume_preserve_accepted_work_and_budget(self):
        run = self.create_run('repair_once', condition='tools_specified')
        first = Controller(run).run(max_stages=1)
        state = json.loads((run / 'state.json').read_text())
        self.assertEqual(state['stages']['prepare']['status'], 'accepted', first)
        calls = self.calls(run)
        self.assertEqual(sum(c['role'] == 'executor' and c['stage'] == 'prepare' for c in calls), 2)
        self.assertEqual(sum(c['role'] == 'repair' for c in calls), 1)
        self.assertTrue(all(c['condition'] == 'tools_specified' for c in calls))
        spent = state['usage']['active_seconds']
        self.assertGreater(spent, 0)
        Controller(run).run(max_stages=1)
        state2 = json.loads((run / 'state.json').read_text())
        calls2 = self.calls(run)
        self.assertEqual(sum(c['role'] == 'executor' and c['stage'] == 'prepare' for c in calls2), 2)
        self.assertEqual(state2['stages']['generate']['status'], 'accepted')
        self.assertGreater(state2['usage']['active_seconds'], spent)
        self.assertEqual(state['policy_sha256'], state2['policy_sha256'])

    def test_reviewer_acceptance_cannot_waive_invalid_artifact_hash(self):
        run = self.create_run('invalid_hash')
        result = Controller(run).run()
        self.assertEqual(result['qualified_design_count'], 0)
        self.assertNotEqual(json.loads((run / 'state.json').read_text())['stages']['prepare']['status'], 'accepted')
        self.assertFalse(any(c['stage'] == 'generate' for c in self.calls(run)))

    def test_profile_from_another_request_cannot_dispatch_generation(self):
        path = self.fixture / 'generation.json'
        generation = json.loads(path.read_text())
        generation['request_sha256'] = '0' * 64
        self.bundle['prepare'][1] = self.artifact('generation.json', generation, 'generation_profile')
        (self.fixture / 'bundle.json').write_text(json.dumps(self.bundle))
        run = self.create_run('normal')
        result = Controller(run).run()
        self.assertEqual(result['qualified_design_count'], 0)
        self.assertFalse(any(c['stage'] == 'generate' for c in self.calls(run)))
        self.assertIn('different resolved request', (run / 'trajectory.jsonl').read_text())

    def test_routine_questions_return_to_internal_resolution_then_continue(self):
        for mode in ('routine_question', 'misclassified_question'):
            with self.subTest(mode=mode):
                run = self.root / mode
                initialize(run, 'SOFTWARE TEST ONLY', [], self.config(mode),
                           {'active_seconds': 90, 'call_timeout_seconds': 5, 'poll_seconds': 0})
                result = Controller(run).run(max_stages=2)
                self.assertEqual(result['status'], 'READY', result)
                self.assertEqual(result['stages']['generate'], 'accepted', result)
                self.assertEqual(sum(c['role'] == 'repair' for c in self.calls(run)), 1)
                events = [json.loads(line) for line in (run / 'trajectory.jsonl').read_text().splitlines()]
                self.assertTrue(any(e['kind'] == 'user_question_redirected' for e in events))
                self.assertNotIn('input_request', result)

    def test_essential_intent_and_access_boundaries_remain_user_questions(self):
        for mode in ('essential_question', 'access_question'):
            with self.subTest(mode=mode):
                run = self.root / mode
                initialize(run, 'SOFTWARE TEST ONLY: unresolved alternatives', [], self.config(mode),
                           {'active_seconds': 90, 'call_timeout_seconds': 5, 'poll_seconds': 0})
                result = Controller(run).run()
                self.assertEqual(result['status'], 'NEEDS_INPUT', result)
                self.assertIn(result['input_request']['item'], ('substrate', 'tool_access'))
                self.assertFalse(any(c['role'] == 'repair' or c['stage'] == 'generate'
                                     for c in self.calls(run)))

    def test_repeated_routine_question_exhausts_repair_without_escalating_to_user(self):
        run = self.create_run('persistent_question', policy={'max_repairs_per_stage': 1})
        result = Controller(run).run()
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertNotIn('input_request', result)
        self.assertEqual(sum(c['role'] == 'repair' for c in self.calls(run)), 1)
        self.assertEqual(result['qualified_design_count'], 0)

    def test_late_chemistry_gap_returns_partial_after_eligible_stages(self):
        for mode in ('late_unresolved', 'blocked_chemistry'):
            with self.subTest(mode=mode):
                run = self.root / mode
                initialize(run, 'SOFTWARE TEST ONLY', [], self.config(mode),
                           {'active_seconds': 90, 'call_timeout_seconds': 5, 'poll_seconds': 0})
                result = Controller(run).run()
                self.assertEqual(result['status'], 'PARTIAL', result)
                self.assertEqual(result['qualified_design_count'], 0)
                bundle = run / '08_results'
                for name in ('designed_sequences.fasta', 'assemblies.json', 'shortlist.csv',
                             'evaluation.json', 'report.md', 'manifest.json', 'trajectory.jsonl'):
                    self.assertTrue((bundle / name).is_file(), name)
                self.assertEqual((bundle / 'designed_sequences.fasta').read_text(), '')
                self.assertEqual(json.loads((bundle / 'evaluation.json').read_text())['status'], 'PARTIAL')
                calls = self.calls(run)
                self.assertTrue(any(c['stage'] == 'generate' and c['role'] == 'executor' for c in calls))
                self.assertTrue(any(c['stage'] == 'chemistry' and c['role'] == 'executor' for c in calls))
                if mode == 'late_unresolved':
                    self.assertTrue(any(c['stage'] == 'evaluate' and c['role'] == 'executor' for c in calls))

    def test_expired_deadline_prevents_dispatch_and_resume_does_not_renew_it(self):
        run = self.create_run(policy={'deadline_utc': '2000-01-01T00:00:00+00:00'})
        for _ in range(2):
            result = Controller(run).run()
            self.assertEqual(result['status'], 'BUDGET_EXHAUSTED', result)
            self.assertEqual(self.calls(run), [])
        state = json.loads((run / 'state.json').read_text())
        self.assertEqual(state['usage']['active_seconds'], 0)
        self.assertEqual(state['policy']['deadline_utc'], '2000-01-01T00:00:00+00:00')

    def test_pending_poll_transport_failure_recovers_without_resubmitting(self):
        run = self.create_run('pending_once', policy={'max_pending_polls': 3})
        result = Controller(run).run(max_stages=2)
        state = json.loads((run / 'state.json').read_text())
        self.assertEqual(state['stages']['generate']['status'], 'accepted', result)
        calls = [c for c in self.calls(run) if c['stage'] == 'generate' and c['role'] == 'executor']
        self.assertEqual(sum(c['mode'] == 'execute' for c in calls), 1)
        self.assertEqual(sum(c['mode'] == 'poll' for c in calls), 2)
        self.assertEqual(state['stages']['generate']['attempts'], 1)

    def test_changed_nested_reference_blocks_next_scientific_dispatch(self):
        run = self.create_run()
        Controller(run).run(max_stages=1)
        (self.fixture / 'software_evidence.txt').write_text('CHANGED nested reference after readiness review')
        result = Controller(run).run(max_stages=1)
        self.assertEqual(result['qualified_design_count'], 0)
        self.assertFalse(any(c['stage'] == 'generate' for c in self.calls(run)), result)

    def test_wrong_or_missing_poll_identity_retains_original_job_without_resubmitting(self):
        for mode in ('pending_wrong_job', 'pending_wrong_provider', 'pending_missing_receipt'):
            with self.subTest(mode=mode):
                run = self.create_run(mode, name=mode)
                result = Controller(run).run(max_stages=2)
                self.assertNotEqual(result['stages']['generate'], 'accepted')
                self.assertEqual(result['outstanding_jobs']['generate'],
                                 [{'provider': 'software_fixture', 'id': 'test_job_1'}])
                calls = [c for c in self.calls(run) if c['stage'] == 'generate' and c['role'] == 'executor']
                self.assertEqual([c['mode'] for c in calls], ['execute', 'poll'])
                self.assertIn('poll_receipt_rejected', (run/'trajectory.jsonl').read_text()
                              + (run/'state.json').read_text())

    def test_partial_poll_batch_cannot_drop_or_replace_an_original_job(self):
        handles = [{'provider': 'fixture', 'id': 'a'}, {'provider': 'fixture', 'id': 'b'}]
        check_poll_response(handles, {'status': 'pending', 'polled_job_handles': handles,
                                      'job_handles': list(reversed(handles))})
        for remaining in ([], handles[:1], [*handles, {'provider': 'fixture', 'id': 'c'}]):
            with self.subTest(remaining=remaining), self.assertRaises(ValueError):
                check_poll_response(handles, {'status': 'pending', 'polled_job_handles': handles,
                                              'job_handles': remaining})
        with self.assertRaises(ValueError):
            check_poll_response(handles, {'status': 'completed', 'polled_job_handles': handles,
                                          'job_handles': handles})

    def test_poll_approval_timeout_cannot_clear_original_remote_handles(self):
        run = self.create_run('pending_approval_block')
        result = Controller(run).run(max_stages=2)
        self.assertEqual(result['outstanding_jobs']['generate'],
                         [{'provider': 'software_fixture', 'id': 'test_job_1'}])
        self.assertIn('EXECUTION_APPROVAL_REQUIRED', result['reason'])
        calls = [c for c in self.calls(run) if c['stage'] == 'generate']
        self.assertEqual([(c['role'], c['mode']) for c in calls], [('executor', 'execute'), ('executor', 'poll')])

    def test_saved_poll_receipt_recovery_enforces_original_job_identity(self):
        for mode, accepted in (('pending_valid', True), ('pending_wrong_job', False)):
            with self.subTest(mode=mode):
                run = self.create_run(mode, name=mode)
                controller = Controller(run)
                handles = [{'provider': 'software_fixture', 'id': 'test_job_1'}]
                pending = {'status': 'pending', 'job_handles': handles}
                controller.state['stages']['generate'].update(
                    status='running', response=pending, job_handles=handles)
                # Save an actual subprocess receipt, then simulate restart before
                # applying that receipt to the stage or acknowledging the call.
                controller.call('executor', controller.task('generate', 'poll', job_handles=handles))
                recovered = Controller(run)
                self.assertEqual(recovered.reconcile(), accepted)
                stage = recovered.state['stages']['generate']
                self.assertEqual(stage['job_handles'], [] if accepted else handles)
                self.assertEqual(stage['response']['status'], 'completed' if accepted else 'pending')
                self.assertIsNone(recovered.state['inflight'])
                self.assertEqual(len(self.calls(run)), 1)

    def test_technical_rejection_is_not_a_completed_negative_design_experiment(self):
        run = self.create_run('technical_reject')
        result = Controller(run).run()
        self.assertEqual(result['status'], 'BLOCKED', result)
        self.assertEqual(result['qualified_design_count'], 0)

    def test_interrupt_after_worker_receipt_does_not_resubmit_completed_work(self):
        run = self.create_run()

        class CrashAfterReceipt(Controller):
            def event(self, kind, **details):
                super().event(kind, **details)
                if kind == 'agent_finished' and details.get('role') == 'executor':
                    raise SystemExit('Injected interruption after a real subprocess returned')

        with self.assertRaises(SystemExit):
            CrashAfterReceipt(run).run(max_stages=1)
        result = Controller(run).run(max_stages=1)
        state = json.loads((run / 'state.json').read_text())
        self.assertEqual(state['stages']['prepare']['status'], 'accepted', result)
        self.assertEqual(sum(c['role'] == 'executor' and c['stage'] == 'prepare'
                             for c in self.calls(run)), 1,
                         'A persisted completed worker receipt must be recovered instead of resubmitted')

    def test_later_stage_cannot_override_frozen_inputs_or_change_canonical_candidate(self):
        for mode in ('override_frozen', 'changed_candidate'):
            with self.subTest(mode=mode):
                run = self.root / mode
                initialize(run, 'SOFTWARE TEST ONLY', [], self.config(mode),
                           {'active_seconds': 90, 'call_timeout_seconds': 5, 'poll_seconds': 0})
                result = Controller(run).run()
                state = json.loads((run / 'state.json').read_text())
                self.assertEqual(result['qualified_design_count'], 0)
                self.assertEqual(state['stages']['generate']['status'], 'accepted')
                self.assertNotEqual(state['stages']['sequence_screen']['status'], 'accepted')
                self.assertFalse(any(c['stage'] == 'fold' for c in self.calls(run)), result)

    def test_stricter_resolved_request_budget_prevents_further_dispatch(self):
        # The accepted request cannot enlarge the policy or silently lose a
        # stricter user limit. Tiny CPU quota is a deterministic software test.
        self.make_bundle({'wall_time_hours': 2, 'cpu_core_hours': 1e-9, 'gpu_hours': 1})
        run = self.create_run()
        result = Controller(run).run()
        self.assertEqual(result['status'], 'BUDGET_EXHAUSTED', result)
        self.assertFalse(any(c['stage'] == 'generate' for c in self.calls(run)), result)

    def test_documented_geometry_defect_cannot_be_accepted_as_full_structure(self):
        run = self.create_run('wrong_full_accept', policy={'max_repairs_per_stage': 1})
        result = Controller(run).run()
        self.assertEqual(result['qualified_design_count'], 0)
        self.assertNotEqual(result['stages']['generate'], 'accepted')
        self.assertFalse(any(c['stage']=='sequence_screen' for c in self.calls(run)))
        self.assertIn('Documented geometry defect', (run/'trajectory.jsonl').read_text())

    def test_sequence_only_generation_can_screen_without_promoting_bad_structure(self):
        run = self.create_run('sequence_only', policy={'max_repairs_per_stage': 1})
        checkpoint = Controller(run).run(max_stages=3)
        self.assertEqual(checkpoint['status'], 'READY', checkpoint)
        self.assertEqual(checkpoint['stages']['generate'], 'accepted_sequence_only')
        self.assertEqual(checkpoint['stages']['sequence_screen'], 'accepted')
        self.assertFalse(any(c['stage']=='fold' for c in self.calls(run)))
        result = Controller(run).run()
        self.assertEqual(result['status'], 'PARTIAL', result)
        self.assertEqual(result['qualified_design_count'], 0)
        self.assertEqual(result['stages']['sequence_screen'], 'accepted')
        self.assertNotEqual(result['stages']['fold'], 'accepted')
        self.assertFalse(any(c['stage']=='aggregation' for c in self.calls(run)))
        self.assertIn('structural preparation', (run/'trajectory.jsonl').read_text())

    def test_independent_sequence_fold_advances_with_a_separate_reviewed_model(self):
        run = self.create_run('independent_fold')
        result = Controller(run).run()
        self.assertEqual(result['status'], 'PARTIAL', result)
        self.assertEqual(result['stages']['generate'], 'accepted_sequence_only')
        self.assertEqual(result['stages']['fold'], 'accepted')
        self.assertEqual(result['stages']['chemistry'], 'accepted')
        self.assertEqual(result['qualified_design_count'], 0)
        models = json.loads((run/'08_results/assessment_models.json').read_text())['models']
        self.assertEqual(models, self.bundle['assessment_models'])
        self.assertIn('NOT A MOLECULAR MODEL', (self.fixture/'software_structure.pdb').read_text())
        self.assertFalse((run/'08_results/designed_sequences.fasta').read_text())

    def test_downstream_cannot_switch_reviewed_coordinate_versions(self):
        run = self.create_run('independent_stale_downstream', policy={'max_repairs_per_stage': 1})
        result = Controller(run).run()
        self.assertEqual(result['stages']['fold'], 'accepted', result)
        self.assertNotEqual(result['stages']['aggregation'], 'accepted')
        self.assertFalse(any(c['stage'] == 'complex' for c in self.calls(run)))
        self.assertIn('not bound to the reviewed assessment models', (run/'trajectory.jsonl').read_text())
        self.assertNotIn('running', result['stages'].values())

    def test_result_export_uses_reviewed_model_and_preserves_generated_provenance(self):
        # Explicitly synthetic export fixture, not a qualified controller outcome.
        run = self.create_run('independent_fold')
        summary = Controller(run).run(max_stages=4)
        state = json.loads((run/'state.json').read_text())
        model = self.bundle['assessment_models'][0]
        original = json.loads((self.fixture/'candidates.json').read_text())
        candidate = original['candidates'][0]
        candidate['assembly_map'] = self.artifact('synthetic_map.json', {
            'candidate_id': candidate['candidate_id'], 'synthetic_only': True,
            'structure_sha256': model['structure']['sha256']})
        summary['artifacts']['candidate_manifest'] = self.artifact('export_manifest.json', original, 'candidate_manifest')
        summary['qualified_candidates'] = [candidate['candidate_id']]
        summary['reason'] = 'Synthetic exporter test only; no scientific qualification'
        write_bundle(run, state, summary)
        assembly = json.loads((run/'08_results/assemblies.json').read_text())['assemblies'][0]
        exported = run/'08_results'/assembly['structure']
        self.assertEqual(hashlib.sha256(exported.read_bytes()).hexdigest(), model['structure']['sha256'])
        self.assertEqual(assembly['generated_structure'], candidate['structure'])
        self.assertNotEqual(assembly['structure_sha256'], candidate['structure']['sha256'])
        # Re-exporting identical evidence is idempotent; invalidation archives the
        # old bundle and removes stale structures/chemistry from current results.
        old_bytes = exported.read_bytes()
        write_bundle(run, state, summary)
        self.assertFalse((run/'result_history').exists())
        summary['qualified_candidates'] = []
        summary['reason'] = 'Synthetic evidence invalidation'
        write_bundle(run, state, summary)
        self.assertFalse((run/'08_results/structures').exists())
        self.assertFalse((run/'08_results/chemistry').exists())
        self.assertEqual((run/'08_results/designed_sequences.fasta').read_text(), '')
        histories = list((run/'result_history').iterdir())
        self.assertEqual(len(histories), 1)
        self.assertEqual((histories[0]/assembly['structure']).read_bytes(), old_bytes)
        self.assertEqual(json.loads((histories[0]/'SUPERSEDED.json').read_text())['status'], 'SUPERSEDED')
        self.assertTrue((histories[0]/'chemistry/evidence.json').is_file())
        write_bundle(run, state, summary)
        self.assertEqual(list((run/'result_history').iterdir()), histories)

    def test_changed_prediction_evidence_cannot_be_reused_after_restart(self):
        run = self.create_run('independent_fold', policy={'max_repairs_per_stage': 1})
        self.assertEqual(Controller(run).run(max_stages=4)['stages']['fold'], 'accepted')
        (self.fixture/'raw_prediction_fixture.txt').write_text('changed historical result')
        result = Controller(run).run()
        self.assertNotEqual(result['stages']['fold'], 'accepted')
        self.assertFalse(any(c['stage'] == 'aggregation' for c in self.calls(run)))

    def test_stopped_controller_retains_remote_uncertainty_without_running_label(self):
        run = self.create_run()
        controller = Controller(run)
        item = controller.state['stages']['generate']
        item.update(status='running', job_handles=[{'provider': 'fixture', 'id': 'not-a-real-job'}])
        result = controller.finish('PARTIAL', 'Synthetic stopped-controller regression')
        self.assertEqual(result['stages']['generate'], 'awaiting_reconciliation')
        self.assertEqual(result['outstanding_jobs']['generate'], item['job_handles'])
        self.assertFalse(any(c['role'] == 'executor' for c in self.calls(run)))

    def test_execution_gate_denial_never_dispatches_repair_or_an_alternate_launch(self):
        for mode, roles in [('approval_block', ['executor']),
                            ('approval_reviewer', ['executor', 'reviewer']),
                            ('approval_repair', ['executor', 'reviewer', 'repair'])]:
            with self.subTest(mode=mode):
                run = self.root / mode
                initialize(run, 'SOFTWARE TEST ONLY: execution approval boundary', [], self.config(mode),
                           {'active_seconds': 90, 'call_timeout_seconds': 5, 'poll_seconds': 0})
                result = Controller(run).run()
                self.assertEqual(result['status'], 'BLOCKED', result)
                self.assertEqual([c['role'] for c in self.calls(run)], roles)
                self.assertEqual(result['execution_approval_block']['failure']['approval_request_id'], 'fixture-only')
                self.assertIn('EXECUTION_APPROVAL_REQUIRED', result['reason'])
                self.assertEqual(Controller(run).run(), result)
                self.assertEqual([c['role'] for c in self.calls(run)], roles)


if __name__ == '__main__':
    unittest.main()
