from pyrs import schema
import six

from . import lib
from . import response


class Error(Exception):
    """
    This is the base exception of this framework.
    The response based on this exception will be a JSON data
    """

    #: HTTP status code (default=500)
    status = 500

    #: HTTP Response headers, (default None processed as empty)
    headers = None

    #: Error code should be a string. If it's not specified the class fully
    #: qualified name will be used
    error = None

    #: Description of error. Should give details about the error
    #: In the message it will appearing as error_description
    description = None

    #: Reference for this error. You can pointing out a documentation which
    #: gives more information about how could this error happen and how could
    #: be possible to avoid
    uri = None

    #: None used as empty dict. Gives extra information about this error which
    #: could be parsed by the consumer of API.
    details = None

    #: You can specify your schema class for validating your message
    #: By default the application default error schema the `ErrorSchema` will
    #: be used
    schema = None

    def __init__(self, *args, **details):
        super(Error, self).__init__(*args)
        if six.PY3:
            self.traceback = lib.parse_traceback(self.__traceback__)
            cause = self.__cause__ or self.__context__
        else:
            self.traceback = lib.get_traceback()
            cause = None
        self.cause = details.pop('cause', cause)
        self.details = details

    def get_headers(self):
        """
        This method gives back the header property by default or an empty dict,
        but you can override, then provide special headers based on the context
        """
        return self.headers or {}

    def get_status(self):
        """
        This method gives back the status property by default which will be
        threated as HTTP status code. You can override, then provide your own
        status code based on the context.
        """
        return self.status

    def get_details(self, debug=False):
        """
        Gives back detailed information about the error and the context.
        As this is part of the message should conform with the `DetailsSchema`.
        """
        return {}

    @classmethod
    def wrap(cls, original):
        """
        Wraps the exception gives back an `Error` instance. The created `Error`
        instance `error` property will be updated by the fully qualified name
        of the `original` exception.
        You could use it for `Error` instances as well, though is not
        recommended.
        """
        ex = cls(*original.args, cause=original)
        ex.error = lib.get_fqname(original)
        return ex


class ClientError(Error):
    """
    Generic Client Error. Normally the client errors have 4xx status codes.
    """
    status = 400


class ValidationErrorX(Error):
    status = 500
    error = 'validation_error'


class InputValidationErrorX(Error):
    status = 400
    error = 'invalid_request_format'


class DetailsSchema(schema.Object):
    """
    Details part of the error schema. Additional properties possible.
    """
    traceback = schema.Array()
    args = schema.Array()

    class Attrs:
        additional = True


class ErrorSchema(schema.Object):
    """
    Describe how the error response should look like. Goal of this schema is
    a minimalistic but usable error response.
    """
    error = schema.String(required=True)
    error_description = schema.String()
    error_uri = schema.String()
    message = schema.String()
    details = DetailsSchema()

    def to_raw(self, value, context=None):
        raw = {
            'error': value.error or lib.get_fqname(value)
        }
        if value.args and value.args[0]:
            raw['message'] = value.args[0]
        if value.description:
            raw['error_description'] = value.description
        if value.uri:
            raw['error_uri'] = value.uri
        details = self.get_details(value)
        if details:
            raw['details'] = details
        return raw

    def get_details(self, ex):
        """
        Gives back detailed information about the error and the context.
        By default its an empty dictionary. The `debug` depends on the debug
        parameter should give back traceback information and the positional
        arguments of the exception.
        As this is part of the message should conform with the `ErrorSchema`.
        """
        details = {}
        if ex.details:
            details = ex.details.copy()
        if self.get_attr('debug', False):
            details['traceback'] = ex.traceback
            details['args'] = ex.args[1:]
        details.update(ex.get_details(self.get_attr('debug', False)))
        return details


class ErrorResponseBuilder(response.ResponseBuilder):

    def setup(self):
        if not isinstance(self.content, Error):
            self.content = Error.wrap(self.content)
        self.status = self.content.get_status()
        self.headers = self.content.get_headers()
        if self.content.schema:
            self.processor = self.content.schema(
                debug=self.app.config['debug']
            )
        else:
            self.processor = ErrorSchema(debug=self.app.config['debug'])


class BadRequestErrorSchema(ErrorSchema):
    errors = schema.Array()

    def to_raw(self, value, context=None):
        message = super(BadRequestErrorSchema, self).to_raw(
            value, context=context
        )
        if value.errors:
            message['errors'] = value.errors
        return message


class BadRequestError(ClientError):
    """
    Request cannot be processed because of error.
    """

    schema = BadRequestErrorSchema
    error = 'BadRequest'

    def __init__(self, message=None, errors=None, **details):
        super(BadRequestError, self).__init__(message, **details)
        self.errors = errors
