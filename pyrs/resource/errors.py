from pyrs import schema
import six

from . import lib
from . import response


class Error(Exception):
    """
    This is the base exception of this framework.
    """
    status = 500
    headers = None
    error = None
    description = None
    uri = None
    details = None

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
        return self.headers or {}

    def get_status(self):
        return self.status

    def get_message(self, debug=False):
        res = {
            'error': self.error or lib.get_fqname(self)
        }
        if self.args:
            res['message'] = list(self.args)
        if self.description:
            res['error_description'] = self.description
        if self.uri:
            res['error_uri'] = self.uri
        details = self.get_details(debug)
        if details:
            res['details'] = details
        return res

    def get_details(self, debug=False):
        details = {}
        if self.details:
            details = self.details.copy()
        if debug:
            details['traceback'] = self.traceback
        return details


class ValidationError(Error):
    status = 500
    error = 'validation_error'


class InputValidationError(Error):
    status = 400
    error = 'invalid_request_format'


class DetailsSchema(schema.Object):
    traceback = schema.Array()


class ErrorSchema(schema.Object):
    error = schema.String(required=True)
    error_description = schema.String()
    error_uri = schema.String()
    message = schema.Array()
    details = DetailsSchema()

    def dump(self, ex):
        if isinstance(ex, Error):
            msg = ex.get_message(self['debug'])
        else:
            msg = self.get_generic_message(ex)
        return super(ErrorSchema, self).dump(msg)

    def get_generic_message(self, ex):
        msg = {
            'error': lib.get_fqname(ex)
        }
        if ex.args:
            msg['message'] = list(ex.args)
        if ex.__dict__:
            msg['details'] = ex.__dict__
        return msg


class ErrorResponse(response.Response):

    def setup(self):
        self.processor = ErrorSchema(debug=self.app['debug'])
        if isinstance(self.content, Error):
            self.status = self.content.get_status()
            self.headers = self.content.get_headers()
        else:
            self.status = 500
            self.headers = {}
