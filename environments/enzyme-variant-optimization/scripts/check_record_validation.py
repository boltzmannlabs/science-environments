"""Regression checks for record validation; no model calls or scientific execution."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from validate_run_records import resolve_reference, validate_artifact_names, validate_configuration_layout, validate_usage_accounting, validate_benchmark_identity

ENV = Path(__file__).resolve().parents[1]


class RecordValidationChecks(unittest.TestCase):
    def setUp(self):
        self.record = next((ENV / 'benchmark/evaluation').rglob('provenance.json'))
        self.metadata = json.loads(self.record.read_text())
        self.metadata['artifacts'] = [next(a for a in self.metadata['artifacts'] if a.get('filename_components'))]

    def test_existing_names(self):
        self.assertEqual(validate_artifact_names(self.record.parent, self.metadata), 1)

    def rejected(self, change):
        data = copy.deepcopy(self.metadata)
        change(data['artifacts'][0])
        with self.assertRaises((ValueError, KeyError)):
            validate_artifact_names(self.record.parent, data)

    def test_omitted_missing_field(self):
        self.rejected(lambda a: a['missing_source_fields'].pop())

    def test_false_missing_field(self):
        self.rejected(lambda a: a['missing_source_fields'].append('run_reference'))

    def test_duplicate_missing_field(self):
        self.rejected(lambda a: a['missing_source_fields'].append(a['missing_source_fields'][0]))

    def test_missing_declaration(self):
        self.rejected(lambda a: a.pop('missing_source_fields'))

    def test_component_and_declaration_disagree(self):
        self.rejected(lambda a: a['filename_components'].__setitem__('tool_name', 'claimed-tool'))

    def test_wrong_run(self):
        self.rejected(lambda a: a['filename_components'].__setitem__('run_reference', 'another-run'))

    def test_original_path_escape(self):
        self.rejected(lambda a: a.__setitem__('original_relative_path', '../../outside.csv'))

    def test_absolute_reference_rejected(self):
        with self.assertRaises(ValueError):
            resolve_reference(ENV / 'config', '/tmp/anything', ENV)

    def test_parent_reference_within_environment(self):
        self.assertEqual(resolve_reference(ENV / 'config', '../tasks/README.md', ENV), ENV / 'tasks/README.md')

    def test_reference_escape_rejected(self):
        with self.assertRaises(ValueError):
            resolve_reference(ENV / 'config', '../../../outside', ENV)

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'env'
            root.mkdir()
            (root / 'escape').symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                resolve_reference(root, 'escape/outside', root)

    def test_configuration_layout(self):
        self.assertEqual(validate_configuration_layout(ENV)['configurations_validated'], 19)

    def test_benchmark_assisted_scope_rejected(self):
        data = copy.deepcopy(self.metadata)
        data['approach'] = 'agent-with-specialist'
        with self.assertRaises(ValueError):
            validate_benchmark_identity(ENV, self.record, data)

    def test_benchmark_wrong_run_rejected(self):
        data = copy.deepcopy(self.metadata)
        data['run_id'] = 'another-run'
        with self.assertRaises(ValueError):
            validate_benchmark_identity(ENV, self.record, data)

    def test_usage_double_count_rejected(self):
        path = next((ENV / 'runs').glob('task_*/*/run.json'))
        run = json.loads(path.read_text())
        validate_usage_accounting(run)
        run['usage_accounting']['parent_plus_specialists']['token_total_excluding_reasoning_subset'] += 1
        with self.assertRaises(ValueError):
            validate_usage_accounting(run)

    def test_usage_overlap_rejected(self):
        path = next((ENV / 'runs').glob('task_*/*/run.json'))
        run = json.loads(path.read_text())
        run['usage_accounting']['specialist_session_ids'].append(run['native_session_ids'][0])
        with self.assertRaises(ValueError):
            validate_usage_accounting(run)

    def test_impossible_calendar_timestamp_rejected(self):
        data = copy.deepcopy(self.metadata)
        item = data['artifacts'][0]
        item['filename_components']['timestamp_utc'] = '20261399T259999Z'
        item['missing_source_fields'].remove('timestamp_utc')
        with self.assertRaises(ValueError):
            validate_artifact_names(self.record.parent, data)

    def test_parameter_reference_wrong_job_rejected(self):
        for record in (ENV / 'results').rglob('provenance.json'):
            data = json.loads(record.read_text())
            item = next((a for a in data['artifacts'] if a.get('filename_components', {}).get('parameters') == 'metadata'), None)
            if item:
                data['artifacts'] = [item]
                item['parameters_reference'] = item['parameters_reference'].split('#')[0] + '#entry-0'
                with self.assertRaises(ValueError):
                    validate_artifact_names(record.parent, data)
                return
        self.fail('Expected recorded native parameter fixture')


if __name__ == '__main__':
    unittest.main()
