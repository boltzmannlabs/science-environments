"""Persistence, observations and budget regression tests."""
import tempfile
import unittest
from pathlib import Path
from environment.state import Episode
from environment.budget import Budget
from environment.observations import Value, Observation


class StateTests(unittest.TestCase):
    def test_resume_audit(self):
        with tempfile.TemporaryDirectory() as d:
            e = Episode({'task_id':'t'})
            e.log('check','success')
            e.save(Path(d)/'state.json')
            restored = Episode.load(Path(d)/'state.json')
            self.assertEqual(restored.audit[0]['action'],'check')

    def test_labels(self):
        with self.assertRaises(ValueError): Value('dissolution',42,'%', 'measured')
        with self.assertRaises(ValueError): Value('dissolution',42,None, 'predicted')
        v = Value('dissolution',42,'%', 'predicted')
        with self.assertRaises(ValueError): Observation('t','success','measured',results=[v])

    def test_budget(self):
        b = Budget({'actions':1})
        b.charge('actions')
        with self.assertRaises(RuntimeError): b.charge('actions')
        self.assertEqual(Budget.restore(b.snapshot()).used['actions'],1)


if __name__ == '__main__': unittest.main()
