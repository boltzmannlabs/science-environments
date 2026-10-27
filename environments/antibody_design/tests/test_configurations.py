"""Synthetic configuration checks for all profiles; no scientific acceptance claims."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import ValidationError
from referencing.exceptions import NoSuchResource

from contract_io import read_json, sha256
from schema_registry import ROOT, config_path, environment_config, schema_registry, validator_for_path
from task_contracts import task_profile, validate_task_contract

TARGET = 'mab_target_only_design'
BISPECIFIC = 'bispecific_antibody_design'
READOUT = 'bispecific_cns_readout_comparison'


def example(task):
    profile = task_profile(task)
    value = read_json(ROOT / profile.get('request_example', 'config/monoclonal_reference/denv.request.example.json'))
    if 'variant' in profile:
        value['variant'] = profile['variant']
    return value


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def result_pair(self, task=READOUT):
        request = example(task)
        path = self.root / 'request.json'
        path.write_text(json.dumps(request))
        result = dict(schema_version='1.0', task_id=task, status='NEEDS_INPUT',
                      request_sha256=sha256(path), answer=None, evidence=[], report=None,
                      missing_requirements=['datasets not supplied'], limitations=[],
                      validation_scope='declared_contract_only')
        return result, path

    def artifact(self):
        path = self.root / 'evidence.txt'
        path.write_text('Synthetic data-contract fixture; no scientific evidence.\n')
        return dict(path=path.name, sha256=sha256(path), media_type='text/plain', source='synthetic test')

    def assessed(self):
        result, path = self.result_pair()
        result.update(status='ASSESSED', missing_requirements=[], evidence=[self.artifact()],
                      report=self.artifact(), answer=dict(construct='CD98hc_shuttle',
                      governing_readout='capillary_depletion', brain_concentration_fold_change=1))
        return result, path

    def test_every_profile_routes_its_example(self):
        profiles = environment_config()['task_profiles']
        self.assertEqual(len(profiles), 9)
        for task in profiles:
            with self.subTest(task=task):
                report = validate_task_contract(example(task), task)
                self.assertEqual(report['status'], 'CONTRACT_VALID')
                self.assertFalse(report['artifacts_checked'])
                self.assertIn('not a readiness result', report['scope'])

    def test_unknown_tasks_and_config_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown task'):
            validate_task_contract({}, 'unknown')
        with self.assertRaisesRegex(ValueError, 'escapes'):
            config_path('../README.md')

    def test_external_schema_resolution_has_no_network_fallback(self):
        with self.assertRaises(NoSuchResource):
            schema_registry().get_or_retrieve('https://example.invalid/unregistered.schema.json')

    def test_family_mismatch_rejected(self):
        with self.assertRaises(ValidationError):
            validate_task_contract(example(TARGET), BISPECIFIC)
        value = example(TARGET)
        value['antibody']['reference'] = example('mab_reference_guided_design')['antibody']['reference']
        with self.assertRaises(ValidationError):
            validate_task_contract(value, TARGET)

    def test_denv_variant_must_match_profile(self):
        with self.assertRaisesRegex(ValueError, 'variant'):
            validate_task_contract(example('denv_antibody_001'), 'denv_antibody_001_tools')

    def test_target_only_library_requires_source(self):
        value = example(TARGET)
        value['discovery']['candidate_origin'] = 'supplied_library'
        with self.assertRaisesRegex(ValueError, 'source artifacts'):
            validate_task_contract(value, TARGET)
        value['discovery']['source_artifacts'] = [self.artifact()]
        validate_task_contract(value, TARGET)

    def test_target_only_budget_and_domains(self):
        value = example(TARGET)
        value['evaluation']['requested_count'] = 2
        with self.assertRaisesRegex(ValueError, 'budget'):
            validate_task_contract(value, TARGET)
        value = example(TARGET)
        value['evaluation']['required_evidence_domains'].remove('specificity')
        with self.assertRaisesRegex(ValueError, 'evidence domains'):
            validate_task_contract(value, TARGET)

    def test_biparatopic_same_target_and_flexible_chain_count(self):
        value = example(BISPECIFIC)
        self.assertEqual(len(value['targets']), 1)
        for count in [1, 2, 5]:
            changed = deepcopy(value)
            for index in range(1, count):
                chain = deepcopy(changed['architecture']['chains'][0])
                chain['chain_id'] = f'chain-{index}'
                changed['architecture']['chains'].append(chain)
            validate_task_contract(changed, BISPECIFIC)

    def test_bispecific_duplicate_and_unknown_identifiers(self):
        for field in ['target_id', 'chain_ids', 'arm_id', 'epitope_id']:
            value = example(BISPECIFIC)
            arms = value['architecture']['arms']
            arms[1][field] = {'target_id': 'missing', 'chain_ids': ['missing'],
                              'arm_id': arms[0]['arm_id'], 'epitope_id': arms[0]['epitope_id']}[field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_task_contract(value, BISPECIFIC)

    def test_joint_evidence_required_only_when_declared(self):
        value = example(BISPECIFIC)
        value['mechanism']['simultaneous_engagement'] = 'required'
        with self.assertRaisesRegex(ValueError, 'joint evidence'):
            validate_task_contract(value, BISPECIFIC)
        value['evaluation']['required_evidence_domains'].append('joint_engagement')
        validate_task_contract(value, BISPECIFIC)

    def test_assessment_missing_datasets_are_explicit_null(self):
        value = example(READOUT)
        validate_task_contract(value, READOUT)
        del value['datasets']['microscopy']
        with self.assertRaises(ValidationError):
            validate_task_contract(value, READOUT)

    def test_fixed_comparison_candidates_cannot_be_replaced(self):
        value = example(READOUT)
        value['candidate_ids'][0] = 'another-candidate'
        with self.assertRaises(ValidationError):
            validate_task_contract(value, READOUT)

    def test_result_requires_exact_request_hash(self):
        value, request = self.result_pair()
        validate_task_contract(value, READOUT, 'result', request_path=request)
        with self.assertRaisesRegex(ValueError, 'requires --request'):
            validate_task_contract(value, READOUT, 'result')
        request.write_text(request.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            validate_task_contract(value, READOUT, 'result', request_path=request)

    def test_needs_input_cannot_claim_answer(self):
        value, path = self.result_pair()
        value['answer'] = self.assessed()[0]['answer']
        with self.assertRaises(ValidationError):
            validate_task_contract(value, READOUT, 'result', request_path=path)

    def test_assessed_requires_evidence_and_exact_answer_shape(self):
        value, path = self.assessed()
        validate_task_contract(value, READOUT, 'result', input_root=self.root, request_path=path)
        for patch in [{'evidence': []}, {'answer': dict(value['answer'], extra=True)},
                      {'answer': dict(value['answer'], brain_concentration_fold_change=0.5)},
                      {'answer': dict(value['answer'], governing_readout='unknown')}]:
            with self.subTest(patch=patch), self.assertRaises(ValidationError):
                validate_task_contract(dict(value, **patch), READOUT, 'result', request_path=path)

    def test_artifacts_reject_traversal_and_changed_contents(self):
        value, path = self.assessed()
        value['evidence'][0]['path'] = '../outside.txt'
        with self.assertRaisesRegex(ValueError, 'beneath'):
            validate_task_contract(value, READOUT, 'result', input_root=self.root, request_path=path)
        value, path = self.assessed()
        (self.root / 'evidence.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            validate_task_contract(value, READOUT, 'result', input_root=self.root, request_path=path)

    def test_cellular_answer_requires_two_distinct_known_sources(self):
        task = 'bispecific_cellular_mechanism_assessment'
        schema = validator_for_path(config_path(task_profile(task)['result_schema']))
        value, _ = self.result_pair(task)
        value.update(status='ASSESSED', missing_requirements=[], evidence=[self.artifact()], report=self.artifact(),
                     answer={'validity_assessment': 'insufficient_underpowered_single_rater_check',
                             'same_mechanism_baseline_sources': ['class_frequency_source_data_fig2ef',
                             'supplementary_annotation_crosscheck_dataset']})
        schema.validate(value)
        value['answer']['same_mechanism_baseline_sources'] *= 2
        with self.assertRaises(ValidationError):
            schema.validate(value)

    def test_cli_selects_profile_and_reports_scope(self):
        command = [sys.executable, str(ROOT / 'tests/task_contracts.py'),
                   str(ROOT / 'config/bispecific_design/request.example.json'), '--task', BISPECIFIC]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['status'], 'CONTRACT_VALID')
        completed = subprocess.run(command[:-1] + [TARGET], capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)

    def design_result(self, task):
        request = example(task)
        path = self.root / 'design-request.json'
        path.write_text(json.dumps(request))
        value = dict(schema_version='1.0', task_id=task, run_status='NEEDS_INPUT',
                     requested_count=1, records=[], shortlist=[], missing_requirements=['inputs'],
                     stop_reason='Synthetic fixture', provenance=dict(request_sha256=sha256(path),
                     protocol_sha256=None, scientific_execution=False, synthetic_fixture=True,
                     knowledge_cutoff=request['knowledge_cutoff']),
                     resources=dict(wall_time_minutes=0, cpu_core_hours=0, gpu_hours=0, remote_cost_units=0))
        if task == TARGET:
            value.update(design_mode='de_novo', sequence_scope='variable_domains', run_id='synthetic',
                         candidate_origins=[], assay_records=[])
        return value, request, path

    def test_design_failure_results_cannot_claim_completion(self):
        for task in [TARGET, BISPECIFIC]:
            value, request, path = self.design_result(task)
            validate_task_contract(value, task, 'result', request_path=path)
            for status in ['QUALIFIED', 'PARTIAL']:
                changed = dict(value, run_status=status)
                with self.subTest(task=task, status=status), self.assertRaises(ValueError):
                    validate_task_contract(changed, task, 'result', request_path=path)
            value['provenance']['knowledge_cutoff'] = '2020-01-01'
            with self.assertRaisesRegex(ValueError, 'Cutoff changed'):
                validate_task_contract(value, task, 'result', request_path=path)

    def test_target_only_origin_and_scope_remain_bound(self):
        value, request, path = self.design_result(TARGET)
        value['sequence_scope'] = 'full_length_chains'
        with self.assertRaisesRegex(ValueError, 'scope changed'):
            validate_task_contract(value, TARGET, 'result', request_path=path)
        value['sequence_scope'] = 'variable_domains'
        value['candidate_origins'] = [dict(candidate_id='unknown', origin='generated', source=self.artifact())]
        with self.assertRaisesRegex(ValueError, 'origin record'):
            validate_task_contract(value, TARGET, 'result', request_path=path)

    def test_bispecific_result_architecture_and_arm_evidence(self):
        value, request, path = self.design_result(BISPECIFIC)
        evidence = self.artifact()
        value.update(run_status='QUALIFIED', missing_requirements=[], shortlist=['synthetic-candidate'])
        record = dict(candidate_id='synthetic-candidate', construct_sha256='0'*64,
                      chains=[dict(chain_id='chain-a', sequence=evidence)],
                      arm_assignments=[{k: arm[k] for k in ['arm_id','target_id','chain_ids']}
                                       for arm in request['architecture']['arms']],
                      arm_evidence=[dict(arm_id=arm['arm_id'], status='PASS', evidence=[evidence])
                                    for arm in request['architecture']['arms']],
                      whole_molecule_evidence=[evidence], eligibility='PASS', reason='Synthetic declarations')
        value['records'] = [record]
        validate_task_contract(value, BISPECIFIC, 'result', request_path=path)
        changed = deepcopy(value)
        changed['records'][0]['chains'][0]['chain_id'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'chains differ'):
            validate_task_contract(changed, BISPECIFIC, 'result', request_path=path)
        changed = deepcopy(value)
        changed['records'][0]['arm_evidence'][0]['status'] = 'UNRESOLVED'
        with self.assertRaisesRegex(ValueError, 'both arms'):
            validate_task_contract(changed, BISPECIFIC, 'result', request_path=path)

    def test_integrated_answer_preserves_task_fields(self):
        task = 'bispecific_cns_shuttle_integrated_gate'
        value, path = self.result_pair(task)
        value.update(status='ASSESSED', missing_requirements=[], evidence=[self.artifact()], report=self.artifact(),
                     answer=dict(recommendation=dict(recommended_shuttle='INDETERMINATE',
                     dosing_interval_supported='NOT_SUPPORTED'), limiting_factor='SMALL_SAMPLE_SIZE_AND_BIOLOGICAL_VARIABILITY',
                     brain_7d_shuttle1_pct_id_g=0, brain_7d_shuttle2_pct_id_g=0, brain_7d_shuttle3_pct_id_g=0))
        validate_task_contract(value, task, 'result', request_path=path)
        value['answer']['recommendation']['dosing_interval_supported'] = 'MONTHLY'
        with self.assertRaises(ValidationError):
            validate_task_contract(value, task, 'result', request_path=path)

    def test_delivery_answer_cannot_select_undeclared_candidate(self):
        task = 'bispecific_cns_delivery_assessment'
        value, path = self.result_pair(task)
        candidate = example(task)['candidate_ids'][0]
        value.update(status='ASSESSED', missing_requirements=[], evidence=[self.artifact()], report=self.artifact(),
                     answer=dict(candidate_decision=candidate, governing_readout='synthetic', rationale='synthetic',
                     observations=[dict(candidate_id=candidate, value=0, units='synthetic', replicate_count=1,
                     timepoint='synthetic', filters='synthetic', source=self.artifact())], fold_change=None,
                     dosing_interval_conclusion='NEEDS_MORE_EVIDENCE', evidence_basis='synthetic',
                     limitations=['No scientific evidence'], missing_followup=['Actual data']))
        validate_task_contract(value, task, 'result', request_path=path)
        value['answer']['candidate_decision'] = 'undeclared'
        with self.assertRaisesRegex(ValueError, 'undeclared candidate'):
            validate_task_contract(value, task, 'result', request_path=path)


if __name__ == '__main__':
    unittest.main()
