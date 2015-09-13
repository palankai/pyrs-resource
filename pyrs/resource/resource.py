from . import conf
from . import lib

"""
This module mainly define decorators for resources
"""


def endpoint(_func=None, path="/", **kwargs):
    """
    Deadly simple decorator, add options to the given function.
    Can be user with or without any keyword arguments.
    The default options would contain the path and the name of the function.
    Based on configuration: :py:data:`.conf.decorate`
    """
    parsed_path, args = lib.parse_path(path)

    def decorator(_func):
        if not hasattr(_func, conf.decorate):
            setattr(_func, conf.decorate, {})
        getattr(_func, conf.decorate).update(kwargs)
        getattr(_func, conf.decorate).update({
            'werkzeug_path': path,
            'path': parsed_path,
            'args': args,
            'name': kwargs.pop('name', _func.__name__),
            'status': kwargs.pop('status', 200),
        })
        return _func
    if _func is not None:
        return decorator(_func)
    return decorator


def GET(_func=None, **kwargs):
    """
    Decorator function
    Ensure the given function will be available for GET method
    """
    return endpoint(_func, methods=['GET'], **kwargs)


def POST(_func=None, **kwargs):
    """
    Decorator function
    Ensure the given function will be available for POST method
    """
    return endpoint(
        _func, methods=['POST'], status=kwargs.pop('status', 201), **kwargs
    )


def RPC(_func=None, **kwargs):
    """
    Decorator function
    Ensure the given function will be available for POST method
    This action tend to use as Remote procedure call
    """
    return endpoint(
        _func, methods=['POST'], **kwargs
    )


def PUT(_func=None, **kwargs):
    """
    Decorator function
    Ensure the given function will be available for PUT method
    """
    return endpoint(_func, methods=['PUT'], **kwargs)


def DELETE(_func=None, **kwargs):
    """
    Decorator function
    Ensure the given function will be available for DELETE method
    """
    return endpoint(_func, methods=['DELETE'], **kwargs)


def PATCH(_func=None, **kwargs):
    """
    Decorator function
    Ensure the given function will be available for PATCH method
    """
    return endpoint(_func, methods=['PATCH'], **kwargs)
