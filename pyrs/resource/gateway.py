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


def _text_plain(value, option):
    return value


def _application_json_reader(value, option):
    return schema.JSONReader(option).read(value)


def _form_reader(value, option):
    return schema.JSONFormReader(option).read(value)


def _application_json_writer(value, option):
    return schema.JSONWriter(option).write(value)


class RequestMixin(object):

    consumers = {
        None: _application_json_reader,
        'query': _form_reader,
        'text/plain': _text_plain,
        'application/json': _application_json_reader,
        'application/x-www-form-urlencoded': _form_reader,
        'multipart/form-data': _form_reader
    }

    def get_content_type(self):
        return self.headers.get('Content-Type') or None

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
        return self.consumers.get(self.get_content_type())

    def get_query_consumer(self):
        return self.consumers.get('query')

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
        except schema.exceptions.SchemaError as ex:
            raise errors.BadRequestError(
                *ex.args,
                errors=getattr(ex, 'errors', None)
            )


class CompatibilityMixin(object):

    @property
    def text(self):
        return self.get_data(as_text=True)

    @property
    def json(self):
        return json.loads(self.text)


class ExceptionMixin(object):

    error_mimetype = 'application/json'

    def produce_exception(self, ex):
        self.mimetype = self.error_mimetype
        if not isinstance(ex, errors.Error):
            ex = errors.Error.wrap(ex)
        option = ex.schema(debug=self.debug)
        self.status_code = ex.get_status()
        self.headers.extend(ex.get_headers())
        self.set_data(schema.JSONWriter(option).write(ex))
        return self

    @classmethod
    def from_exception(cls, ex):
        return cls().produce_exception(ex)


class ProducerMixin(object):

    _request_parsed = False

    producers = {
        'text/plain': _text_plain,
        'application/json': _application_json_writer,
    }

    debug = False

    def produce(self, request, value=''):
        self.set_data(self._parse_value(request, value))
        return self

    def _parse_value(self, request, value):
        self.parse_request(request)
        if self._get_option(request):
            producer = self._get_producer(request)
            return producer(value, self._get_option(request))
        return value or ''

    def parse_request(self, request):
        self.mimetype = request.headers.get(
            'Accept', self.default_mimetype
        )
        if hasattr(request, 'options'):
            self.headers.extend(request.options.get('headers', {}))
        if self._request_parsed:
            return
        self._request_parsed = True
        if hasattr(request, 'options'):
            self.status_code = request.options.get('status', self.status_code)

    def _get_option(self, request):
        return request.options.get('output')

    def _get_producer(self, request):
        return self.producers.get(
            request.headers.get(
                'Accept', self.default_mimetype
            )
        )


class Request(wrappers.Request, RequestMixin):
    pass


class Response(
    wrappers.Response, CompatibilityMixin, ProducerMixin,
    ExceptionMixin
):
    default_mimetype = 'application/json'


class Envelope(object):

    Response = Response

    def __init__(self, request):
        self.request = request

    @property
    def response(self):
        if not getattr(self, '_response', None):
            self._response = self.Response()
            self._response.parse_request(self.request)
        return self._response
