"""Public literature discovery must not become fabricated lot-level measurements."""
import json
import unittest
from pathlib import Path


class PublicLiteratureTests(unittest.TestCase):
    def test_catalog_is_reference_only(self):
        path = Path(__file__).resolve().parent.parent / 'data' / 'processed' / 'public_literature_catalog.json'
        catalog = json.loads(path.read_text())
        self.assertEqual(catalog['purpose'], 'Public-source discovery only; not a training or lot-level QC dataset')
        for record in catalog['records']:
            self.assertEqual(record['evidence_label'], 'literature_reported')
            self.assertTrue(record['doi'] and record['pdf_sha256'] and record['quality_flags'])
            self.assertNotEqual(record.get('readiness'), 'validated_measured_holdout')
            self.assertNotIn('dissolution_measurements', record)


if __name__ == '__main__': unittest.main()
