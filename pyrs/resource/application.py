from . import response


class Application(object):

    def __init__(self, builder, adapter):
        self._builder = builder
        self._adapter = adapter

    def dispatch(self, method, path):
        key, kwargs = self.match(method, path)
        endpoint = self._builder.endpoints[key]
        res = self.execute(endpoint, kwargs)
        return res.content, res.status, res.headers

    def disp(self, method, path):
        def ex(name, kwargs):
            return 1
        return self._adapter.dispatch(ex, path, method)

    def execute(self, endpoint, kwargs):
        content = endpoint()
        if isinstance(content, response.Response):
            return content
        res = self._builder.make_response(endpoint)
        res.update(content, endpoint)
        return res

    def match(self, method, path):
        return self._adapter.match(path, method)


class Executer(object):

    def __init__(self, endpoints, query=None, body=None, headers=None):
        self.endpoints = endpoints
        self.query = query
        self.body = body
        self.headers = headers

    def __call__(self, endpoint, kwargs):
        resource = self.endpoints[endpoint]
        return resource(**kwargs)
