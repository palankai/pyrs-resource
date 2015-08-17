from . import lib
from . import response


class Application(object):

    def __init__(self, adapter, endpoints):
        self._adapter = adapter
        self._endpoints = endpoints

    def dispatch(self, method, path):
        key, kwargs = self.match(method, path)
        endpoint = self._endpoints[key]
        res = self.execute(endpoint, kwargs)
        return res.body, res.status, res.headers

    def execute(self, endpoint, kwargs):
        opts = lib.get_options(endpoint)
        res = endpoint()
        if isinstance(res, response.Response):
            return res
        return response.Response(res, opts['status'], {})

    def match(self, method, path):
        return self._adapter.match(path, method)
