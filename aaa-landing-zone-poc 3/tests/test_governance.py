import unittest
from app import governance as g

class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.state = g.init_state()

    def test_environments_differ(self):
        accounts = self.state['accounts']
        self.assertEqual(g.desired(accounts[0])['log_retention_days'], 30)
        self.assertEqual(g.desired(accounts[1])['log_retention_days'], 90)
        self.assertEqual(g.desired(accounts[2])['log_retention_days'], 365)
        self.assertEqual(g.desired(accounts[2])['access_tier'], 'read-only')

    def test_reconcile_then_detect_drift_then_repair(self):
        g.reconcile(self.state)
        self.assertTrue(all(g.assess(a)['status']=='compliant' for a in self.state['accounts']))
        account = self.state['accounts'][2]
        account['actual']['public_s3_block'] = False
        self.assertIn('public_s3_block', g.assess(account)['drift'])
        g.reconcile(self.state, [account['id']])
        self.assertEqual(g.assess(account)['status'], 'compliant')

    def test_failure_isolated(self):
        result = g.reconcile(self.state, fail_ids=['444444444444'])
        self.assertEqual(sum(r['status']=='failed' for r in result), 1)
        self.assertEqual(sum(r['status']=='succeeded' for r in result), 5)

    def test_guardrail_exception_rejected(self):
        with self.assertRaises(ValueError):
            g.request_exception(self.state, '333333333333', 'public_s3_block', False, 'SEC-45', '2027-01-01')

    def test_new_account_inherits_baseline(self):
        account = g.add_account(self.state, '777777777777', 'new-prod', 'production')
        self.assertEqual(g.desired(account)['log_retention_days'], 365)
        g.reconcile(self.state, [account['id']])
        self.assertEqual(g.assess(account)['status'], 'compliant')

if __name__ == '__main__': unittest.main()
