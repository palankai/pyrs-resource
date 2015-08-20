import unittest

from .. import builder
from .. import resource
from .. import response


class TestApplication(unittest.TestCase):

    def setUp(self):
        class Resource(object):
            _name = 'Resource'

            @resource.GET
            def func(self):
                return 'hello'

        self.resource = Resource()
        self.builder = builder.ApplicationBuilder()
        self.builder.add('/path', self.resource)
        self.app = self.builder.bind('example.com')

    def test_match(self):
        endpoint, kwargs = self.app.match('GET', '/path/')
        self.assertEqual(endpoint, 'Resource#func')
        self.assertEqual(kwargs, {})

    def test_dispatch(self):
        content, status, headers = self.app.dispatch('GET', '/path/')

        self.assertEqual(content, 'hello')
        self.assertEqual(status, 200)
        self.assertEqual(headers, {})

    def test_dispatch_x(self):
        res = self.app.disp('GET', '/path/')

        self.assertEqual(res, 1)

    def test_execute_endpoint(self):
        @resource.GET
        def func():
            return 'hello'

        res = self.app.execute(func, {})
        self.assertIsInstance(res, response.Response)
        self.assertEqual(res.content, 'hello')
        self.assertEqual(res.status, 200)
        self.assertEqual(res.headers, {})
