"""Adapter timeout, malformed, auth, retries and unavailable tests."""
import unittest
from time import sleep
from environment.observations import Observation, Value
from tools.boltzmann_adapters import Registry, Contract


class AdapterTests(unittest.TestCase):
    def setUp(self): self.registry = Registry()
    def register(self, invoke, *, timeout=1, retries=0):
        self.registry.register(Contract('fixture','1','dissolution',invoke,lambda p:True,lambda r:isinstance(r,Observation),timeout,retries),approved=True)

    def test_unavailable_and_approval(self):
        self.assertEqual(self.registry.call('dissolution',{},task_id='t').status,'tool_unavailable')
        with self.assertRaises(PermissionError): self.registry.register(Contract('x','1','x',lambda p,i:None,lambda p:True,lambda r:True),approved=False)

    def test_success_provenance(self):
        self.register(lambda p,i:Observation('t','success','predicted',results=[Value('y',1,'%', 'predicted')]))
        result = self.registry.call('dissolution',{},task_id='t')
        self.assertEqual(result.provenance['version'],'1')
        self.assertEqual(result.result_type,'predicted')

    def test_timeout(self):
        self.register(lambda p,i:sleep(0.03), timeout=0.001)
        self.assertIn('timeout', self.registry.call('dissolution',{},task_id='t').warnings)

    def test_malformed_auth_retry(self):
        self.register(lambda p,i:{'junk':True})
        self.assertIn('malformed response',self.registry.call('dissolution',{},task_id='t').warnings)
        r = Registry()
        r.register(Contract('fixture','1','x',lambda p,i: (_ for _ in ()).throw(PermissionError('secret')),lambda p:True,lambda r:True),approved=True)
        self.assertEqual(r.call('x',{},task_id='t').warnings,['authentication_failed'])
        calls = []
        def fail(p,i):
            calls.append(i)
            raise ConnectionError('do not log raw error')
        q = Registry()
        q.register(Contract('fixture','1','x',fail,lambda p:True,lambda r:True,retries=2),approved=True)
        self.assertEqual(len(q.call('x',{},task_id='t').warnings),3)
        self.assertEqual(len(calls),3)


if __name__ == '__main__': unittest.main()
