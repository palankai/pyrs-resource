import six

from . import lib


class Path(six.text_type):

    @property
    def template(self):
        if not hasattr(self, '_template'):
            self._parse()
        return self._template

    @property
    def args(self):
        if not hasattr(self, '_args'):
            self._parse()
        return self._args

    def _parse(self):
        self._template, self._args = lib.parse_path(self)

    def __add__(self, other):
        return self.__class__(six.text_type(self) + other)

    def __mod__(self, kwargs):
        return self.format(**kwargs)

    def format(self, **kwargs):
        return self.template.format(**kwargs)


class Endpoint(dict):

    def __init__(self, name, *args, **kwargs):
        super(Endpoint, self).__init__(*args, **kwargs)
        self['name'] = name

    def __hash__(self):
        return hash(self['name'])

    def __eq__(self, other):
        if isinstance(other, Endpoint):
            return self['name'] == other['name']
        return self['name'] == other

    def __repr__(self):
        return repr(self['name'])

    def __str__(self):
        return self['name']

    def copy(self):
        data = super(Endpoint, self).copy()
        return self.__class__(data.pop('name'), **data)

    @property
    def parent(self):
        return self.get('parent', self)

    @property
    def root(self):
        _root = self
        while _root.get('parent'):
            _root = _root['parent']
        return _root

    @property
    def chain(self):
        if not self.get('parent'):
            return [self]
        return self.parent.chain + [self]

    @property
    def name(self):
        return self['name']

    @property
    def fqname(self):
        return ".".join(map(lambda x: x['name'], self.chain))


class Factory(object):

    def GET(self, _target_=None, path=None, methods=None, **extra):
        decorate = self.ENDPOINT(path, methods or ['GET'], **extra)
        return _target_ and decorate(_target_) or decorate

    def POST(self, _target_=None, path=None, methods=None, **extra):
        decorate = self.ENDPOINT(path, methods or ['POST'], **extra)
        return _target_ and decorate(_target_) or decorate

    def PUT(self, _target_=None, path=None, methods=None, **extra):
        decorate = self.ENDPOINT(path, methods or ['PUT'], **extra)
        return _target_ and decorate(_target_) or decorate

    def DELETE(self, _target_=None, path=None, methods=None, **extra):
        decorate = self.ENDPOINT(path, methods or ['DELETE'], **extra)
        return _target_ and decorate(_target_) or decorate

    def PATCH(self, _target_=None, path=None, methods=None, **extra):
        decorate = self.ENDPOINT(path, methods or ['PATCH'], **extra)
        return _target_ and decorate(_target_) or decorate

    def RPC(self, _target_, path=None, methods=None, **extra):
        decorate = self.ENDPOINT(path, methods or ['POST'], **extra)
        return _target_ and decorate(_target_) or decorate

    def ENDPOINT(self, path, methods, **extra):
        def decorate(target):
            self.make(target, extra)
            self._update_path(target, path)
            self._update_methods(target, methods)
            return target
        return decorate

    def PATH(self, path):
        def decorate(_target_):
            self.make(_target_)
            self._update_path(_target_, path)
            return _target_
        return decorate

    def RESOURCE(self, _target_=None, **extra):
        def decorate(target):
            self.make(target, extra)
            return target
        return _target_ and decorate(_target_) or decorate

    def make(self, target, extra=None):
        if extra is None:
            extra = {}
        name = extra.pop('name', target.__name__)
        if not hasattr(target, '_endpoint_'):
            target._endpoint_ = Endpoint(name)
            target._endpoint_['realname'] = target.__name__
            target._endpoint_['target'] = target
        target._endpoint_.update(extra)
        return target

    def _update_path(self, target, path):
        if not path:
            return
        paths = target._endpoint_.get('paths') or []
        paths.extend(map(Path, lib.ensure_list(path)))
        target._endpoint_['paths'] = paths

    def _update_methods(self, target, default):
        endpoint = target._endpoint_
        methods = endpoint.get('methods', [])
        endpoint['methods'] = list(set(methods + default))


factory = Factory()

GET = factory.GET
POST = factory.POST
PUT = factory.PUT
DELETE = factory.DELETE
PATCH = factory.PATCH
RPC = factory.RPC
