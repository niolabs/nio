from inspect import isclass
from nio.util.logging import get_nio_logger

# Module proxy interfaces
from nio.modules.scheduler import Job
from nio.modules.persistence import Persistence
from nio.modules.communication.publisher import Publisher
from nio.modules.communication.subscriber import Subscriber
from nio.modules.security.auth import Authenticator
from nio.modules.security.roles import RolesProvider
from nio.modules.security.permissions import PermissionsProvider
from nio.modules.web import WebEngine


class ModuleInitializer(object):

    """ A class that proxies and unproxies modules """

    def __init__(self):
        self.logger = get_nio_logger('ModuleInitializer')
        self._module_implementations = {}
        self._initialized_modules = []
        self._module_interfaces = {
            'scheduler': Job,
            'persistence': Persistence,
            'publisher': Publisher,
            'subscriber': Subscriber,
            'authenticator': Authenticator,
            'roles': RolesProvider,
            'permissions': PermissionsProvider,
            'web_engine': WebEngine
        }

    def initialize(self, **kwargs):
        """ Initialize and proxy any registered proxy implmentations.

        This function will proxy any implmentations that have been registered
        with this ModuleInitializer. You can optionally pass the implmentations
        directly to this initialize function too.

        Kwargs:
            module_name: module_implementation (class) - Pass an implmentation
                class as the value for a valid module name to have it
                registered before proxying.
        """
        for module_name, module_implementation in kwargs.items():
            if module_name in self._module_interfaces:
                self.register_implementation(
                    module_name, module_implementation)
        self._proxy_modules()

    def register_implementation(self, module_name, implementation_class):
        """ Register an implmentation of the WebEngine proxy

        The class registered here will be proxied when the module initializer
        is initialized. The implementation class can also be passed to that
        method directly.

        Args:
            implmentation_class (class): A class containing the implementation
                for the WebEngine proxy

        Raises:
            TypeError: if the implementation class is not a class
        """
        if (implementation_class is not None and
                not isclass(implementation_class)):
            raise TypeError(
                "Must register type class for the {} module, not {}".format(
                    module_name, type(implementation_class)))
        self._module_implementations[module_name] = implementation_class

    def finalize(self):
        """ Unproxy the registered proxies on this initializer.

        This will unproxy the interfaces in the reverse order that they
        were proxied.
        """
        for interface in reversed(self._initialized_modules):
            interface.unproxy()
        self._initialized_modules = []

    def _proxy_modules(self):
        """ Proxy the modules if they are registered

        This method will proxy the classes in a reasonable order
        """
        self._proxy_module('scheduler')
        self._proxy_module('persistence')
        self._proxy_module('publisher')
        self._proxy_module('subscriber')
        self._proxy_module('authenticator')
        self._proxy_module('roles')
        self._proxy_module('permissions')
        self._proxy_module('web_engine')

    def _get_module_interface(self, module_name):
        """ Get the interface proxy class for a given module name """
        if module_name not in self._module_interfaces:
            raise ValueError(
                "{} is not a valid module name".format(module_name))
        return self._module_interfaces.get(module_name)

    def _proxy_module(self, module_name):
        """ Proxy a module if it has a registered implementation """
        interface = self._get_module_interface(module_name)
        implementation = self._module_implementations.get(module_name)
        if implementation is not None:
            interface.proxy(implementation)
            self._initialized_modules.append(interface)
