"""
The entry point of the application wrapped by the Request.
The request tend to be immutable.

Request actually is a builder, it builds request arguments for the endpoint,
can hold extra information about the application about the whole environment
and can be passed to the endpoint as well.
"""
from pyrs import schema
from werkzeug import wrappers
from werkzeug.test import EnvironBuilder

from . import lib
from . import errors


class RequestMixin(object):

    meta = None
    app = None
    kwargs = None

    @property
    def route(self):
        return self.path, self.method

    @property
    def text(self):
        return self.get_data(as_text=True)

    @property
    def is_form(self):
        return self.headers['Content-Type'] in (
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        )

    @property
    def body(self):
        if self.is_form:
            return self.form
        return self.text

    def begin(self, app):
        self.app = app

    def forward(self, func, kwargs):
        self.func = func
        self.meta = lib.get_meta(func)
        self.kwargs = kwargs
        self.kwargs.update_by_request(self)

    def __call__(self):
        return self.func(**self.kwargs)


class Request(wrappers.Request, RequestMixin):
    pass


class Arguments(dict):

    def __init__(self, meta, kwargs):
        super(Arguments, self).__init__(kwargs)
        self.meta = meta
        self.request = None

    def update_by_request(self, request):
        self.request = request
        self._parse_query()
        self._parse_body()

    def _parse_query(self):
        s = self.meta.get('query')
        value = self._parse_value(self.request.args, s)
        if isinstance(s, schema.Schema) and s.get_attr('name'):
            self.update({s.get_attr('name'): value})
        else:
            self.update(value)

    def _parse_body(self):
        if self.request.method not in ['POST', 'PUT', 'PATCH']:
            return
        s = self.meta.get('body')
        value = self._parse_value(self.request.body, s)
        if isinstance(s, schema.Schema) and s.get_attr('name'):
            self.update({s.get_attr('name'): value})
        else:
            self.update({'body': value})

    def _parse_value(self, value, opt):
        """Parse a value based on options.
        The option can be `None` means shouldn't be not parsed
        Can be an instance (or a subclass) of `schema.Object`.
        In that case the schema `load` will be executed
        """
        if opt is None:
            return value
        reader = schema.JSONFormReader(opt)
        try:
            return reader.read(value)
        except schema.ValidationErrors as ex:
            raise errors.BadRequestError(errors=ex.errors)


def req(*args, **kwargs):
    env_builder = EnvironBuilder(*args, **kwargs)
    return Request(env_builder.get_environ())


class RequestOld(object):
    """
    This builder class responsible to gather all of necessary information
    about the request and build the arguments of actual method.
    """

    def __init__(
        self, opts=None, app=None, path=None,
        auth=None, cookies=None, session=None
    ):
        self.app = app or lib.get_config()
        self.auth = auth
        self.cookies = cookies
        self.opts = opts or {}
        self.path = path or {}
        self.session = session

        self._setup_injects()

    def build(self):
        """
        Build kwargs for calling the method.

        :raises pyrs.resource.errors.BadRequestError:
        """
        kwargs = self.path
        kwargs.update(self._inject(self._inject_app, self.app))
        kwargs.update(self._inject(self._inject_auth, self.auth))
        kwargs.update(self._inject(self._inject_cookies, self.cookies))
        kwargs.update(self._inject(self._inject_request, self))
        kwargs.update(self._inject(self._inject_session, self.session))
        return kwargs

    def __getitem__(self, name):
        return self.headers[name]

    def _setup_injects(self):
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
        if opt is None:
            return value
        reader = schema.JSONFormReader(opt)
        try:
            return reader.read(value)
        except schema.ValidationErrors as ex:
            raise errors.BadRequestError(errors=ex.errors)
