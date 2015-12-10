"""

  Discoverable type

"""
from enum import Enum


class DiscoverableType(Enum):
    block = 1
    service = 2
    module = 3
    component = 4


def _discoverable_type_to_attr(discoverable_type):
    return "_%{0}%".format(discoverable_type.name)


def class_has_discoverable_type(_class, disc_type):
    """ Returns true if the class has the specified discoverable type

    Args:
        _class (class): The class in question, should be a class object
        disc_type (enum): The discoverable type enum to check. Should be
            something like `DiscoverableType.block`

    Returns:
        discoverable (bool): True if the class has the discoverable type
    """
    disc_val = getattr(_class, _discoverable_type_to_attr(disc_type), None)

    # We need the value to not only be set, but to also be set to the right
    # class name. This prevents subclasses from also being discoverable
    return disc_val == _class.__name__


class Discoverable(object):

    def __init__(self, discoverable_type, **kwargs):
        self._disc_type = discoverable_type

    def __call__(self, cls):
        # Set the attribute to the class name, to prevent subclasses from also
        # being discoverable.
        setattr(cls, _discoverable_type_to_attr(self._disc_type), cls.__name__)
        return cls
