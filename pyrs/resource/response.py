import inspect

from pyrs import schema

from . import lib


class Response(object):
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
            content = self.processor.dump(content)
            return (content, status, headers)
        if callable(self.processor):
            return self.processor(content, status, headers)
        return (content, status, headers)
