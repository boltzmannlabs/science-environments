"""Guard the OpenPKFlow demonstration against FDA-case data contamination."""
import json
import unittest
from pathlib import Path


class OpenPKFlowProbeTests(unittest.TestCase):
    def test_optional_demo_artifact_is_never_lot_data(self):
        artifact = Path(__file__).resolve().parent.parent/'data/processed/openpkflow_package_demo.json'
        if not artifact.exists():
            self.skipTest('optional OpenPKFlow demonstration not executed')
        data = json.loads(artifact.read_text())
        self.assertEqual(data['status'],'software_demonstration_only')
        self.assertEqual(data['product'],'not_ranolazine')
        self.assertEqual(data['uncertainty']['calibration'],'not_established')
        self.assertFalse(any(k.startswith('D-') for k in data['profiles']))
        self.assertNotIn('optimized_composition',data)
        self.assertTrue(all(p['model_fits'] for p in data['profiles'].values()))


if __name__ == '__main__': unittest.main()
