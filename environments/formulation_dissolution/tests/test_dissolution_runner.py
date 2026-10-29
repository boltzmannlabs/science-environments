"""CLI smoke and safety gates; no network or real laboratory backend required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cli import dispatch
from tools.dissolution_runner import submit
from tools.dissolution_history import inventory

class Args:
    command='solve';config='configs/task.yaml';mode='predict';track='fixtures'

class CLITests(unittest.TestCase):
    def test_prediction_abstains(self):
        result=dispatch(Args())
        self.assertEqual(result['status'],'insufficient_data')
        self.assertEqual(result['artifacts'],[])
    def test_fixture_no_measured_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(submit('predict',tmp)['status'],'insufficient_data')
            self.assertEqual(submit('replay',tmp)['status'],'tool_unavailable')
    def test_missing_archive_logged(self):
        entries=inventory(legacy_root='/nonexistent',prior_gym_root='/nonexistent')
        self.assertTrue(all(e['permission_status']=='unresolved' for e in entries))

if __name__=='__main__': unittest.main()
