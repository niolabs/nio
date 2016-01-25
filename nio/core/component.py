"""
  NIO Core Component interface

"""
from nio.util.logging import get_nio_logger
from nio.util.runner import Runner


class MissingComponent(Exception):
    """Exception raised when a component is missing"""
    pass


class CoreComponent(Runner):
    """ Base core component class.

    Contains base properties and functionality common to all components

    """
    _name = "Unknown"
    # have a default somewhere in the "middle"
    default_order = 100

    def __init__(self):
        self._logger = get_nio_logger(self._name)
        Runner.__init__(self,
                        status_change_callback=self._on_status_change_callback)

        self._context = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def get_logger(self):
        return self._logger

    @property
    def version(self):
        """ Attempts to find the version of the core component """
        version = None
        try:
            from importlib import import_module

            module = import_module(self.__class__.__module__)
            version = module.__version__
        except:
            # No version was specified
            pass
        return version

    def _on_status_change_callback(self, old_status, new_status):
        self._logger.info("Component: {0} status changed from: {1} to: {2}".
                          format(self.name, old_status.name, new_status.name))

    def prepare_context(self, context):
        """ Method executed when preparing an init context

        Components can override this method to provide specific information
        through the service init context

        Args:
            context (ServiceContext): service initialization context

        """
        pass

    def configure(self, context):
        """Configure method to override when subclassing component"""
        self._context = context

    # TODO: Move this method to core, it relies on the core context
    def get_dependency(self, name, optional=False):
        """ Retrieves a core dependency

        Retrieves a core dependency by name and throws an exception
        if component is not available

        Args:
            name (str): Dependency's name
            optional (bool): Raise error if not dependency found

        Returns:
            Dependency component

        Raises:
            InvalidContext if component is not available
        """
        # Our reference to the core context will be set on configure
        if self._context is None:
            raise RuntimeError("Component has not been configured")

        dep = self._context.get_component(name)
        if dep is None and not optional:
            raise MissingComponent("Missing Component : %s" % name)
        return dep

    def get_order(self):
        return CoreComponent.default_order
