"""Holdout integrity and deterministic baseline tests using fake fixtures only."""
import unittest
from environment.state import Episode
from evaluation.baselines import run
from evaluation.holdout_benchmark import benchmark, split
from evaluation.verifier import verify
from models.mixture_predictor import MixturePredictor
from run import investigate


class EvaluationTests(unittest.TestCase):
    def test_baseline_no_claims(self):
        task={'task_id':'ranolazine_er_dissolution_investigation'}
        self.assertEqual(run(task),run(task))
        result = investigate(Episode(task))
        self.assertEqual(result['auditor']['decision'],'abstain')
        self.assertEqual(result['status'],'insufficient_data')
        self.assertTrue(result['unknowns'])

    def test_holdout_split(self):
        rows = [{'label':'measured','source_id':'fixture','group_id':str(i//2),'target':i,'unit':'fixture-unit','composition':{'x':1.0}} for i in range(8)]
        a,b = split(rows)
        self.assertEqual({r['group_id'] for r in a} & {r['group_id'] for r in b},set())
        self.assertEqual((a,b),split(rows))
        self.assertEqual(benchmark([],('x',),'fixture-unit')['status'],'not_evaluated')
        out = benchmark(rows,('x',),'fixture-unit')
        self.assertEqual(out['status'],'evaluated')
        self.assertEqual(out['point_metrics']['status'],'not_established')
        with self.assertRaises(ValueError): MixturePredictor(('x',),'fixture-unit').fit([{'label':'predicted','composition':{'x':1},'target':1,'unit':'fixture-unit'}])

    def test_independent_verifier(self):
        e = Episode({'task_id':'t'})
        e.predictions['x']={'invalid':True}
        self.assertTrue(verify(e))


if __name__ == '__main__': unittest.main()
