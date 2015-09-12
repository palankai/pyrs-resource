"""
The entry point of the application wrapped by the Request.
The request tend to be immutable.

Request actually is a builder, it builds request arguments for the endpoint,
can hold extra information about the application about the whole environment
and can be passed to the endpoint as well.
"""
import json

from pyrs import schema
from werkzeug import wrappers
import six

from . import errors


class RequestMixin(object):

    app = None
    options = None

    def setup(self, app):
        self.app = app

    def get_route(self):
        return self.path, self.method

    def get_content_type(self):
        return self.headers.get('Content-Type', None)

    def get_text(self):
        return self.get_data(as_text=True, cache=True, parse_form_data=False)

    def get_form(self):
        if getattr(self, '_form_cache', None) is not None:
            return self._form_cache
        self._form_cache = {}
        for k in self.form:
            self._form_cache[k] = self.form[k]
        self._form_cache.update(self.files)
        return self._form_cache

    def is_form(self):
        return self.headers['Content-Type'] in (
            'application/x-www-form-urlencoded',
            'multipart/form-data'
        )

    def get_body(self):
        if self.is_form():
            return self.get_form()
        return self.get_text()

    def get_consumer(self):
        return self.app.consumers.get(self.get_content_type())

    def get_query_consumer(self):
        return self.app.consumers.get('query')

    def parse(self, options, **kwargs):
        if kwargs:
            options = options.copy()
            options.update(kwargs)
        self.options = options
        consumer = self.get_consumer()
        query_consumer = self.get_query_consumer()
        kwargs = {}
        kwargs.update(self._parse_query(options, query_consumer))
        kwargs.update(self._parse_body(options, consumer))
        return kwargs

    def _parse_query(self, options, consumer):
        option = options.get('query')
        if not option:
            return {}
        if option is True:
            return self.args
        if isinstance(option, six.text_type):
            return {option: self.args}
        value = self._parse_value(self.args, consumer, option)
        if isinstance(option, schema.Schema) and option.get_attr('name'):
            return {option.get_attr('name'): value}
        else:
            return value

    def _parse_body(self, options, consumer):
        if self.method not in ['POST', 'PUT', 'PATCH']:
            return {}
        option = options.get('body')
        if not option:
            return {}
        if option is True and self.is_form():
            return self.get_body()
        if isinstance(option, six.text_type):
            return {option: self.get_body()}
        value = self._parse_value(self.get_body(), consumer, option)
        if isinstance(option, schema.Schema) and option.get_attr('name'):
            return {option.get_attr('name'): value}
        else:
            return {'body': value}

    def _parse_value(self, value, consumer, option):
        """Parse a value based on options.
        The option can be `None` means shouldn't be not parsed
        Can be an instance (or a subclass) of `schema.Object`.
        In that case the schema `load` will be executed
        """
        if option is None or consumer is None:
            return value
        try:
            return consumer(value, option)
        except Exception as ex:
            if getattr(ex, 'errors'):
                raise errors.BadRequestError(errors=ex.errors)
            raise


class Request(RequestMixin, wrappers.Request):

    @classmethod
    def from_values(cls, *args, **kwargs):
        app = kwargs.pop('app', None)
        request = super(Request, cls).from_values(*args, **kwargs)
        request.setup(app)
        return request


def _application_json_writer(value, option):
    if not option:
        return value
    return schema.JSONWriter(option).write(value)


class Response(wrappers.Response):

    @property
    def text(self):
        return self.get_data(True)

    @property
    def json(self):
        return json.loads(self.text)

    def parse(self, request, value=None):
        self.status_code = request.options.get('status', 200)
        self.headers.extend(request.options.get('headers', {}))
        if not self.get_option(request) and not value:
            return
        if isinstance(value, Exception):
            value = self.parse_exception(value, request)
            self.mimetype = request.app.error_mimetype
        elif self.get_option(request):
            value = self.parse_value(value, request)
            self.mimetype = request.headers.get(
                'Accept', request.app.default_mimetype
            )
        self.set_data(value)

    def parse_value(self, value, request):
        if self.get_option(request):
            producer = self.get_producer(request)
            return producer(value, self.get_option(request))

    def parse_exception(self, value, request):
        if not isinstance(value, errors.Error):
            value = errors.Error.wrap(value)
        schema = value.schema
        if not schema:
            schema = errors.ErrorSchema
        option = schema(
            debug=request.app.debug
        )
        self.status_code = value.get_status()
        self.headers.extend(value.get_headers())
        return self.get_error_producer(request)(value, option)

    def get_option(self, request):
        return request.options.get('output')

    def get_producer(self, request):
        return request.app.producers.get(
            request.headers.get(
                'Accept', request.app.default_mimetype
            )
        )

    def get_error_producer(self, request):
        return request.app.producers.get(request.app.error_mimetype)
