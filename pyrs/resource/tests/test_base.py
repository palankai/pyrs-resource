import unittest

from pyrs import schema
import werkzeug

from .. import base
from .. import lib
from .. import resource
from .. import request


class TestConfiguration(unittest.TestCase):

    def test_default_configs(self):
        app = base.App()

        app['decorate']
        with self.assertRaises(KeyError):
            app['doesnt_exists_config_key']

    def test_declared_config(self):
        class MyApp(base.App):
            config = {
                'special_config': 'special'
            }

        app = MyApp(debug=True)
        app['decorate']
        self.assertEqual(app['special_config'], 'special')
        self.assertEqual(app['debug'], True)
        with self.assertRaises(KeyError):
            app['doesnt_exists_config_key']


class TestRules(unittest.TestCase):

    def setUp(self):
        self.app = base.App()

    def test_rule_make(self):
        res = self.app._make_rule('/', ['GET'], 'test-endpoint')

        self.assertIsInstance(res, werkzeug.routing.Rule)
        self.assertEqual(res.rule, '/')
        self.assertSetEqual(res.methods, {'GET', 'HEAD'})
        self.assertEqual(res.endpoint, 'test-endpoint')

    def test_add_function_raise_error(self):
        def func(self):
            pass

        with self.assertRaises(ValueError):
            self.app.add('/path', func)

    def test_add_function(self):
        @resource.GET
        def func(self):
            pass

        self.app.add('/path', func)
        rule = self.app.rules._rules[0]

        self.assertTrue(self.app.rules.is_endpoint_expecting('func'))
        self.assertIsInstance(rule, werkzeug.routing.Rule)
        self.assertEqual(rule.rule, '/path')
        self.assertSetEqual(rule.methods, {'GET', 'HEAD'})
        self.assertEqual(rule.endpoint, 'func')

    def test_add_function_with_prefix(self):
        @resource.GET
        def func(self):
            pass

        self.app.add('/path', func, prefix='testbuilder')

        self.app.rules.is_endpoint_expecting('testbuilder#func')

    def test_add_class(self):
        class Resource(object):
            @resource.GET
            def func(self):
                pass

        self.app.add('/path', Resource)
        name = lib.get_fqname(Resource)

        self.app.rules.is_endpoint_expecting(name+'#func')

    def test_add_class_with_prefix(self):
        class Resource(object):
            @resource.GET
            def func(self):
                pass

        self.app.add('/path', Resource, prefix='Resource')

        self.app.rules.is_endpoint_expecting('Resource#func')

    def test_add_class_with_declated_prefix(self):
        class Resource(object):
            _name = 'Resource'

            @resource.GET
            def func(self):
                pass

        self.app.add('/path', Resource)

        self.app.rules.is_endpoint_expecting('Resource#func')

    def test_add_object(self):
        class Resource(object):
            @resource.GET
            def func(self):
                pass

        self.app.add('/path', Resource())
        name = lib.get_fqname(Resource)

        self.app.rules.is_endpoint_expecting(name+'#func')


class TestDispatch(unittest.TestCase):

    def setUp(self):

        class Query(schema.Object):
            limit = schema.String()

        class Req(schema.Object):
            username = schema.String()

        class Res(schema.Object):
            username = schema.String()
            pk = schema.Integer()
            query = Query()

        class Resource(object):
            @resource.RPC(request=Req, response=Res, query=Query)
            def func(self, body, **qry):
                return {'pk': 1, 'username': body['username'], 'query': qry}

        self.app = base.App()
        self.app.add('/path', Resource())

    def test_dispatch(self):
        req = request.req(
            path='/path/', method='POST', query_string={'limit': 5},
            data={'username': 'testuser'}
        )
        res = self.app.dispatch(req, '/path/', 'POST')

        self.assertEqual(
            res.json,
            {'pk': 1, 'username': 'testuser', 'query': {'limit': '5'}}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            dict(res.headers),
            {
                'Content-Type': 'application/json',
                'Content-Length': str(len(res.text))
            }
        )
