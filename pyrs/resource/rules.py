import inspect

from werkzeug import routing

from . import operations


class Caller(object):
    def __init__(self, target):
        self.target = target

    def __call__(self, *args, **kwargs):
        return self.target(*args, **kwargs)


class InstanceMethodCaller(Caller):

    def __init__(self, target, instance):
        func = getattr(target, '__func__', target)
        super(InstanceMethodCaller, self).__init__(func)
        self.instance = instance

    def __call__(self, *args, **kwargs):
        return super(InstanceMethodCaller, self).__call__(
            self.instance, *args, **kwargs
        )


class ClassMethodCaller(InstanceMethodCaller):

    def __init__(self, target, klass):
        super(ClassMethodCaller, self).__init__(
            target, klass()
        )


class MidPoint(object):

    def __init__(self, caller, path=None, operation=None):
        self.caller = caller
        self.path = operations.Path(path or '')
        self.operation = operation or {}
        self.inject = self.get('envelope', False)
        if self.inject is True:
            self.inject = 'e'

    def __getitem__(self, name):
        return self.operation[name]

    def get(self, name, default=None):
        return self.operation.get(name, default)

    def __call__(self, envelope, **kwargs):
        if self.inject:
            kwargs.update({self.inject: envelope})
        return self.caller(**kwargs)


class Endpoint(MidPoint):

    def __init__(self, name, path, target, operation):
        super(Endpoint, self).__init__(target, path, operation)
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Endpoint '"+self.name+"'>"


class Mount(routing.RuleFactory):

    def __init__(self, path, resource):
        self.path = operations.Path(path.rstrip('/'))
        self.resource = resource

    def get_rules(self, map):
        if inspect.isfunction(self.resource):
            return self.get_method_rules(
                basepath=self.path,
                method=self.resource,
                dispatch=self.resource,
                map=map
            )
        if inspect.isclass(self.resource):
            return self.get_class_rules(
                basepath=self.path,
                klass=self.resource,
                map=map
            )

    def get_method_rules(self, basepath, method, dispatch, map):
        descriptor = method._descriptor_
        methods = descriptor['methods']
        paths = descriptor.get('paths', [''])
        for path in paths:
            endpoint = Endpoint(
                descriptor['fqname'], path, method, descriptor)
            yield routing.Rule(
                basepath+path, methods=methods, endpoint=endpoint
            )

    def get_class_rules(self, basepath, klass, map):
        members = self._get_members(klass)
        for member in members:
            if isinstance(member._descriptor_, operations.Forward):
                rules = self.get_forwarded_rules(basepath, member, map)
            else:
                rules = self.get_method_rules(basepath, member, member, map)
            for rule in rules:
                yield rule

    def get_forwarded_rules(self, basepath, method, map):
        descriptor = method._descriptor_
        path = descriptor['path']
        resource = descriptor['resource']
        for rule in self.get_class_rules(basepath+path, resource, map):
            yield rule

    def _get_members(self, klass):
        members = [
            member for name, member in filter(
                lambda m: hasattr(m[1], '_descriptor_'),
                inspect.getmembers(klass)
            )
        ]
        return sorted(members, key=lambda m: m._descriptor_._create_index)
