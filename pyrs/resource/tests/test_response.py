import unittest

from pyrs import schema

from .. import response


class TestResponse(unittest.TestCase):

    def test_basic_response(self):
        res = response.Response('content')
        value = res.build()

        self.assertEqual(value, ('content', 200, {}))

    def test_status_setup(self):
        res = response.Response(None, opts={'status': 201})

        self.assertEqual(res.build(), (None, 201, {}))

    def test_header_setup(self):
        res = response.Response(
            None, opts={'headers': {'content-type': 'application/json'}}
        )

        self.assertEqual(
            res.build(), (None, 200, {'content-type': 'application/json'})
        )


class TestCustomProcessor(unittest.TestCase):

    def test_function(self):
        def proc(content, status, headers):
            return str(content), 201, {'X-Test': 'test'}

        res = response.Response(1231, opts={'response': proc})
        self.assertEqual(res.build(), ('1231', 201, {'X-Test': 'test'}))


class TestBuildContent(unittest.TestCase):

    def test_build_simple_content(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.Response({'num': 12}, opts={'response': MySchema})
        self.assertEqual(
            res.build(),
            ('{"num": 12}', 200, {'Content-Type': 'application/json'})
        )

    def test_build_tuple_content_status(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.Response(
            ({'num': 12}, 201), opts={'response': MySchema}
        )
        self.assertEqual(
            res.build(),
            ('{"num": 12}', 201, {'Content-Type': 'application/json'})
        )

    def test_build_tuple_content_headers(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.Response(
            ({'num': 12}, {'X-Test': 'hello'}), opts={'response': MySchema}
        )
        self.assertEqual(
            res.build(),
            (
                '{"num": 12}',
                200,
                {'Content-Type': 'application/json', 'X-Test': 'hello'}
            )
        )

    def test_build_tuple_content_status_headers(self):
        class MySchema(schema.Object):
            num = schema.Integer()

        res = response.Response(
            ({'num': 12}, 201, {'X-Test': 'hello'}),
            opts={'response': MySchema}
        )
        self.assertEqual(
            res.build(),
            (
                '{"num": 12}',
                201,
                {'Content-Type': 'application/json', 'X-Test': 'hello'}
            )
        )
