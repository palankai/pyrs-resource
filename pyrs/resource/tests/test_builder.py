import unittest

import werkzeug

from .. import application
from .. import builder
from .. import lib
from .. import resource


class TestBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = builder.ApplicationBuilder()

    def test_rule_make(self):
        res = self.builder._make_rule('/', ['GET'], 'test-endpoint')

        self.assertIsInstance(res, werkzeug.routing.Rule)
        self.assertEqual(res.rule, '/')
        self.assertSetEqual(res.methods, {'GET', 'HEAD'})
        self.assertEqual(res.endpoint, 'test-endpoint')

    def test_add_function_raise_error(self):
        def func(self):
            pass

        with self.assertRaises(ValueError):
            self.builder.add('/path', func)

    def test_add_function(self):
        @resource.GET
        def func(self):
            pass

        self.builder.add('/path', func)
        rule = self.builder._map._rules[0]

        self.assertTrue(self.builder._map.is_endpoint_expecting('func'))
        self.assertIsInstance(rule, werkzeug.routing.Rule)
        self.assertEqual(rule.rule, '/path')
        self.assertSetEqual(rule.methods, {'GET', 'HEAD'})
        self.assertEqual(rule.endpoint, 'func')

    def test_add_function_with_prefix(self):
        @resource.GET
        def func(self):
            pass

        self.builder.add('/path', func, prefix='testbuilder')

        self.builder._map.is_endpoint_expecting('testbuilder#func')

    def test_add_class(self):
        class Resource(object):
            @resource.GET
            def func(self):
                pass

        self.builder.add('/path', Resource)
        name = lib.get_fqname(Resource)

        self.builder._map.is_endpoint_expecting(name+'#func')

    def test_add_class_with_prefix(self):
        class Resource(object):
            @resource.GET
            def func(self):
                pass

        self.builder.add('/path', Resource, prefix='Resource')

        self.builder._map.is_endpoint_expecting('Resource#func')

    def test_add_class_with_declated_prefix(self):
        class Resource(object):
            _name = 'Resource'

            @resource.GET
            def func(self):
                pass

        self.builder.add('/path', Resource)

        self.builder._map.is_endpoint_expecting('Resource#func')

    def test_add_object(self):
        class Resource(object):
            @resource.GET
            def func(self):
                pass

        self.builder.add('/path', Resource())
        name = lib.get_fqname(Resource)

        self.builder._map.is_endpoint_expecting(name+'#func')

    def test_build(self):
        @resource.GET
        def func(self):
            pass

        self.builder.add('/path', func)
        app = self.builder.bind('example.com')

        self.assertIsInstance(app, application.Application)
        self.assertIsInstance(app._adapter, werkzeug.routing.MapAdapter)
        self.assertEqual(app._endpoints, {'func': func})
