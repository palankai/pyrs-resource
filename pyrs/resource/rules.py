from werkzeug import routing

from . import endpoints


class Mount(routing.RuleFactory):

    def __init__(self, path, resource):
        self.path = endpoints.Path(path.rstrip('/'))
        self.resource = resource

    def get_rules(self, map):
        return self.get_method_rules(map)

    def get_method_rules(self, map):
        endpoint = self.resource._endpoint_
        methods = endpoint['methods']
        paths = endpoint.get('paths', [''])
        for path in paths:
            yield routing.Rule(
                self.path+path, methods=methods, endpoint=endpoint
            )
