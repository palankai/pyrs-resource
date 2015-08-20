import inspect

import werkzeug
from pyrs import schema

from . import application
from . import lib
from . import response


class ApplicationBuilder(object):

    def __init__(self):
        self.rules = werkzeug.routing.Map()
        self.endpoints = {}
        self.default_response_cls = response.Response

    def bind(self, server_name):
        adapter = self.rules.bind(server_name)
        return application.Application(self, adapter)

    def add(self, path, resource, prefix=''):
        if inspect.isfunction(resource):
            self._add_function(path, resource, prefix)
        elif inspect.isclass(resource):
            self._add_class(path, resource(), prefix)
        else:
            self._add_class(path, resource, prefix)

    def add_rule(self, rule):
        self.rules.add(rule)

    def set_endpoint(self, name, resource):
        self.endpoints[name] = resource

    def make_response(self, endpoint):
        res = lib.get_options(endpoint, 'response')
        if res is None:
            return self.default_response_cls()
        if inspect.isclass(res):
            res = res()
        if isinstance(res, response.Response):
            return res
        if isinstance(res, schema.Schema):
            return response.SchemaResponse()
        raise ValueError("Unable to process the response")

    def lookup(self, name):
        return self.endpoints[name]

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
            self.set_endpoint(name, resource)
        else:
            raise ValueError(
                "The given function (%s) is not and endpoint endpoint"
                % resource
            )

    def _make_rule(self, path, methods, endpoint):
        return werkzeug.routing.Rule(path, methods=methods, endpoint=endpoint)
