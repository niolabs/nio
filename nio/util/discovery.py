""" Discoverable type

Classes marked as Discoverable for a given type allow the system to
identify them as belonging to a specific group be registered and
treated accordingly

Some examples are: block, service, etc

"""
from enum import Enum


class DiscoverableType(Enum):

    """Enum specifying the different discoverable types that are possible"""

    block = 1
    service = 2
    module = 3
    component = 4


class Discoverable(object):

    """Decorator for declaring a class as Discoverable"""

    def __init__(self, discoverable_type, **kwargs):
        """ Create a Discoverable with a given type

        Args:
            discoverable_type (DiscoverableType): What type of discoverable
                should this be
        """
        self._disc_type = discoverable_type

    def __call__(self, cls):
        """The decorator method to be called on the class object.

        This method will set the proper discoverable type to the class. It
        should return the class passed in, according to the decorator spec.
        """

        # Set the attribute to the class name, to prevent subclasses from also
        # being discoverable.
        setattr(cls, _discoverable_type_to_attr(self._disc_type), cls.__name__)
        return cls


def _discoverable_type_to_attr(discoverable_type):
    """ Mangles the discoverable type to avoid collisions with other potential
    attributes of the class

    Args:
        discoverable_type (DiscoverableType): Discoverable type to mangle

    Returns:
        Mangled discoverable type
    """
    return "_%{0}%".format(discoverable_type.name)


def class_has_discoverable_type(_class, disc_type):
    """ Returns true if the class has the specified discoverable type

    Args:
        _class (class): The class in question, should be a class object
        disc_type (DiscoverableType): The discoverable type enum to check.
            Should be something like `DiscoverableType.block`

    Returns:
        discoverable (bool): True if the class has the discoverable type
    """
    disc_val = getattr(_class, _discoverable_type_to_attr(disc_type), None)

    # We need the value to not only be set, but to also be set to the right
    # class name. This prevents subclasses from also being discoverable
    return disc_val == _class.__name__
