import inspect

import werkzeug

from . import lib
from . import request
from . import response
from . import errors


class Directory(object):

    #: Tuple should be presented as ('/path', Resource, [namespace])
    resources = None

    Arguments = request.Arguments

    def __init__(self, parent=None, **config):
        self._parent = parent
        self.config = lib.get_config(getattr(self, 'config', {}))
        self.config.update(config)
        self.functions = {}
        self.rules = werkzeug.routing.Map()
        self.adapter = self.rules.bind(self.config['host'])
        for resource in self.resources or ():
            self.add(*resource)
        self.setup()

    def setup(self):
        pass

    def match(self, path_info, method):
        endpoint, kwargs = self.adapter.match(path_info, method)
        func = self.functions[endpoint]
        meta = lib.get_meta(func)
        return func, self.root.Arguments(meta, kwargs)

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


class Dispatcher(Directory):

    def dispatch(self, request, path_info=None, method='GET'):
        if path_info is None:
            path_info, method = request.route
        try:
            func, kwargs = self.match(path_info, method)
            request.forward(func, kwargs)
        except Exception as ex:
            res = self.handle_exception(ex, request)
            return res.build()

        try:
            content = request()
            res = response.ResponseBuilder(
                content, self, request.meta, request
            )
            return res.build()
        except Exception as ex:
            res = self.handle_exception(ex, request)
            return res.build()

    def handle_exception(self, ex, request):
        return errors.ErrorResponseBuilder(
            content=ex, app=self, opts=request.meta, request=request
        )


class App(Dispatcher):

    def __getitem__(self, name):
        return self.config[name]

    def dispatch(self, request):
        request.begin(self)
        return super(App, self).dispatch(request)

    @request.Request.application
    def __call__(self, request):
        return self.dispatch(request)
