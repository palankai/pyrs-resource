import unittest

from pyrs import schema

from .. import base
from .. import gateway


class TestResponse(unittest.TestCase):

    def test_basic_response(self):
        request = gateway.Request.from_values(app=base.App())
        request.parse({})
        response = gateway.Response()
        response.parse(request, 'content')

        self.assertEqual(response.text, 'content')

    def test_status_setup(self):
        request = gateway.Request.from_values(app=base.App())
        request.parse({'status': 201})
        response = gateway.Response()
        response.parse(request)
        self.assertEqual(response.status_code, 201)

    def test_header_setup(self):
        request = gateway.Request.from_values(app=base.App())
        request.parse({'headers': {'X-Special': 'application/json'}})
        response = gateway.Response()
        response.parse(request)
        self.assertEqual(
            response.text, ''
        )
        self.assertEqual(
            dict(response.headers)['X-Special'], 'application/json'
        )


class TestBuildContent(unittest.TestCase):

    def test_build_simple_content(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        request = gateway.Request.from_values(app=base.App())
        request.parse({'output': MySchema})

        response = gateway.Response()
        response.parse(request, {'num': 12})

        expected = '{"num": 12}'

        self.assertEqual(response.text, expected)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            dict(response.headers),
            {
                'Content-Type': 'application/json',
                'Content-Length': str(len(expected))
            }
        )
