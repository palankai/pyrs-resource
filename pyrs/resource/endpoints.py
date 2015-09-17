import functools

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


def init(_target_, **extra):
    name = extra.pop('name', _target_.__name__)
    extra.pop('realname', None)
    extra.pop('target', None)
    if not hasattr(_target_, '_endpoint_'):
        _target_._endpoint_ = Endpoint(name)
        _target_._endpoint_['name'] = name
        _target_._endpoint_['realname'] = _target_.__name__
        _target_._endpoint_['target'] = _target_
    _target_._endpoint_.update(extra)
    return _target_


def decorator(f=None, base=None):
    def decorate(f):
        @functools.wraps(f)
        def wrapper(self, _target_, *args, **kwargs):
            if isinstance(_target_, Endpoint):
                kwargs.pop('realname', None)
                kwargs.pop('target', None)
                _target_.update(kwargs)
                if base:
                    base(self, _target_, **kwargs)
                f(self, _target_, *args, **kwargs)
            else:
                init(_target_, **kwargs)
                if base:
                    base(self, _target_, **kwargs)
                f(self, _target_._endpoint_, *args, **kwargs)
            return _target_

        def inner(self, _target_=None, *args, **kwargs):
            def decorate(_target_):
                return wrapper(self, _target_, *args, **kwargs)
            if _target_ is not None:
                return decorate(_target_)
            return decorate
        inner.f = wrapper
        return inner
    if f is not None:
        return decorate(f)
    return decorate


class Factory(object):

    @decorator
    def RESOURCE(self, _endpoint_, **kwargs):
        pass

    @decorator
    def PATH(self, _endpoint_, path='/', **extra):
        _endpoint_['paths'] = map(Path, lib.ensure_list(path))

    @decorator(base=PATH)
    def GET(self, _endpoint_, **extra):
        _endpoint_['methods'] = self._get_methods(_endpoint_, extra, ['GET'])

    @decorator(base=PATH)
    def POST(self, _endpoint_, **extra):
        _endpoint_['methods'] = self._get_methods(_endpoint_, extra, ['POST'])

    @decorator(base=PATH)
    def PUT(self, _endpoint_=None, **extra):
        _endpoint_['methods'] = self._get_methods(_endpoint_, extra, ['PUT'])

    @decorator(base=PATH)
    def DELETE(self, _endpoint_=None, **extra):
        _endpoint_['methods'] = \
            self._get_methods(_endpoint_, extra, ['DELETE'])

    @decorator(base=PATH)
    def PATCH(self, _endpoint_=None, **extra):
        _endpoint_['methods'] = \
            self._get_methods(_endpoint_, extra, ['PATCH'])

    @decorator(base=PATH)
    def RPC(self, _endpoint_=None, **extra):
        _endpoint_['methods'] = \
            self._get_methods(_endpoint_, extra, ['POST'])

    def _get_methods(self, _endpoint_, extra, default):
        default = default + extra.get('methods', [])
        methods = _endpoint_.get('methods', [])
        return list(set(methods + default))


factory = Factory()

GET = factory.GET
POST = factory.POST
PUT = factory.PUT
DELETE = factory.DELETE
PATCH = factory.PATCH
RPC = factory.RPC
