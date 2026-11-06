"""Public-validator regression tests using synthetic, non-biological records only."""
from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import unittest

from .contract_fixtures import ContractFixture, ROOT, validation


class ReferenceGuidedTests(ContractFixture, unittest.TestCase):
    def _protocol(self):
        protocol = super()._protocol()
        protocol['task_id'] = 'mab_reference_guided_001'
        return protocol

    def _request(self):
        request = validation.read_json(ROOT / 'config/monoclonal_reference/request.example.json')
        files = {
            'inputs/target.fasta': '>synthetic\nACDE\n',
            'inputs/construct.fasta': '>synthetic\nACDE\n',
            'inputs/reference-heavy.fasta': '>synthetic-heavy\nCDEF\n',
            'inputs/reference-light.fasta': '>synthetic-light\nGHIK\n',
            'inputs/reference-regions.json': '{}',
        }
        for artifact in validation._artifact_entries(request):
            path = self._write(self.root / artifact['path'], files[artifact['path']])
            artifact['sha256'] = validation.sha256(path)
            artifact['source'] = 'Synthetic contract fixture; not biological evidence'
        request['antibody']['reference']['antibody_id'] = 'synthetic-reference'
        request['antibody']['reference']['heavy_chain_id'] = 'H'
        request['antibody']['reference']['light_chain_id'] = 'L'
        request['constraints']['max_candidates'] = 2
        return request

    def _save_protocol_and_request(self):
        self.protocol_path = self._write(self.root / 'protocol.json', json.dumps(self.protocol))
        self.request = self._request()
        self.request['evaluation']['protocol'] = {
            **self._artifact(self.protocol_path), 'media_type': 'application/json',
            'source': 'Synthetic protocol fixture; no scientific qualification',
        }
        self.request_path = self._write(self.root / 'request.json', json.dumps(self.request))

    def _bundle(self, **kwargs):
        bundle = super()._bundle(**kwargs)
        metrics = validation.read_json(bundle / 'metrics.json')
        del metrics['variant']
        metrics.update(task_id=self.request['task_id'], design_mode=self.request['design_mode'],
                       sequence_scope=self.request['antibody']['sequence_scope'], assay_records=[])
        metrics['records'][0]['candidate_id'] = 'synthetic-reference'
        metrics['records'][1]['parent_id'] = 'synthetic-reference'
        metrics['provenance']['agent_run'] = {
            'agent_id': 'synthetic', 'model_provider': 'synthetic', 'model_id': 'synthetic',
            'model_revision': 'synthetic', 'harness_revision': 'synthetic',
            'task_prompt_sha256': 'a' * 64, 'system_prompt_sha256': 'b' * 64,
            'enabled_tools_sha256': 'c' * 64, 'execution_backend': 'local',
            'environment_digest': None, 'workspace_id': 'synthetic-isolated',
            'workspace_isolated': True, 'random_seed': self.request['evaluation']['seed'],
        }
        self._write(bundle / 'metrics.json', json.dumps(metrics))
        return bundle

    def _validate(self, bundle):
        return validation.validate_bundle(bundle, self.request_path, self.root, allow_synthetic=True)

    def _edit_metrics(self, bundle, edit):
        path = bundle / 'metrics.json'
        metrics = validation.read_json(path)
        edit(metrics)
        path.write_text(json.dumps(metrics))

    def test_complete_reference_contract_dispatches_to_generic_validation(self):
        result = validation.preflight(self.request, self.root)
        self.assertEqual(result['status'], 'CONTRACT_READY')
        self.assertIn('unverified', result['scope'])
        self.assertEqual(self._validate(self._bundle())['shortlist'], ['candidate-1'])

    def test_missing_reference_is_rejected_in_every_active_mode(self):
        for mode in validation.REFERENCE_GUIDED_MODES:
            with self.subTest(mode=mode):
                request = copy.deepcopy(self.request)
                request['design_mode'] = mode
                request['antibody']['reference'] = None
                with self.assertRaises(validation.ValidationError):
                    validation.preflight(request, self.root)

    def test_missing_antigen_is_rejected_in_every_active_mode(self):
        for mode in validation.REFERENCE_GUIDED_MODES:
            for omit in (False, True):
                with self.subTest(mode=mode, omitted=omit):
                    request = copy.deepcopy(self.request)
                    request['design_mode'] = mode
                    if omit:
                        del request['target']
                    else:
                        request['target'] = None
                    with self.assertRaises(validation.ValidationError):
                        validation.preflight(request, self.root)

    def test_target_only_and_bispecific_requests_are_rejected(self):
        for mode in ('de_novo', 'bispecific'):
            with self.subTest(mode=mode):
                request = copy.deepcopy(self.request)
                request['design_mode'] = mode
                with self.assertRaises(validation.ValidationError):
                    validation.preflight(request, self.root)

    def test_target_only_result_is_rejected(self):
        bundle = self._bundle()
        self._edit_metrics(bundle, lambda m: m.update(design_mode='de_novo'))
        with self.assertRaises(validation.ValidationError):
            self._validate(bundle)

    def test_nonpaired_architectures_are_rejected(self):
        for antibody_format in ('VHH', 'scFv', 'bispecific'):
            with self.subTest(antibody_format=antibody_format):
                request = copy.deepcopy(self.request)
                request['antibody']['format'] = antibody_format
                with self.assertRaises(validation.ValidationError):
                    validation.preflight(request, self.root)

    def test_objective_specific_requirements_are_not_optional(self):
        cases = [
            ('humanization', 'immunogenicity'),
            ('specificity_optimization', 'cross-reactivity panel'),
            ('mechanism_optimization', 'functional mechanism'),
        ]
        for mode, message in cases:
            with self.subTest(mode=mode):
                request = copy.deepcopy(self.request)
                request['design_mode'] = mode
                with self.assertRaisesRegex(ValueError, message):
                    validation.preflight(request, self.root)

    def test_requested_shortlist_cannot_exceed_candidate_budget(self):
        self.request['evaluation']['requested_count'] = 3
        with self.assertRaisesRegex(ValueError, 'candidate budget'):
            validation.preflight(self.request, self.root)

    def test_missing_antigen_or_reference_chain_file_reports_needs_input(self):
        for filename in ('target.fasta', 'construct.fasta',
                         'reference-heavy.fasta', 'reference-light.fasta'):
            with self.subTest(filename=filename):
                path = self.root / 'inputs' / filename
                contents = path.read_bytes()
                path.unlink()
                try:
                    result = validation.preflight(self.request, self.root)
                    self.assertEqual(result['status'], 'NEEDS_INPUT')
                    self.assertTrue(any(filename in item for item in result['missing_requirements']))
                finally:
                    path.write_bytes(contents)

    def test_changed_reference_file_is_rejected_by_hash(self):
        (self.root / 'inputs/reference-heavy.fasta').write_text('changed fixture')
        result = validation.preflight(self.request, self.root)
        self.assertEqual(result['status'], 'NEEDS_INPUT')
        self.assertTrue(any('hash mismatch' in item for item in result['missing_requirements']))

    def test_missing_protocol_reports_protocol_required(self):
        self.request['evaluation']['protocol'] = None
        self.assertEqual(validation.preflight(self.request, self.root)['status'], 'PROTOCOL_REQUIRED')

    def test_protocol_cannot_drop_required_developability_evidence(self):
        for rule in self.protocol['rules']:
            if rule['group'] == 'aggregation':
                rule['required'] = False
        self._save_protocol_and_request()
        result = validation.preflight(self.request, self.root)
        self.assertEqual(result['status'], 'PROTOCOL_REQUIRED')
        self.assertTrue(any('aggregation' in item for item in result['missing_requirements']))

    def test_reference_chain_ids_cannot_be_identical(self):
        self.request['antibody']['reference']['light_chain_id'] = 'H'
        with self.assertRaisesRegex(ValueError, 'chain IDs must differ'):
            validation.preflight(self.request, self.root)

    def test_reference_numbering_must_match_constraints(self):
        self.request['constraints']['numbering_scheme'] = 'different-numbering'
        with self.assertRaisesRegex(ValueError, 'numbering schemes must match'):
            validation.preflight(self.request, self.root)

    def test_reference_record_is_required(self):
        bundle = self._bundle()
        self._edit_metrics(bundle, lambda m: m['records'].pop(0))
        with self.assertRaisesRegex(ValueError, 'Exactly one declared reference'):
            self._validate(bundle)

    def test_reference_cannot_be_shortlisted_as_a_design(self):
        bundle = self._bundle()
        self._edit_metrics(bundle, lambda m: m.update(shortlist=['synthetic-reference']))
        with self.assertRaisesRegex(ValueError, 'Shortlist contradicts'):
            self._validate(bundle)

    def test_candidate_must_name_the_supplied_parent(self):
        bundle = self._bundle()
        self._edit_metrics(bundle, lambda m: m['records'][1].update(parent_id='other-reference'))
        with self.assertRaisesRegex(ValueError, 'lineage'):
            self._validate(bundle)

    def test_reference_record_must_match_supplied_chain_artifacts(self):
        bundle = self._bundle()
        def replace_reference(metrics):
            reference = metrics['records'][0]
            reference['sequences']['heavy'] = 'ACDF'
            digest = validation.sequence_hash(reference['sequences'])
            reference['sequence_sha256'] = digest
            for rule in reference['rules']:
                rule['sequence_sha256'] = digest
        self._edit_metrics(bundle, replace_reference)
        with self.assertRaisesRegex(ValueError, 'Reference heavy-chain sequence differs'):
            self._validate(bundle)

    def test_missing_reference_evidence_cannot_support_qualification(self):
        bundle = self._bundle()
        def unset_evidence(metrics):
            metrics['records'][0]['rules'][0].update(value=None, state='UNRESOLVED',
                                                   evidence=[], reason='Missing fixture evidence')
        self._edit_metrics(bundle, unset_evidence)
        with self.assertRaisesRegex(ValueError, 'Reference evidence is incomplete'):
            self._validate(bundle)

    def test_run_provenance_requires_manifest_seed_and_isolation(self):
        mutations = [
            (lambda m: m['provenance'].pop('agent_run'), 'must record model'),
            (lambda m: m['provenance']['agent_run'].update(random_seed=2), 'seed differs'),
            (lambda m: m['provenance']['agent_run'].update(workspace_isolated=False), 'isolated workspace'),
        ]
        for edit, message in mutations:
            with self.subTest(message=message):
                bundle = self._bundle()
                self._edit_metrics(bundle, edit)
                with self.assertRaisesRegex(ValueError, message):
                    self._validate(bundle)

    def test_fasta_and_csv_must_match_generic_shortlist(self):
        for filename in ('designed_sequences.fasta', 'shortlist.csv'):
            with self.subTest(filename=filename):
                bundle = self._bundle()
                (bundle / filename).write_text('')
                with self.assertRaises(ValueError):
                    self._validate(bundle)

    def test_synthetic_bundle_is_rejected_without_test_override(self):
        with self.assertRaisesRegex(ValueError, 'Synthetic fixture'):
            validation.validate_bundle(self._bundle(), self.request_path, self.root)

    def test_generic_preflight_cli_reports_missing_inputs(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / 'tests/monoclonal_antibody_with_reference/validation.py'), 'preflight',
             str(ROOT / 'config/monoclonal_reference/request.example.json'), '--input-root', str(self.root / 'missing')],
            text=True, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'NEEDS_INPUT')


if __name__ == '__main__':
    unittest.main()
