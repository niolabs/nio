""" Discoverable decorator

Classes marked as Discoverable allow the system to identify them and register
them. While any class can technically be marked discoverable, n.io will tend
to only care about blocks, services, or components that are discoverable.

Note: A class being marked discoverable will not mark its subclasses as
discoverable. Each subclass must be explicitly marked with the discoverable
decorator.

To mark a class as discoverable, use the parameter-less decorator
`discoverable`::

    from nio import discoverable, Block

    @discoverable
    class MyBlock(Block):
        pass

"""


def discoverable(_class):
    """The decorator method to be called on the class object.

    This method will set the proper discoverable type to the class. It
    should return the class passed in, according to the decorator spec.
    """

    # Set the attribute to the class name, to prevent subclasses from also
    # being discoverable.
    setattr(_class, _get_discoverable_attribute(_class), True)
    return _class


def is_class_discoverable(_class):
    """ Returns true if the class is marked discoverable

    Note: discoverability does not extend to subclasses. Each subclass must
    explicitly be marked as discoverable

    Args:
        _class (class): The class in question, should be a class object

    Returns:
        bool: True if the class is discoverable
    """
    return bool(getattr(_class, _get_discoverable_attribute(_class), False))


def _get_discoverable_attribute(_class):
    """ Get an attribute to set on a class to consider it discoverable """
    return "__{}_is_discoverable".format(_class.__name__)
