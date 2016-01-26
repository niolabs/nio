"""

    Common definitions

"""

# shortcut to RunnerStatus
from nio.util.runner import RunnerStatus


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
