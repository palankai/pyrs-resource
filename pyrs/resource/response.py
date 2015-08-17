class Response(object):
    """Generic response class"""

    def __init__(self, body, status=200, headers={}):
        self.body = body
        self.status = status
        self.headers = headers
