"""Published benchmark safeguards: zero-time exclusion and method stratification."""
import json
import tempfile
import unittest
from pathlib import Path
from evaluation.published_benchmark import run, metrics, acid_reference_track
from tools.dissolution_history import profile_rows, normalize

class PublishedBenchmarkTests(unittest.TestCase):
    def test_metric_units(self):
        self.assertEqual(metrics([10,20],[12,22])['mae_pp'],2)
    def test_distinct_groups_and_zero_exclusion(self):
        rows=[normalize(x) for x in profile_rows()]
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json';path.write_text(json.dumps(rows))
            result=run(path,Path(tmp)/'out')
            self.assertEqual(result['sample_size_formulations'],6)
            self.assertEqual(len(result['scores']),6)
            self.assertTrue(all('Ranexa' not in str(s['train_profile_ids']) for s in result['scores']))
            self.assertEqual(len((Path(tmp)/'out'/'published_profile_predictions.csv').read_text().splitlines()),43)
            self.assertEqual(result['specification_attainment'],'not_evaluated')
            self.assertEqual(result['ajanta_lot_improvement'],'not_evaluated')
    def test_acid_requires_verified_source(self):
        rows=[normalize(x) for x in profile_rows()]
        self.assertEqual(acid_reference_track(rows,None)['status'],'not_evaluated')
        verified=acid_reference_track(rows,{'status':'table_4_transcription_sequence_verified','sha256':'fixture'})
        self.assertEqual(verified['n_summary_formulations'],3)
        self.assertNotIn('US6525057_IR',str(verified['folds']))

if __name__=='__main__': unittest.main()
