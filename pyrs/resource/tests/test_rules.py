import unittest

from werkzeug import routing

from .. import endpoints
from .. import rules


class TestMount(unittest.TestCase):

    def test_mount_init(self):
        mount = rules.Mount('/user', None)

        self.assertIsInstance(mount.path, endpoints.Path)
        self.assertEqual(mount.path, '/user')

    def test_mount_init_with_slashes(self):
        mount = rules.Mount('/user/', None)

        self.assertEqual(mount.path, '/user')

    def test_giving_a_simple_method(self):

        @endpoints.GET
        def func():
            pass

        mount = rules.Mount('/user', func)

        [rule] = list(mount.get_rules(None))

        self.assertIsInstance(rule, routing.Rule)
        self.assertEqual(rule.endpoint, 'func')
        self.assertEqual(rule.rule, '/user')
        self.assertEqual(rule.methods, {'HEAD', 'GET'})

    def test_giving_a_multiple_paths(self):

        @endpoints.GET(path=['/admin', '/user'])
        def func():
            pass

        mount = rules.Mount('/user', func)

        [rule1, rule2] = list(mount.get_rules(None))

        self.assertIsInstance(rule1, routing.Rule)
        self.assertIsInstance(rule1.endpoint, endpoints.Endpoint)
        self.assertEqual(rule1.endpoint, 'func')
        self.assertEqual(rule1.rule, '/user/admin')
        self.assertEqual(rule1.methods, {'HEAD', 'GET'})

        self.assertIsInstance(rule2, routing.Rule)
        self.assertIsInstance(rule2.endpoint, endpoints.Endpoint)
        self.assertEqual(rule2.endpoint, 'func')
        self.assertEqual(rule2.rule, '/user/user')
        self.assertEqual(rule2.methods, {'HEAD', 'GET'})
