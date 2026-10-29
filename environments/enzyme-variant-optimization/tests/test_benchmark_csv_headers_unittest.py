"""Public-input header regression; no scientific/model service calls."""
import csv
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from enzyme_research.demo import fixture_task
from enzyme_research.preparation import prepare_input
from enzyme_research.store import Store
from enzyme_research.workflow import load_workflow
from enzyme_research.paths import bundled_workflow_source


class ExactBenchmarkCSVHeaders(unittest.TestCase):
    def test_explicit_benchmark_headers_preserve_pairs_and_cache_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            task = fixture_task(root)
            task['allowed_jobs'] = ['Cat_Pred', 'Netsolp', 'Protein_Structure_Prediction']
            store = Store(root / 'state')
            campaign = store.start(task, 'base')
            catalogue = root / 'catalogue'
            catalogue.mkdir()
            (catalogue / 'tool-contracts.v1.json').write_text(json.dumps({'tools': {
                job: {'status': 'active', 'execution_blocked': False} for job in task['allowed_jobs']}}))
            load_workflow(bundled_workflow_source())
            service = SimpleNamespace(store=store, settings={'catalogue_root': str(catalogue)})
            old = prepare_input(service, campaign, 'Cat_Pred', ['parent'])
            service.settings['csv_headers'] = ['Seq_id', 'Sequences', 'SMILES']
            for job in task['allowed_jobs']:
                prepared = prepare_input(service, campaign, job, ['parent'])
                with Path(prepared['path']).open(newline='') as handle:
                    reader = csv.reader(handle)
                    self.assertEqual(next(reader), ['Seq_id', 'Sequences', 'SMILES'])
                    self.assertEqual(list(reader), [['parent', task['parent']['sequence'], task['substrate']['smiles']]])
                self.assertEqual(prepared, prepare_input(service, campaign, job, ['parent']))
                self.assertNotEqual(old['input_id'], prepared['input_id'])
            self.assertEqual(store.status(campaign)['calls'], [])


if __name__ == '__main__':
    unittest.main()
