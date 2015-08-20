import unittest

from .. import builder
from .. import resource


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
