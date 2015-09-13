import inspect

import werkzeug

from . import lib
from . import gateway


class Directory(object):

    #: Tuple should be presented as ('/path', Resource, [namespace])
    resources = None
    host = 'localhost'

    def __init__(self, parent=None, **config):
        self._parent = parent
        self.functions = {}
        self.rules = werkzeug.routing.Map()
        self.adapter = self.rules.bind(self.host)
        for resource in self.resources or ():
            self.add(*resource)
        self.setup()

    def setup(self):
        pass

    def match(self, path_info, method):
        endpoint, kwargs = self.adapter.match(path_info, method)
        func = self.functions[endpoint]
        return func, kwargs

    def add(self, path, resource, prefix=''):
        if inspect.isfunction(resource):
            self._add_function(path, resource, prefix)
        elif inspect.isclass(resource):
            self._add_class(path, resource(), prefix)
        else:
            self._add_class(path, resource, prefix)

    @property
    def parent(self):
        return self._parent or self

    @property
    def root(self):
        _root = self
        while _root._parent:
            _root = _root.parent
        return _root

    def _add_class(self, path, resource, prefix=''):
        members = lib.get_resource_members(resource)
        if not members:
            raise ValueError(
                "There is no endpoint in the given resource: %s" % resource
            )
        if not prefix:
            prefix = getattr(resource, '_name', lib.get_fqname(resource))
        for member in members:
            opts = lib.get_meta(member)
            self._add_function(path+opts['werkzeug_path'], member, prefix)

    def _add_function(self, path, resource, prefix=''):
        opts = lib.get_meta(resource)
        if opts:
            if prefix:
                prefix += '#'
            name = prefix+opts['name']
            if 'forward' in opts:
                rule = self._make_rule(
                    path+'/<path:path>', opts['methods'], name
                )
                self.rules.add(rule)
            rule = self._make_rule(path, opts['methods'], name)
            self.rules.add(rule)
            self.functions[name] = resource
        else:
            raise ValueError(
                "The given function (%s) is not and endpoint endpoint"
                % resource
            )

    def _make_rule(self, path, methods, endpoint):
        return werkzeug.routing.Rule(path, methods=methods, endpoint=endpoint)


class Scope(object):

    Response = gateway.Response

    def __init__(self, request, application):
        self.request = request
        self.application = application

    @property
    def response(self):
        if not getattr(self, '_response', None):
            self._response = self.Response()
            self._response.parse_request(self.request)
        return self._response

    def forward(self, resource, path='/'):
        return self.application.forward(self, path, resource)


class Dispatcher(Directory):

    Response = gateway.Response

    def dispatch(self, request, path=None, scope=None):
        if path is None:
            path = request.path
        if scope is None:
            scope = Scope(request=request, application=self)
        try:
            func, kwargs = self.match(path, request.method)
            meta = lib.get_meta(func)
            kwargs.update(request.parse(meta))
            if meta.get('scope') is True:
                kwargs.update(scope=scope)

            content = func(**kwargs)
            if isinstance(content, gateway.Response):
                return content
            return scope.response.produce(request, content)
        except Exception as ex:
            return self.Response.from_exception(ex)

    @classmethod
    def forward(cls, scope, path, resource):
        if isinstance(resource, Dispatcher):
            return resource.dispatch(scope.request, path, scope)
        dispatcher = Dispatcher()
        dispatcher.add('', resource)
        return dispatcher.dispatch(scope.request, path, scope)


class App(Dispatcher):

    @gateway.Request.application
    def wsgi(self, request):
        return self.dispatch(request)
