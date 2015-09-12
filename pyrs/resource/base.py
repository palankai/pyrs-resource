import inspect

from pyrs import schema
import werkzeug

from . import lib
from . import gateway


class Directory(object):

    #: Tuple should be presented as ('/path', Resource, [namespace])
    resources = None

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


def _text_plain(value, option):
    return value


def _application_json_reader(value, option):
    return schema.JSONReader(option).read(value)


def _application_json_writer(value, option):
    return schema.JSONWriter(option).write(value)


def _form_reader(value, option):
    return schema.JSONFormReader(option).read(value)


class Dispatcher(Directory):

    consumers = {
        None: _application_json_reader,
        'query': _form_reader,
        'text/plain': _text_plain,
        'application/json': _application_json_reader,
        'application/x-www-form-urlencoded': _form_reader,
        'multipart/form-data': _form_reader
    }

    producers = {
        'text/plain': _text_plain,
        'application/json': _application_json_writer,
    }

    default_mimetype = 'application/json'
    error_mimetype = 'application/json'

    def __init__(self, parent=None, **config):
        super(Dispatcher, self).__init__(parent, **config)
        self.producers = self.producers.copy()
        self.consumers = self.consumers.copy()

    def dispatch(self, request, path_info=None, method='GET'):
        if path_info is None:
            path_info, method = request.get_route()
        response = gateway.Response()
        try:
            func, kwargs = self.match(path_info, method)
            meta = lib.get_meta(func)
            kwargs.update(request.parse(meta))

            content = func(**kwargs)
            if isinstance(content, gateway.Response):
                return content
            response.parse(request, content)
            return response
        except Exception as ex:
            response.parse(request, ex)
            return response


class App(Dispatcher):

    debug = False

    def dispatch(self, request):
        request.setup(app=self)
        return super(App, self).dispatch(request)

    @gateway.Request.application
    def __call__(self, request):
        return self.dispatch(request)
