import inspect

import werkzeug

from . import application
from . import lib


class ApplicationBuilder(object):

    def __init__(self):
        self._map = werkzeug.routing.Map()
        self._endpoints = {}

    def bind(self, server_name):
        adapter = self._map.bind(server_name)
        return application.Application(adapter, self._endpoints)

    def add(self, path, resource, prefix=''):
        if inspect.isfunction(resource):
            self._add_function(path, resource, prefix)
        elif inspect.isclass(resource):
            self._add_class(path, resource(), prefix)
        else:
            self._add_class(path, resource, prefix)

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
            self._map.add(rule)
            self._endpoints[name] = resource
        else:
            raise ValueError(
                "The given function (%s) is not and endpoint endpoint"
                % resource
            )

    def _make_rule(self, path, methods, endpoint):
        return werkzeug.routing.Rule(path, methods=methods, endpoint=endpoint)
