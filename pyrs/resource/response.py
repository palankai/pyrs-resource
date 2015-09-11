import inspect
import json

from werkzeug import wrappers

from pyrs import schema

from . import lib


class Response(wrappers.Response):

    producer = None

    def setup(self, meta):
        self.meta = meta

    @property
    def text(self):
        return self.get_data(True)

    @property
    def json(self):
        return json.loads(self.text)

    def set_data(self, value):
        super(Response, self).set_data(value)

    def get_data(self, as_text=False):
        return super(Response, self).get_data(as_text=as_text)

    data = property(get_data, set_data)


class ResponseBuilder(object):
    """Generic response class"""

    def __init__(self, content, app=None, opts=None, request=None):
        self.content = content
        self.app = app or lib.get_config()
        self.opts = opts or {}
        self.request = request
        self.setup()

    def setup(self):
        self.processor = self.opts.get(
            self.app['option_response_name']
        )
        if inspect.isclass(self.processor):
            self.processor = self.processor()
        self.status = self.opts.get(
            self.app['option_status_name'], self.app['option_status']
        )
        self.headers = self.opts.get(
            self.app['option_headers_name'], {}
        )

    def build(self):
        if isinstance(self.content, Response):
            return self.content
        status = self.status
        headers = self.headers.copy()
        content = self.content
        if isinstance(content, tuple):
            if len(content) == 3:
                content, status, headers_update = content
                headers.update(headers_update)
            if len(content) == 2 and isinstance(content[1], int):
                content, status = content
            if len(content) == 2 and isinstance(content[1], dict):
                content, headers_update = content
                headers.update(headers_update)
        if isinstance(self.processor, schema.Schema):
            headers['Content-Type'] = 'application/json'
            writer = schema.JSONWriter(self.processor)
            content = writer.write(content)
        return Response(response=content, status=status, headers=headers)
