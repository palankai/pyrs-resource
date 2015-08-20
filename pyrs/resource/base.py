import inspect

import werkzeug

from . import lib
from . import request
from . import response


class App(object):

    def __init__(self, host='localhost', debug=False):
        self.config = lib.get_config(getattr(self, 'config', {}))
        self.config.update({
            'debug': debug,
            'host': host
        })
        self.rules = werkzeug.routing.Map()
        self.adapter = self.rules.bind(host)
        self.functions = {}

    def __getitem__(self, name):
        return self.config[name]

    def dispatch(
        self, path_info, method, query=None, body=None, headers=None,
        cookies=None, session=None
    ):
        endpoint, path = self.adapter.match(path_info, method)
        func = self.functions[endpoint]
        opts = lib.get_options(func)
        req = request.Request(
            opts, self, path, query, body, headers, cookies, session
        )
        kwargs = req.build()
        content = func(**kwargs)
        res = response.Response(content, self, opts, req)
        return res.build()

    def add(self, path, resource, prefix=''):
        if inspect.isfunction(resource):
            self._add_function(path, resource, prefix)
        elif inspect.isclass(resource):
            self._add_class(path, resource(), prefix)
        else:
            self._add_class(path, resource, prefix)

    def add_rule(self, rule):
        self.rules.add(rule)

    def set_function(self, name, resource):
        self.functions[name] = resource

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
            self._add_function(path+opts['path'], member, prefix)

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
