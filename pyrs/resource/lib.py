import inspect
import logging
import traceback
import sys


from . import conf


def get_logger(obj):
    return logging.getLogger(get_fqname(obj))


def get_fqname(thing):
    if isinstance(thing, type):
        return thing.__module__+'.'+thing.__name__
    if isinstance(thing, Exception):
        return thing.__class__.__module__+'.'+thing.__class__.__name__
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


def get_config(update=None):
    config = {}
    for k in dir(conf):
        if not k.startswith('_'):
            config[k] = getattr(conf, k)
    config.update(update or {})
    return config


def get_traceback():
    unused, unused, exc_traceback = sys.exc_info()
    return parse_traceback(exc_traceback)


def parse_traceback(trace):
    rows = []
    for row in traceback.extract_tb(trace):
        rows.append("%s:%s %s() %s" % (row[0], row[1], row[2], row[3]))
    rows.reverse()
    return rows
