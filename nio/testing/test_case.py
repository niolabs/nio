"""
  NIO test support base class

"""
import logging.config
import multiprocessing
from unittest import TestCase


# Testing module implementations
from nio.modules.settings import Settings
from nio.testing.module_initializer import TestingModuleInitializer
from nio.testing.modules.scheduler.module import TestingSchedulerModule
from nio.testing.modules.persistence.module \
    import TestingPersistenceModule
from nio.testing.modules.communication.module \
    import TestingCommunicationModule
from nio.testing.modules.security.module import TestingSecurityModule
from nio.testing.modules.settings.module import TestingSettingsModule
from nio.testing.modules.web.module import TestingWebModule


class NIOTestCase(TestCase):

    """ Base Unit Test case class

    Allows to customize environment information when
    running NIO unit tests

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._module_initializer = None
        logging.config.dictConfig(self.get_logging_config())
        # make sure modules are tearDown regardless of test outcome
        self.addCleanup(self.tearDownModules)

        # maintain a mapping from module to module_name
        self._modules_mapping = {}

    def setupModules(self):
        """ Initializes the modules that will be active when running the test

        There are three important methods to override in a test when
        wanting to customize the modules behaviour. These are:
            - get_test_modules
            - get_module
            - get_context

        """
        self._module_initializer = TestingModuleInitializer(self)

        modules = self.get_test_modules()
        for module_name in modules:
            module = self.get_module(module_name)
            self._modules_mapping[module] = module_name
            self._module_initializer.register_module(module)

        # Perform a safe initialization in case a proxy never got cleaned up
        self._module_initializer.initialize(safe=True)

    def get_module(self, module_name):
        """ Returns a module class type given a module name

        Override this method to customize functionality in a module or
        simply when needing a module other than the default testing module.

        Args:
            module_name (str): module name

        Returns:
            module class type

        """
        known_modules = {
            'scheduler': TestingSchedulerModule,
            'persistence': TestingPersistenceModule,
            'security': TestingSecurityModule,
            'communication': TestingCommunicationModule,
            'settings': TestingSettingsModule,
            'web': TestingWebModule
        }
        if module_name not in known_modules:
            raise ValueError("{} is not a valid module".format(module_name))
        return known_modules.get(module_name)()

    def get_context(self, module_name, module):
        """ Provides the context to use when initializing the module

        Args:
            module_name (str): module name
            module (type): module class type

        Returns:
            module context

        """
        return getattr(module, "prepare_core_context")()

    def tearDownModules(self):
        # Perform a safe finalization in case anything wasn't proxied first
        if self._module_initializer:
            self._module_initializer.finalize(safe=True)

    def get_test_modules(self):
        """ Returns set of modules to load during test

        Override this method to customize which modules you want to load
        during a test
        """
        return {'settings', 'scheduler', 'persistence'}

    def set_settings(self):
        """ Allows test to set settings after 'settings' module is initialized

        A given test can set settings by making calls such as:
            Settings.set([section], [option], value)

        """
        pass

    def get_logging_config(self):
        """ Specifies the default logging configuration """
        return {
            "version": 1,
            "formatters": {
                "default": {
                    "format": ("[%(niotime)s] NIO [%(levelname)s] "
                               "[%(context)s] %(message)s")
                }
            },
            "filters": {
                "niofilter": {
                    "()": "nio.util.logging.filter.NIOFilter"
                }
            },
            "handlers": {
                "default": {
                    "level": "NOTSET",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                    "filters": ["niofilter"]
                }
            },
            "root": {
                "handlers": ["default"]
            }
        }

    def setUp(self):
        super().setUp()
        try:
            multiprocessing.set_start_method('spawn')
        except Exception as e:
            # ignore this error
            if isinstance(e, RuntimeError) \
                    and "context has already been set" in str(e):
                pass
            else:
                print('Setting multiprocess start method, details: {0}'.
                      format(str(e)))

        self.setupModules()

    def tearDown(self):
        try:
            Settings.clear()
        except NotImplementedError:
            # can be triggered if test chooses not to have a Settings module
            pass
        super().tearDown()

    def get_module_name(self, module):
        return self._modules_mapping.get(module, None)


class NIOTestCaseNoModules(NIOTestCase):

    """ NIO Test case that don't need to use modules

    """

    def get_test_modules(self):
        return set()

    def setupModules(self):
        pass  # Not using functionality modules

    def tearDownModules(self):
        pass  # Not using functionality modules
