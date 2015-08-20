import inspect
import logging

from . import conf


def get_logger(obj):
    return logging.getLogger(get_fqname(obj))


def get_fqname(thing):
    if not hasattr(thing, '__name__'):
        return thing.__module__+'.'+thing.__class__.__name__
    return thing.__module__+'.'+thing.__name__


def get_options(resource, key=None, default=None):
    options = getattr(resource, conf.decorate, None)
    if key is not None:
        return options.get(key, default)
    return options


def get_resource_members(resource):
    return [
        member for name, member in filter(
            lambda m: hasattr(m[1], conf.decorate),
            inspect.getmembers(resource)
        )
    ]
