import inspect

import werkzeug

from . import lib
from . import request
from . import response
from . import errors


class App(object):
    """
    Resource application, provide routing and execution

    :param list hooks: List of hook classes (check :py:mod:`.hooks`)
    :param list resources: Expected items `(path, resource class, [namespace])`
    :param config: optional configuration values (updated :py:mod:`.conf`)
    """
    hooks = []

    #: List of rules, will be **extended** by App(resources=[])
    #: Tuple should be presented: ('path', Resource, [namespace])
    resources = []

    def __init__(self, hooks=None, resources=None, **config):
        #: Store the configuration (copied from :py:mod:`.conf`)
        self.config = lib.get_config(getattr(self, 'config', {}))
        self.functions = {}
        if hooks is not None:
            self.hooks = hooks
        self.config.update(config)
        self.rules = werkzeug.routing.Map()
        for resource in self.resources:
            self.add(*resource)
        for resource in resources or ():
            self.add(*resource)
        self.adapter = self.rules.bind(self['host'])
        self.setup_hooks()

    def __getitem__(self, name):
        return self.config[name]

    def dispatch(
        self, path_info, method, query=None, body=None, headers=None,
        cookies=None, session=None
    ):
        opts = None
        req = None
        try:
            endpoint, path = self.adapter.match(path_info, method)
            func = self.functions[endpoint]
            opts = lib.get_options(func)
            req = request.Request(
                opts, self, path, query, body, headers, cookies, session
            )
            kwargs = req.build()
        except Exception as ex:
            res = self.handle_client_exceptions(
                ex, path_info, method, opts, req
            )
            return res.build()

        try:
            content = func(**kwargs)
            res = response.Response(content, self, opts, req)
            return res.build()
        except Exception as ex:
            res = self.handle_exception(ex, opts, req)
        return res.build()

    def add(self, path, resource, prefix=''):
        if inspect.isfunction(resource):
            self._add_function(path, resource, prefix)
        elif inspect.isclass(resource):
            self._add_class(path, resource(), prefix)
        else:
            self._add_class(path, resource, prefix)

    def handle_client_exceptions(
        self, ex, path_info, method, opts=None, req=None
    ):
        ex = self.transform_exception(ex)
        res = errors.ErrorResponse(ex, self, opts, req)
        return res

    def handle_exception(self, ex, opts, req):
        ex = self.transform_exception(ex)
        res = errors.ErrorResponse(ex, self, opts, req)
        return res

    def transform_exception(self, ex):
        return ex

    def add_rule(self, rule):
        self.rules.add(rule)

    def set_function(self, name, resource):
        self.functions[name] = resource

    def setup_hooks(self):
        pass

    def _add_class(self, path, resource, prefix=''):
        members = lib.get_resource_members(resource)
        if not members:
            raise ValueError(
                "There is no endpoint in the given resource: %s" % resource
            )
        if not prefix:
            prefix = getattr(resource, '_name', lib.get_fqname(resource))
        for member in members:
            opts = lib.get_options(member)
            self._add_function(path+opts['werkzeug_path'], member, prefix)

    def _add_function(self, path, resource, prefix=''):
        opts = lib.get_options(resource)
        if opts:
            if prefix:
                prefix += '#'
            name = prefix+opts['name']
            rule = self._make_rule(path, opts['methods'], name)
            self.add_rule(rule)
            self.set_function(name, resource)
        else:
            raise ValueError(
                "The given function (%s) is not and endpoint endpoint"
                % resource
            )

    def _make_rule(self, path, methods, endpoint):
        return werkzeug.routing.Rule(path, methods=methods, endpoint=endpoint)
