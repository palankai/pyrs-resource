"""
The entry point of the application wrapped by the Request.
The request tend to be immutable.

Request actually is a builder, it builds request arguments for the endpoint,
can hold extra information about the application about the whole environment
and can be passed to the endpoint as well.
"""
import inspect

from pyrs import schema

from . import conf


class Request(object):

    def __init__(
        self, opts, app=None, path=None, query=None, body=None, headers=None
    ):
        self.opts = opts
        self.app = app
        self.path = path or {}
        self.query = query or {}
        self.body = body or {}
        self.headers = headers or {}
        self._conf = conf.defaults.copy()
        self._inject_path = self.opts.get(
            'inject_path', self._conf['inject_path']
        )
        self._inject_query = self.opts.get(
            'inject_query', self._conf['inject_query']
        )
        self._inject_request = self.opts.get(
            'inject_request', self._conf['inject_request']
        )
        self._inject_body = self.opts.get(
            'inject_body', self._conf['inject_body']
        )
        if self._inject_request and self._inject_request is True:
            self._inject_request = self._conf['inject_request_name']

    def __getitem__(self, name):
        return self.headers[name]

    def build(self):
        kwargs = {}
        kwargs.update(self._inject(self._inject_path, self.path))
        kwargs.update(self._inject(
            self._inject_query, self.query,
            self.opts.get(self._conf['query_schema_option'], None)
        ))
        kwargs.update(self._inject(
            self._inject_body, self.body,
            self.opts.get(self._conf['body_schema_option'], None)
        ))
        if self._inject_request:
            kwargs[self._inject_request] = self
        return kwargs

    def _inject(self, inject, value, opt=None):
        if inject:
            value = self._parse_value(value, opt)
            if inject is True:
                return value
            else:
                return {inject: value}
        return {}

    def _parse_value(self, value, opt):
        """Parse a value based on options.
        The option can be `None` means shouldn't be not parsed
        Can be an instance (or a subclass) of `schema.Object`.
        In that case the schema `load` will be executed
        """
        if inspect.isclass(opt) and issubclass(opt, schema.Object):
            return opt().load(value)
        if isinstance(opt, schema.Object):
            return opt.load(value)
        return value
