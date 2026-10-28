"""Runtime evidence invariants using synthetic files, never enzyme validation."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


contracts = module('runtime_contracts_under_test', ROOT / 'runtime/contracts.py')
# Reuse the existing synthetic schema fixture in tests only. Production contracts
# implement their semantics directly and never import a test module.
fixtures = module('specification_test_fixtures', ROOT / 'tests/validate_spec.py')


class RuntimeEvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.index = 0
        schema = contracts.load_json(ROOT / 'config/protocol.schema.json')
        self.protocol = fixtures.synthetic_protocol(schema, 'homodimer')
        self.protocol['status'] = 'qualified'
        self.protocol['qualification_evidence'] = [self.artifact('SYNTHETIC SOFTWARE TEST REVIEW')]

        def materialize(value):
            if isinstance(value, dict):
                if 'path_or_uri' in value and value['path_or_uri'].startswith('synthetic://'):
                    return self.artifact('SYNTHETIC CONTRACT CONTENT; NO SCIENTIFIC CLAIM')
                return {k: materialize(v) for k, v in value.items()}
            if isinstance(value, list):
                return [materialize(v) for v in value]
            return value

        self.protocol = materialize(self.protocol)
        self.request = contracts.load_json(ROOT / 'tasks/homodimer.request.example.json')
        self.request['constraints']['length'] = {'min': 4, 'max': 4}
        self.request['execution'].update(final_count=1, max_generated=2,
                                         max_chemistry_candidates=1, controller_mode='fixed')
        self.candidate = {
            'candidate_id': 'synthetic_candidate', 'revision': 1,
            'generation_kind': 'de_novo', 'sequence_designed': True,
            'status': 'chemistry_evaluated',
            'sequence': self.artifact('>synthetic\nACDE\n'),
            'structure': self.artifact('SYNTHETIC STRUCTURE FILE; NOT COORDINATE VALIDATION'),
        }
        self.manifest = {'candidates': [self.candidate]}
        self.evaluation = {'candidates': [{
            'candidate_id': self.candidate['candidate_id'],
            'candidate_sha256': contracts.candidate_hash(self.candidate),
            'rules': [{'rule_id': rule['rule_id'], 'status': 'PASS',
                       'units': rule['units'], 'value': True,
                       'evidence': [self.artifact('SYNTHETIC MEASUREMENT SOFTWARE FIXTURE')]}
                      for rule in self.protocol['rules']],
        }]}

    def artifact(self, text):
        self.index += 1
        path = self.base / f'evidence_{self.index}.txt'
        path.write_text(text)
        return {'path_or_uri': path.name, 'sha256': contracts.digest(path),
                'description': 'SYNTHETIC SOFTWARE TEST, NOT ENZYME EVIDENCE'}

    def qualify(self, evaluation=None, manifest=None, protocol=None):
        return contracts.qualified_ids(evaluation if evaluation is not None else self.evaluation,
                                       manifest if manifest is not None else self.manifest,
                                       protocol if protocol is not None else self.protocol, self.base)

    def test_final_gate_requires_every_current_rule_without_score_compensation(self):
        contracts.check_protocol(self.protocol, self.base)
        contracts.check_candidates(self.manifest, self.base, self.request)
        self.assertEqual(self.qualify(), ['synthetic_candidate'])
        for mutation in ['missing', 'fail', 'unresolved', 'empty_evidence', 'false_value', 'exploratory']:
            with self.subTest(mutation=mutation):
                evaluation, manifest = copy.deepcopy(self.evaluation), copy.deepcopy(self.manifest)
                row = evaluation['candidates'][0]
                row['mean_score'] = 1.0  # Cannot compensate for any mandatory rule.
                if mutation == 'missing':
                    row['rules'].pop()
                elif mutation == 'fail':
                    row['rules'][0]['status'] = 'FAIL'
                elif mutation == 'unresolved':
                    row['rules'][0].update(status='UNRESOLVED', value=None)
                elif mutation == 'empty_evidence':
                    row['rules'][0]['evidence'] = []
                elif mutation == 'false_value':
                    row['rules'][0]['value'] = False
                else:
                    manifest['candidates'][0]['status'] = 'exploratory'
                self.assertEqual(self.qualify(evaluation, manifest), [])
        stale = copy.deepcopy(self.evaluation)
        stale['candidates'][0]['candidate_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'stale'):
            self.qualify(stale)
        path = contracts.artifact_path(self.evaluation['candidates'][0]['rules'][0]['evidence'][0], self.base)
        path.write_text('changed after review')
        with self.assertRaisesRegex(ValueError, 'changed evidence'):
            self.qualify()

    def test_protocol_semantics_require_coverage_typed_gates_and_real_hashes(self):
        for mutation in ['draft', 'chain', 'site', 'step', 'rule_duplicate', 'range', 'operator', 'units', 'weights']:
            with self.subTest(mutation=mutation):
                p = copy.deepcopy(self.protocol)
                if mutation == 'draft':
                    p['status'] = 'draft'
                elif mutation == 'chain':
                    next(r for r in p['rules'] if r['group'] == 'assembly_and_interface')['chain_ids'] = ['A']
                elif mutation == 'site':
                    next(r for r in p['rules'] if r['group'] == 'reactive_geometry')['site_ids'] = ['site_A']
                elif mutation == 'step':
                    p['steps'][0]['to_state'] = 'unknown'
                elif mutation == 'rule_duplicate':
                    p['rules'][1]['rule_id'] = p['rules'][0]['rule_id']
                elif mutation == 'range':
                    p['rules'][0].update(units='angstrom', acceptance={'operator': 'between', 'value': [4, 1]})
                elif mutation == 'operator':
                    p['rules'][0]['acceptance'] = {'operator': 'ge', 'value': True}
                elif mutation == 'units':
                    p['rules'][0]['units'] = 'angstrom'
                else:
                    p['rules'][0]['reward_weight'] = 0.9
                with self.assertRaises(ValueError):
                    contracts.check_protocol(p, self.base)
        contracts.artifact_path(self.protocol['chemistry']['controls'][0], self.base).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or changed'):
            contracts.check_protocol(self.protocol, self.base)

    def test_candidates_cannot_hide_fixtures_invalid_lengths_or_stale_revisions(self):
        original_hash = contracts.candidate_hash(self.candidate)
        revised = copy.deepcopy(self.candidate)
        revised['revision'] += 1
        self.assertNotEqual(original_hash, contracts.candidate_hash(revised))
        for mutation in ['fixture', 'placeholder', 'status', 'revision', 'short', 'ambiguous', 'different_chains', 'duplicate_id', 'quota']:
            with self.subTest(mutation=mutation):
                manifest = copy.deepcopy(self.manifest)
                candidate = manifest['candidates'][0]
                if mutation == 'fixture':
                    candidate['generation_kind'] = 'reference_backbone_redesign'
                elif mutation == 'placeholder':
                    candidate['sequence_designed'] = False
                elif mutation == 'status':
                    candidate['status'] = 'qualified'
                elif mutation == 'revision':
                    candidate['revision'] = True
                elif mutation == 'short':
                    candidate['sequence'] = self.artifact('>short\nACD\n')
                elif mutation == 'ambiguous':
                    candidate['sequence'] = self.artifact('>ambiguous\nACDX\n')
                elif mutation == 'different_chains':
                    candidate['sequence'] = self.artifact('>A\nACDE\n>B\nACDF\n')
                elif mutation == 'duplicate_id':
                    manifest['candidates'].append(copy.deepcopy(candidate))
                else:
                    for i in range(2):
                        manifest['candidates'].append({**candidate, 'candidate_id': f'other_{i}'})
                with self.assertRaises(ValueError):
                    contracts.check_candidates(manifest, self.base, self.request)
        identical_chains = copy.deepcopy(self.manifest)
        identical_chains['candidates'][0]['sequence'] = self.artifact('>A\nACDE\n>B\nACDE\n')
        contracts.check_candidates(identical_chains, self.base, self.request)
        contracts.artifact_path(self.candidate['sequence'], self.base).write_text('>changed\nACDF\n')
        with self.assertRaisesRegex(ValueError, 'changed evidence'):
            contracts.check_candidates(self.manifest, self.base, self.request)

    def test_numeric_acceptance_and_coverage_use_frozen_definitions(self):
        for operator, threshold, passing, failing in [
            ('ge', 5, 5, 4), ('le', 5, 5, 6), ('between', [2, 5], 3, 6),
            ('in', ['left', 'right'], 'left', 'middle'), ('eq', 1, 1, True),
        ]:
            with self.subTest(operator=operator):
                p, e = copy.deepcopy(self.protocol), copy.deepcopy(self.evaluation)
                p['rules'][0].update(units='test_unit', acceptance={'operator': operator, 'value': threshold})
                metric = e['candidates'][0]['rules'][0]
                metric.update(units='test_unit', value=passing)
                self.assertEqual(self.qualify(e, protocol=p), ['synthetic_candidate'])
                metric['value'] = failing
                self.assertEqual(self.qualify(e, protocol=p), [])
        bad = copy.deepcopy(self.evaluation)
        bad['candidates'][0]['rules'][0]['site_ids'] = ['site_A']
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.qualify(bad)
        bad = copy.deepcopy(self.evaluation)
        bad['candidates'][0]['rules'][0]['units'] = 'other'
        with self.assertRaisesRegex(ValueError, 'units'):
            self.qualify(bad)


if __name__ == '__main__':
    unittest.main()
