"""Synthetic provenance/representation tests; no scientific quality is simulated."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from assessment import INTEGRITY_CHECKS, check_assessment_models, pdb_chain_sequences
from contracts import load_json, object_hash


def artifact(root, name, value):
    path = root / name
    path.write_text(value if isinstance(value, str) else json.dumps(value))
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def pdb_fixture(chains=('A',), residues=('ALA', 'CYS', 'ASP')):
    lines = ['REMARK SYNTHETIC SOFTWARE FIXTURE; GEOMETRY IS NOT VALIDATED']
    for chain in chains:
        for number, residue in enumerate(residues, 1):
            for name in ('N', 'CA', 'C', 'O', 'CB'):
                serial = len(lines)
                lines.append(f'ATOM  {serial:5d} {name:^4s} {residue:3s} {chain}{number:4d}    '
                             f'{float(serial):8.3f}{1.0:8.3f}{2.0:8.3f}  1.00  0.00           C')
    return '\n'.join(lines) + '\nEND\n'


def assessment_fixture(root, candidate, plan_hash, chains=('A',)):
    structure = artifact(root, 'predicted_fixture.pdb', pdb_fixture(chains))
    raw = artifact(root, 'raw_prediction_fixture.txt', 'Synthetic output; not a folding calculation.')
    provenance = artifact(root, 'prediction_fixture.json', {
        'sequence_sha256': candidate['sequence']['sha256'], 'structure_sha256': structure['sha256'],
        'input_basis': 'sequence', 'coordinate_input_sha256': [],
        'method': 'software_fixture', 'version': 'test-only', 'settings': {'synthetic': True},
        'raw_output': raw})
    control = artifact(root, 'geometry_fixture.txt', 'Synthetic contract receipt; no physical measurements.')
    method_validation = artifact(root, 'method_validation_fixture.json', {
        'schema_version': '1.0', 'method': 'software_fixture', 'version': 'test-only',
        'settings_sha256': object_hash({'synthetic': True}), 'evaluation_plan_sha256': plan_hash,
        'status': 'PASS', 'synthetic_only': True,
        'applicability': {'status': 'PASS', 'assembly_kind': 'monomer' if len(chains) == 1 else 'homodimer',
                         'candidate_information_basis': 'synthetic_sequence_only',
                         'control_information_basis': 'synthetic_sequence_only',
                         'rationale': 'Software test only; no inference or scientific validation', 'evidence': [control]},
        'controls': [{'control_id': 'fixture_positive', 'kind': 'positive', 'status': 'PASS',
                      'expected_outcome': 'Synthetic contract behavior only', 'evidence': [control]}]})
    report = artifact(root, 'integrity_fixture.json', {
        'candidate_id': candidate['candidate_id'], 'revision': candidate['revision'],
        'sequence_sha256': candidate['sequence']['sha256'], 'structure_sha256': structure['sha256'],
        'evaluation_plan_sha256': plan_hash, 'status': 'PASS', 'synthetic_only': True,
        'reference_controls': [control], 'checks': [
            {'check_id': key, 'status': 'PASS', 'evidence': [control]} for key in sorted(INTEGRITY_CHECKS)]})
    return {'candidate_id': candidate['candidate_id'], 'revision': candidate['revision'],
            'sequence_sha256': candidate['sequence']['sha256'],
            'generated_structure_sha256': candidate['structure']['sha256'],
            'basis': 'independent_sequence_prediction', 'structure': structure,
            'prediction_record': provenance, 'method_validation': method_validation, 'integrity_report': report}


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = {'candidate_id': 'fixture', 'revision': 1,
                          'sequence': artifact(self.root, 'sequence.fasta', '>fixture\nACD\n'),
                          'structure': artifact(self.root, 'generated.pdb', 'REMARK invalid fixture\n')}
        self.model = assessment_fixture(self.root, self.candidate, 'a' * 64, ('A', 'B'))
        self.assembly = {'kind': 'homodimer', 'sequence_groups': [{'chain_ids': ['A', 'B']}]}

    def validate(self, model=None):
        return check_assessment_models([model or self.model], [self.candidate],
                                       self.assembly, 'a' * 64, self.root)

    def test_homodimer_sequence_mapping_does_not_depend_on_generated_geometry(self):
        self.assertEqual(set(self.validate()), {'fixture'})
        self.assertEqual(pdb_chain_sequences(Path(self.model['structure']['path'])), {'A': 'ACD', 'B': 'ACD'})
        self.assertEqual(Path(self.candidate['structure']['path']).read_text(), 'REMARK invalid fixture\n')

    def test_missing_partner_wrong_sequence_and_duplicate_atoms_are_rejected(self):
        for content in (pdb_fixture(('A',)), pdb_fixture(('A', 'B'), ('ALA', 'CYS', 'GLU')),
                        pdb_fixture(('A', 'B')).replace('END\n', pdb_fixture().splitlines()[1] + '\nEND\n')):
            with self.subTest(content=content[-80:]):
                model = copy.deepcopy(self.model)
                model['structure'] = artifact(self.root, 'wrong.pdb', content)
                with self.assertRaises(ValueError):
                    self.validate(model)

    def test_other_revision_relabeling_and_stale_raw_output_are_rejected(self):
        for key, value in [('revision', 2), ('revision', True), ('sequence_sha256', '0' * 64),
                           ('structure', self.candidate['structure'])]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    self.validate({**self.model, key: value})
        (self.root / 'raw_prediction_fixture.txt').write_text('changed')
        with self.assertRaises(ValueError):
            self.validate()

    def test_failed_unbound_or_incomplete_integrity_report_is_rejected(self):
        original = load_json(Path(self.model['integrity_report']['path']))
        changes = [{'status': 'FAIL'}, {'structure_sha256': '0' * 64},
                   {'evaluation_plan_sha256': '0' * 64}, {'reference_controls': []}, {'checks': []}]
        for change in changes:
            with self.subTest(change=change):
                model = {**self.model, 'integrity_report': artifact(self.root, 'bad_report.json', {**original, **change})}
                with self.assertRaises(ValueError):
                    self.validate(model)

    def test_method_control_failure_is_distinct_from_candidate_failure(self):
        original = load_json(Path(self.model['method_validation']['path']))
        for status in ('FAIL', 'UNRESOLVED'):
            with self.subTest(status=status):
                model = {**self.model, 'method_validation': artifact(self.root, 'control_failure.json', {**original, 'status': status})}
                expected = 'METHOD_CONTROL_FAILED' if status == 'FAIL' else 'METHOD_CONTROL_UNRESOLVED'
                with self.assertRaisesRegex(ValueError, expected):
                    self.validate(model)
        self.assertEqual(self.candidate['revision'], 1)

    def test_control_settings_and_candidate_information_scope_cannot_be_guessed(self):
        original = load_json(Path(self.model['method_validation']['path']))
        changes = [({'settings_sha256': '0' * 64}, 'METHOD_VALIDATION_BINDING_MISMATCH'),
                   ({'controls': []}, 'METHOD_CONTROL_UNRESOLVED'),
                   ({'applicability': {**original['applicability'], 'status': 'UNRESOLVED'}}, 'METHOD_APPLICABILITY_UNRESOLVED'),
                   ({'applicability': {**original['applicability'], 'assembly_kind': 'monomer'}}, 'METHOD_APPLICABILITY_UNRESOLVED')]
        for change, expected in changes:
            with self.subTest(change=change):
                model = {**self.model, 'method_validation': artifact(self.root, 'unmatched_control.json', {**original, **change})}
                with self.assertRaisesRegex(ValueError, expected):
                    self.validate(model)

    def test_integrity_errors_identify_unresolved_failed_or_stale_evidence(self):
        original = load_json(Path(self.model['integrity_report']['path']))
        for change, expected in [({'status': 'UNRESOLVED'}, 'STRUCTURAL_INTEGRITY_UNRESOLVED'),
                                 ({'status': 'FAIL'}, 'STRUCTURAL_INTEGRITY_FAILED'),
                                 ({'structure_sha256': '0' * 64}, 'ASSESSMENT_IDENTITY_MISMATCH')]:
            with self.subTest(change=change):
                model = {**self.model, 'integrity_report': artifact(self.root, 'precise_failure.json', {**original, **change})}
                with self.assertRaisesRegex(ValueError, expected):
                    self.validate(model)


if __name__ == '__main__':
    unittest.main()
