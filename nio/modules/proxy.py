"""

  Proxy classes and decorator for Modules

"""
from importlib import import_module
from inspect import getmembers, isclass
from nio.util.logging import get_nio_logger


class ProxyNotInitialized(Exception):
    pass


class ModuleProxy(object):

    _module_class = None
    _unproxied_methods = {}
    _logger = get_nio_logger('ModuleProxy')

    def __init__(self, *args, **kwargs):
        """ Handling the instantiation of a ModuleProxy

        Instantiating a ModuleProxy probably means they want to instantiate
        the module implementation class instead.

        By setting the __class__ attribute, the instance will have access to
        the instance level methods provided by the module implementation.
        In all likelihood, these will not be called by the person using the
        interface, but it can often be useful for the implementation itself
        to define its own helper methods.
        """

        # Check that we have defined our module_class already
        if isclass(self._module_class):

            klass = self.__class__
            # Set the class attribute
            if self.__class__.__name__ == self._module_class.__name__:
                self.__class__ = self._module_class
                klass = self.__class__

            # Now call the constructor they were intending to call, but act
            # like it is our constructor (pass self)
            klass.__init__(self, *args, **kwargs)

    @classmethod
    def initialize(cls, module_name, defined_module, module_locations):
        """ Initialize a ModuleProxy by proxying any flagged methods

        This method will use the configured values to import the proper module
        and then discover any proxied methods and point them to the proper
        module implementation. This method should be called before any proxied
        methods are called.

        Args:
            module_name (str): The name of the module to proxy (i.e. scheduler)
            defined_module (str): The name of the module implementation to
                import
        """
        cls._logger = get_nio_logger('{0}ModuleProxy'.format(module_name))
        if cls._unproxied_methods.get(cls.__name__, None):
            raise RuntimeError("%s already initialized !!!")

        for prefix in module_locations:
            module_package = "{0}.{1}.{2}".format(prefix, module_name,
                                                  defined_module)
            try:
                cls.initialize_from_package(module_package)
                return True
            except ImportError:
                cls._logger.info(
                    "Failed to import module {0} from package {1}.{2}".format(
                        defined_module, prefix, module_name),
                    exc_info=True)
            except:
                cls._logger.exception("Error importing module")

        raise ProxyNotInitialized()

    @classmethod
    def initialize_from_package(cls, module_package):
        # The module containing the implemented module (confusing...)
        module_module = import_module(module_package)

        # The class inside of the module that corresponds to this class
        proxied_class = getattr(module_module, cls.__name__, None)

        if proxied_class:
            # Redirect proxied members
            cls._module_class = proxied_class
            cls._setup_proxied_members()
        else:
            # Proxied class not found, raise an Exception
            raise Exception("Proxied class {0} not found in {1}".format(
                cls.__name__, module_package))

    @classmethod
    def finalize(cls):
        """ ModuleProxy to original class methods """
        cls._module_class = None
        # make sure it has been 'proxied' before
        if cls.__name__ in cls._unproxied_methods:
            orig_methods = cls._unproxied_methods[cls.__name__]
            for name in cls._unproxied_methods[cls.__name__]:
                setattr(cls, name, orig_methods[name])
            cls._unproxied_methods[cls.__name__] = {}

    @classmethod
    def _setup_proxied_members(cls):
        """Redirect any proxied methods inside of the class.

        This method goes through all of the members in the class and redirects
        anything proxied to the attribute on the module implementation class.
        """
        orig_methods = {}
        for (name, member) in getmembers(cls):
            if getattr(member, '_use_proxied_class', False):
                cls._logger.debug("Proxying member {0} to {1}".format(
                    name, cls._module_class))
                orig_methods[name] = member
                setattr(cls, name, getattr(cls._module_class, name))

        cls._unproxied_methods[cls.__name__] = orig_methods


def proxied(target):
    """ A decorator to consider a member "proxied"

    This decorator can be applied to functions/attributes inside of a
    ModuleProxy sub class to have them use their respective implementations
    inside of the module implementation.

    Note: When decorating a class method, make sure that the proxied decorator
    appears after the classmethod decorator in the code, so that it gets
    evaluated first.
    """
    setattr(target, '_use_proxied_class', True)
    return target
