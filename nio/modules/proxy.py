"""

  Proxy classes and decorator for Modules

"""
from collections import defaultdict
from inspect import getmembers, isfunction, ismethod, isroutine
from nio.util.logging import get_nio_logger


class ProxyNotProxied(Exception):
    pass


class ProxyAlreadyProxied(Exception):
    pass


class ModuleProxy(object):

    # Whether or not this class has already been proxied
    proxied = False
    _unproxied_methods = defaultdict(dict)
    _logger = get_nio_logger('ModuleProxy')

    @classmethod
    def proxy(cls, class_to_proxy):
        """ Initialize a ModuleProxy by proxying any methods

        This will proxy the class by applying methods from the class passed
        in to the method to the proxy interface. This method should be called
        before any proxied methods are called.

        Args:
            class_to_proxy (class): A reference to the class to proxy on top
                of this interface

        Raises:
            ProxyAlreadyProxied: If the proxy has already been proxied
        """
        if cls.proxied:
            raise ProxyAlreadyProxied()

        # Iterate through the members of the proxy implementation class
        for (name, impl_member) in getmembers(class_to_proxy):
            # Make sure this is a method we want to proxy
            if not cls._is_proxyable(name, impl_member):
                continue

            interface_member = getattr(cls, name, None)
            cls._logger.debug("Proxying member {0} from {1}".format(
                name, class_to_proxy.__name__))
            # Save a reference to the original member to replace during unproxy
            cls._unproxied_methods[cls.__name__][name] = interface_member
            setattr(cls, name, impl_member)

        # Mark the class as proxied
        cls.proxied = True

    @classmethod
    def unproxy(cls):
        """ Return the ModuleProxy to its original class methods

        Raises:
            ProxyNotProxied: If the proxy has not yet been proxied
        """
        if not cls.proxied:
            raise ProxyNotProxied()

        for name, iface_member in cls._unproxied_methods[cls.__name__].items():
            if iface_member is None:
                # We didn't have this member on the original interface, delete
                delattr(cls, name)
            else:
                # We had this member originally, replace it with that one
                setattr(cls, name, iface_member)

        # Reset all of our cached proxy class information
        cls._unproxied_methods[cls.__name__] = {}
        cls.proxied = False

    @classmethod
    def _is_proxyable(cls, name, member):
        """Returns True if a member is proxy-able.

        Here is what we want to proxy:
            * The __init__ constructor
            * Any non-private instance functions
            * Any non-private class methods
            * Any non-private class variables
        """
        return (name == '__init__' or not name.startswith('__')) and \
            (isfunction(member) or ismethod(member) or not isroutine(member))
