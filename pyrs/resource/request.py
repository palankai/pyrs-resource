"""
The entry point of the application wrapped by the Request.
The request tend to be immutable.

Request actually is a builder, it builds request arguments for the endpoint,
can hold extra information about the application about the whole environment
and can be passed to the endpoint as well.
"""
import inspect

from pyrs import schema
import jsonschema

from . import lib
from . import errors


class Request(object):

    def __init__(
        self, opts, app=None, path=None, query=None, body=None, headers=None,
        auth=None, cookies=None, session=None
    ):
        self.app = app or lib.get_config()
        self.auth = auth
        self.body = body or {}
        self.cookies = cookies
        self.headers = headers or {}
        self.opts = opts
        self.path = path or {}
        self.query = query or {}
        self.session = session

        self._setup_injects()

    def build(self):
        kwargs = {}
        kwargs.update(self._inject(
            self._inject_body, self.body,
            self.opts.get(self.app['body_schema_option'], None)
        ))
        kwargs.update(self._inject(self._inject_path, self.path))
        kwargs.update(self._inject(
            self._inject_query, self.query,
            self.opts.get(self.app['query_schema_option'], None)
        ))
        kwargs.update(self._inject(self._inject_app, self.app))
        kwargs.update(self._inject(self._inject_auth, self.auth))
        kwargs.update(self._inject(self._inject_cookies, self.cookies))
        kwargs.update(self._inject(self._inject_request, self))
        kwargs.update(self._inject(self._inject_session, self.session))
        return kwargs

    def __getitem__(self, name):
        return self.headers[name]

    def _setup_injects(self):
        self._inject_body = self._get_inject('inject_body', False)
        self._inject_path = self._get_inject('inject_path', False)
        self._inject_query = self._get_inject('inject_query', False)

        self._inject_app = self._get_inject('inject_app', True)
        self._inject_auth = self._get_inject('inject_auth', True)
        self._inject_cookies = self._get_inject('inject_cookies', True)
        self._inject_request = self._get_inject('inject_request', True)
        self._inject_session = self._get_inject('inject_session', True)

    def _get_inject(self, name, force_kwargs=False):
        inject = self.opts.get(
            name, self.app[name]
        )
        if force_kwargs and inject is True:
            inject = self.app[name+'_name']
        return inject

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
            opt = opt()
        if isinstance(opt, schema.Object):
            try:
                return opt.load(value)
            except jsonschema.exceptions.ValidationError as ex:
                raise errors.InputValidationError(cause=ex)
        return value
