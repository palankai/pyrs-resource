from . import lib


class Response(object):
    """Generic response class"""

    def __init__(self):
        pass

    def update(self, content, endpoint):
        self.content = content
        self.status = lib.get_options(endpoint, 'status')
        self.headers = {}


class SchemaResponse(Response):
    pass
