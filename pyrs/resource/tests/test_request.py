import unittest

from pyrs import schema

from .. import request


class TestBuildKwargs(unittest.TestCase):

    def test_simple(self):
        req = request.Request(
            opts=dict(request=None),
            app="Fake",
            path=dict(name='user'),
            query=dict(limit='5'),
            body=dict(password='123'),
            headers={'host': 'www.example.com'}
        )
        self.assertEqual(req.opts, {'request': None})
        self.assertEqual(req.app, "Fake")
        self.assertEqual(req.path, {'name': 'user'})
        self.assertEqual(req.query, {'limit': '5'})
        self.assertEqual(req.body, {'password': '123'})
        self.assertEqual(req.headers, {'host': 'www.example.com'})
        self.assertEqual(req['host'], 'www.example.com')
        with self.assertRaises(TypeError):
            # Request tend to be immutable
            req['other'] = 12

    def test_case_default(self):
        req = request.Request(
            opts=dict(request=None),
            app="Fake",
            path=dict(search='user'),
            query=dict(limit='5'),
            body=None,
            headers={'host': 'www.example.com'}
        )
        kwargs = req.build()
        self.assertEqual(kwargs, {'search': 'user', 'limit': '5'})

    def test_injecting_request(self):
        req = request.Request(
            opts=dict(inject_request=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'request': req}
        )

    def test_injecting_app(self):
        req = request.Request(
            app="FakeApp",
            opts=dict(inject_app=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'app': "FakeApp"}
        )

    def test_injecting_auth(self):
        req = request.Request(
            auth="FakeAuth",
            opts=dict(inject_auth=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'auth': "FakeAuth"}
        )

    def test_injecting_cookies(self):
        req = request.Request(
            cookies="FakeCookies",
            opts=dict(inject_cookies=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'cookies': "FakeCookies"}
        )

    def test_injecting_session(self):
        req = request.Request(
            session="FakeSession",
            opts=dict(inject_session=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'session': "FakeSession"}
        )

    def test_injecting_query(self):
        req = request.Request(
            opts=dict(inject_query=True),
            query=dict(limit='5'),
        )
        kwargs = req.build()
        self.assertEqual(kwargs, {'limit': '5'})

    def test_injecting_path(self):
        req = request.Request(
            opts=dict(inject_path='path'),
            path=dict(user='user'),
        )
        kwargs = req.build()
        self.assertEqual(kwargs, {'path': {'user': 'user'}})

    def test_injecting_body(self):
        req = request.Request(
            opts=dict(inject_body='user'),
            body=dict(name='Name of user'),
        )
        kwargs = req.build()
        self.assertEqual(kwargs, {'user': {'name': 'Name of user'}})


class TestInjection(unittest.TestCase):

    def test_disable(self):
        req = request.Request({})
        kwargs = req._inject(False, {'search': 'user'})

        self.assertEqual(kwargs, {})

    def test_enable(self):
        req = request.Request({})
        kwargs = req._inject(True, {'search': 'user'})

        self.assertEqual(kwargs, {'search': 'user'})

    def test_map(self):
        req = request.Request({})
        kwargs = req._inject('param', {'search': 'user'})

        self.assertEqual(kwargs, {'param': {'search': 'user'}})


class TestParseInput(unittest.TestCase):

    def test_parse_without_parser(self):
        req = request.Request({})

        value = req._parse_value('Hello', None)
        self.assertEqual(value, 'Hello')

    def test_parse_schema(self):
        req = request.Request({})

        class MySchema(schema.Object):
            search = schema.String()
            limit = schema.Integer()

        value_part_cls = req._parse_value(
            {'search': 'hello'}, MySchema
        )
        value_full_cls = req._parse_value(
            {'search': 'hello', 'limit': '1'}, MySchema()
        )
        value_part_obj = req._parse_value(
            {'search': 'hello'}, MySchema
        )
        value_full_obj = req._parse_value(
            {'search': 'hello', 'limit': '1'}, MySchema()
        )

        self.assertEqual(value_part_cls, {'search': 'hello'})
        self.assertEqual(value_part_obj, {'search': 'hello'})

        self.assertEqual(value_full_cls, {'search': 'hello', 'limit': 1})
        self.assertEqual(value_full_obj, {'search': 'hello', 'limit': 1})
