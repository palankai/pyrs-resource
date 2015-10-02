import unittest

from werkzeug import routing

from .. import operations
from .. import rules


class TestCallerMixin(object):

    def test_caller(self):
        self.assertEqual(self.caller(arg1=1), 2)


class TestBaseCaller(unittest.TestCase, TestCallerMixin):

    def setUp(self):
        def func(arg1):
            return arg1 + 1

        self.caller = rules.Caller(func)


class TestInstanceMethodCaller(unittest.TestCase, TestCallerMixin):

    def setUp(self):
        class Res(object):
            def func(self, arg1):
                return arg1 + 1

        self.caller = rules.InstanceMethodCaller(Res.func, Res())


class TestClassMethodCaller(unittest.TestCase, TestCallerMixin):

    def setUp(self):
        class Res(object):
            def func(self, arg1):
                return arg1 + 1

        self.caller = rules.ClassMethodCaller(Res.func, Res)


class TestMidPoint(unittest.TestCase):

    def test_basic(self):
        midpoint = rules.MidPoint(None)

        self.assertEqual(midpoint.get('x', 1), 1)
        self.assertEqual(midpoint.path.template, '')
        self.assertEqual(midpoint.path.args, {})

    def test_plain_call(self):
        def func(arg1):
            return arg1 + 1
        caller = rules.Caller(func)

        midpoint = rules.MidPoint(caller)

        self.assertEqual(midpoint(None, arg1=1), 2)


class TestEndpoint(unittest.TestCase):

    def test_interface(self):
        operation = operations.Operation('func')
        endpoint = rules.Endpoint(
            'name_of_operation', '/', None, operation
        )

        self.assertIsInstance(endpoint, rules.Endpoint)
        self.assertEqual(endpoint, 'name_of_operation')
        self.assertEqual(endpoint.path, '/')
        self.assertEqual(endpoint['name'], 'func')


class TestMount(unittest.TestCase):

    def test_mount_init(self):
        mount = rules.Mount('/user', None)

        self.assertIsInstance(mount.path, operations.Path)
        self.assertEqual(mount.path, '/user')

    def test_mount_init_with_slashes(self):
        mount = rules.Mount('/user/', None)

        self.assertEqual(mount.path, '/user')

    def test_giving_a_simple_method(self):

        @operations.GET
        def func():
            pass

        mount = rules.Mount('/user', func)

        [rule] = list(mount.get_rules(None))

        self.assertIsInstance(rule, routing.Rule)
        self.assertEqual(rule.rule, '/user')
        self.assertEqual(rule.methods, {'HEAD', 'GET'})

    def test_giving_a_multiple_paths(self):

        @operations.GET(path=['/admin', '/user'])
        def func():
            pass

        mount = rules.Mount('/user', func)

        [rule1, rule2] = list(mount.get_rules(None))

        self.assertIsInstance(rule1, routing.Rule)
        self.assertIsInstance(rule1.endpoint, rules.Endpoint)
        self.assertEqual(rule1.rule, '/user/admin')
        self.assertEqual(rule1.methods, {'HEAD', 'GET'})

        self.assertIsInstance(rule2, routing.Rule)
        self.assertIsInstance(rule2.endpoint, rules.Endpoint)
        self.assertEqual(rule2.rule, '/user/user')
        self.assertEqual(rule2.methods, {'HEAD', 'GET'})


class TestClassMount(unittest.TestCase):

    def test_simple_resource(self):
        class Resource(object):
            @operations.GET
            def func(self):
                pass

        mount = rules.Mount('/user', Resource)
        [rule] = list(mount.get_rules(None))

        self.assertIsInstance(rule, routing.Rule)
        self.assertEqual(rule.rule, '/user')
        self.assertEqual(rule.methods, {'HEAD', 'GET'})

    def test_multiple_methods(self):
        class Resource(object):
            @operations.GET
            def func(self):
                pass

            @operations.POST
            def create_something(self):
                pass

        mount = rules.Mount('/user', Resource)
        [rule1, rule2] = list(mount.get_rules(None))

        self.assertIsInstance(rule1, routing.Rule)
        self.assertEqual(rule1.rule, '/user')
        self.assertEqual(rule1.methods, {'HEAD', 'GET'})

        self.assertIsInstance(rule2, routing.Rule)
        self.assertEqual(rule2.rule, '/user')
        self.assertEqual(rule2.methods, {'POST'})


class TestForwardMount(unittest.TestCase):

    def test_multiple_methods(self):

        class SubResource(object):
            @operations.GET
            def func(self):
                pass

            @operations.POST
            def create_something(self):
                pass

        class Resource(object):
            @operations.GET
            def func(self):
                pass

            @operations.POST
            def create_something(self):
                pass

            @operations.FORWARD('/sub', SubResource)
            def factory(self):
                pass

        mount = rules.Mount('/user', Resource)
        [rule1, rule2, rule3, rule4] = list(mount.get_rules(None))

        self.assertIsInstance(rule1, routing.Rule)
        self.assertEqual(rule1.rule, '/user')
        self.assertEqual(rule1.methods, {'HEAD', 'GET'})

        self.assertIsInstance(rule2, routing.Rule)
        self.assertEqual(rule2.rule, '/user')
        self.assertEqual(rule2.methods, {'POST'})

        self.assertIsInstance(rule3, routing.Rule)
        self.assertEqual(rule3.rule, '/user/sub')
        self.assertEqual(rule3.methods, {'HEAD', 'GET'})

        self.assertIsInstance(rule4, routing.Rule)
        self.assertEqual(rule4.rule, '/user/sub')
        self.assertEqual(rule4.methods, {'POST'})
