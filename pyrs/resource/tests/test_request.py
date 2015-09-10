import unittest

from pyrs import schema

from .. import lib
from .. import request


class TestBuildKwargs(unittest.TestCase):

    def test_simple(self):
        req = request.RequestOld(
            opts=dict(request=None),
        )
        self.assertEqual(req.opts, {'request': None})
        self.assertEqual(req.app, lib.get_config())
        with self.assertRaises(TypeError):
            # Request tend to be immutable
            req['other'] = 12

    def test_case_default(self):
        req = request.RequestOld(
            opts=dict(request=None),
            app={},
            path={'search': 'user'},
        )
        kwargs = req.build()
        self.assertEqual(kwargs, {'search': 'user'})

    def test_injecting_request(self):
        req = request.RequestOld(
            opts=dict(inject_request=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'request': req}
        )

    def test_injecting_app(self):
        req = request.RequestOld(
            opts=dict(inject_app=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'app': lib.get_config()}
        )

    def test_injecting_auth(self):
        req = request.RequestOld(
            auth="FakeAuth",
            opts=dict(inject_auth=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'auth': "FakeAuth"}
        )

    def test_injecting_cookies(self):
        req = request.RequestOld(
            cookies="FakeCookies",
            opts=dict(inject_cookies=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'cookies': "FakeCookies"}
        )

    def test_injecting_session(self):
        req = request.RequestOld(
            session="FakeSession",
            opts=dict(inject_session=True),
        )
        kwargs = req.build()
        self.assertEqual(
            kwargs, {'session': "FakeSession"}
        )


class TestInjection(unittest.TestCase):

    def test_disable(self):
        req = request.RequestOld({})
        kwargs = req._inject(False, {'search': 'user'})

        self.assertEqual(kwargs, {})

    def test_enable(self):
        req = request.RequestOld({})
        kwargs = req._inject(True, {'search': 'user'})

        self.assertEqual(kwargs, {'search': 'user'})

    def test_map(self):
        req = request.RequestOld({})
        kwargs = req._inject('param', {'search': 'user'})

        self.assertEqual(kwargs, {'param': {'search': 'user'}})


class TestParseInput(unittest.TestCase):

    def test_parse_without_parser(self):
        req = request.RequestOld({})

        value = req._parse_value('Hello', None)
        self.assertEqual(value, 'Hello')

    def test_parse_schema(self):
        req = request.RequestOld({})

        class MySchema(schema.Object):
            search = schema.String()
            limit = schema.Integer()

        value_part_cls = req._parse_value(
            {'search': 'hello'}, MySchema()
        )
        value_full_cls = req._parse_value(
            {'search': 'hello', 'limit': '1'}, MySchema()
        )
        value_part_obj = req._parse_value(
            {'search': 'hello'}, MySchema()
        )
        value_full_obj = req._parse_value(
            {'search': 'hello', 'limit': '1'}, MySchema()
        )

        self.assertEqual(value_part_cls, {'search': 'hello'})
        self.assertEqual(value_part_obj, {'search': 'hello'})

        self.assertEqual(value_full_cls, {'search': 'hello', 'limit': 1})
        self.assertEqual(value_full_obj, {'search': 'hello', 'limit': 1})
