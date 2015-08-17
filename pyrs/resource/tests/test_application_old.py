import unittest
from ..application_old import Dispatcher, provide, discover, forward
from ..application_old import Application
from .. import conf


class TestDispatcher(unittest.TestCase):

    def test_base(self):
        dispatcher = Dispatcher()
        dispatcher.add(["GET"], "/", "test-endpoint")

        self.assertEqual(dispatcher.match("GET", "/"), ('test-endpoint', {}))

    def test_args(self):
        dispatcher = Dispatcher()
        dispatcher.add("GET", "/", "test-endpoint")
        dispatcher.add("GET", "/<id>", "test-endpoint")

        self.assertEqual(
            dispatcher.match("GET", "/1"),
            ('test-endpoint', {"id": "1"})
        )

    def test_spec_args(self):
        dispatcher = Dispatcher()
        dispatcher.add("GET", "/<int:id>", "test-endpoint")

        self.assertEqual(
            dispatcher.match("GET", "/1"),
            ('test-endpoint', {"id": 1})
        )

    def test_rerouting_case(self):
        dispatcher = Dispatcher()
        dispatcher.add("GET", "/page/<path:subpage>", "test-endpoint")

        self.assertEqual(
            dispatcher.match("GET", "/page/1/hu"),
            ('test-endpoint', {"subpage": "1/hu"})
        )


class TestDecorators(unittest.TestCase):

    def test_provide(self):
        class Resource(object):
            @provide("GET")
            def method(self):
                pass

        self.assertEqual(
            getattr(Resource.method, conf.decorate),
            {"methods": ["GET"], "path": "", "name": "method"}
        )

    def test_provide_extra_args(self):
        class Resource(object):
            @provide("GET", schemax=None, name="newname")
            def method(self):
                pass

        self.assertEqual(
            getattr(Resource.method, conf.decorate),
            {
                "methods": ["GET"],
                "path": "",
                "schemax": None,
                "name": "newname"
            }
        )
        self.assertEqual(Resource.method.__name__, "method")

    def test_forward(self):
        class Resource(object):
            @forward("RES", "trans", name="newname", extra=None)
            def method(self):
                pass

        self.assertEqual(
            getattr(Resource.method, conf.decorate),
            {
                "forward": "RES", "path": "trans",
                "name": "newname", "extra": None
            }
        )


class TestDiscover(unittest.TestCase):

    def test_base(self):
        class Resource(object):
            @provide("GET")
            def method(self):
                pass

        r = discover(Resource)
        self.assertEqual(r, [
            (
                "method", Resource.method,
                {"methods": ["GET"], "path": "", "name": "method"}
            )
        ])


class TestApplication(unittest.TestCase):

    def test_get_instance(self):
        class Resource(object):
            pass
        root = Application()
        obj = root.get_instance(Resource)
        self.assertTrue(isinstance(obj, Resource))

    def test_get_name(self):
        class Resource(object):
            pass

        root = Application()
        name = root.get_instance_name(Resource())
        self.assertEqual(name, self.__module__+".Resource")


class TestFunctionality(unittest.TestCase):

    def test_basic(self):
        class Resource(object):
            @provide("GET")
            def method(self, request, app):
                return 1

        root = Application(inject="app", kwargs={"request": "R"})
        root.add("/res", Resource)
        res = root.dispatch("GET", "/res/")
        self.assertEqual(res, '1')
        self.assertEqual(root.paths, {"/res": Resource})
