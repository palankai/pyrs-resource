from . import lib


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

    def make(self, target, **extra):
        endpoint = Endpoint(target.__name__)
        endpoint['fqname'] = lib.fqname(target)
        target.__endpoint__ = endpoint
        return target
