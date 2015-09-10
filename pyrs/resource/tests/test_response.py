import unittest

from pyrs import schema

from .. import response


class TestResponse(unittest.TestCase):

    def test_basic_response(self):
        res = response.ResponseBuilder('content').build()

        self.assertEqual(res.text, 'content')

    def test_status_setup(self):
        res = response.ResponseBuilder(None, opts={'status': 201}).build()

        self.assertEqual(res.status_code, 201)

    def test_header_setup(self):
        res = response.ResponseBuilder(
            None, opts={'headers': {'content-type': 'application/json'}}
        ).build()

        self.assertEqual(
            dict(res.headers), {'content-type': 'application/json'}
        )


class TestBuildContent(unittest.TestCase):

    def test_build_simple_content(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.ResponseBuilder(
            {'num': 12}, opts={'response': MySchema}
        ).build()
        expected = '{"num": 12}'
        self.assertEqual(res.text, expected)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            dict(res.headers),
            {
                'Content-Type': 'application/json',
                'Content-Length': str(len(expected))
            }
        )

    def test_build_tuple_content_status(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.ResponseBuilder(
            ({'num': 12}, 201), opts={'response': MySchema}
        ).build()
        expected = '{"num": 12}'
        self.assertEqual(res.text, expected)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(
            dict(res.headers),
            {
                'Content-Type': 'application/json',
                'Content-Length': str(len(expected))
            }
        )

    def test_build_tuple_content_headers(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.ResponseBuilder(
            ({'num': 12}, {'X-Test': 'hello'}), opts={'response': MySchema}
        ).build()

        expected = '{"num": 12}'
        self.assertEqual(res.text, expected)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            dict(res.headers),
            {
                'Content-Type': 'application/json',
                'X-Test': 'hello',
                'Content-Length': str(len(expected))
            }
        )

    def test_build_tuple_content_status_headers(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.ResponseBuilder(
            ({'num': 12}, 201, {'X-Test': 'hello'}),
            opts={'response': MySchema}
        ).build()

        expected = '{"num": 12}'
        self.assertEqual(res.text, expected)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(
            dict(res.headers),
            {
                'Content-Type': 'application/json',
                'X-Test': 'hello',
                'Content-Length': str(len(expected))
            }
        )
