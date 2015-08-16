import inspect
import json

import six
import werkzeug.routing as w
from werkzeug.wrappers import Request, Response


class Dispatcher(object):

    def __init__(self):
        self._map = w.Map()
        self._urls = self._map.bind("example.com", "/")
        pass

    def add(self, methods, path, endpoint):
        if isinstance(methods, six.string_types):
            methods = [methods]
        self._map.add(w.Rule(path, methods=methods, endpoint=endpoint))

    def match(self, method, path):
        return self._urls.match(path, method)


def _prepare_func(func):
    func._provide = dict()
    return func


def _base_provide(path, **kwargs):
    def decorator(func):
        _prepare_func(func)
        name = kwargs.pop("name", func.__name__)
        func._provide.update(kwargs)
        func._provide.update({
            "path": path,
            "name": name
        })
        return func
    return decorator


def provide(methods, path="", request=None, response=None, **kwargs):
    if isinstance(methods, six.string_types):
        methods = [methods]
    if request:
        kwargs["request"] = request
    if response:
        kwargs["response"] = response
    return _base_provide(path, methods=methods, **kwargs)


def forward(forward, path, **kwargs):
    assert path, "valid path should be provided"
    return _base_provide(path, forward=forward, **kwargs)


def discover(cls):
    return [
        (m[0], m[1], m[1]._provide)
        for m in inspect.getmembers(cls) if hasattr(m[1], "_provide")
    ]


class Application(object):
    """
    Root
    TODO: middleware,
    """

    def __init__(self, inject=None, kwargs=None):
        self._dispatcher = Dispatcher()
        self._endpoints = {}
        self._inject = inject
        self._extra = kwargs
        self.paths = {}

    def add(self, basepath, resource):
        self.paths[basepath] = resource
        obj = self.get_instance(resource)
        basename = self.get_instance_name(obj)
        methods = discover(obj)
        for name, method, params in methods:
            endpoint = basename+"::"+params["name"]
            path = basepath+(params["path"] or "/")
            self._dispatcher.add(
                params["methods"], path, endpoint
            )
            self._endpoints[endpoint] = method

    def dispatch(self, method, path, extra=None, context=None):
        endpoint, kwargs = self._dispatcher.match(method, path)
        if isinstance(extra, dict):
            kwargs.update(extra)
        func = self._endpoints[endpoint]
        response = self.execute(func, kwargs, context)
        return self.serialize_response(response)

    def serialize_response(self, response):
        return json.dumps(response)

    def execute(self, func, kwargs, context):
        self.prepare(func, kwargs, context)
        response = func(**kwargs)
        return response

    def prepare(self, func, kwargs, context):
        if self._inject:
            kwargs[self._inject] = self
        if isinstance(self._extra, dict):
            kwargs.update(self._extra)

    def get_instance_name(self, obj):
        return obj.__module__+"."+obj.__class__.__name__

    def get_instance(self, resource):
        return resource()


class WSGIAppMixin(object):

    def _dispatch_wsgi_request(self, request):
        raw = self.dispatch(
            request.method,
            request.path,
            extra={"request": request},
            context=request
        )
        response = Response(raw)
        return response

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self._dispatch_wsgi_request(request)
        return response(environ, start_response)

    def prepare(self, func, kwargs, context):
        opts = func._provide
        super(WSGIAppMixin, self).prepare(func, kwargs, context)
        for arg in opts.get("query", []):
            kwargs[arg] = context.args[arg]


class WSGIApplication(WSGIAppMixin, Application):

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
