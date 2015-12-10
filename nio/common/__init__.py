"""

    Common definitions

"""

from enum import Enum


class ComponentStatus(Enum):
    """ Component Status

    Status a component can be at any time
    """
    created = 1
    configuring = 2
    configured = 3
    stopping = 4
    stopped = 5
    starting = 6
    started = 7
    error = 8


def get_class(cls):
    """ returns class from string
    """
    from importlib import import_module

    parts = cls.rsplit('.', 1)

    # namespace is in parts[0]
    # class_name is in parts[1]
    m = import_module(parts[0])
    return getattr(m, parts[1])


def get_class_namespace(cls):
    """ returns string from class
    """
    return "{0}.{1}".format(cls.__module__, cls.__name__)
