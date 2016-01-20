"""
  NIO test support base class

"""
import logging.config
import multiprocessing
from unittest import TestCase

from nio.modules.scheduler import Job as SchedulerModuleJob
from nio.modules.security.auth \
    import Authenticator as SecurityModuleAuthenticator
from nio.modules.security.roles import RolesProvider as SecurityModuleRoles
from nio.modules.security.permissions \
    import PermissionsProvider as SecurityModulePermissions

from nio.modules.communication.publisher import Publisher
from nio.modules.communication.subscriber import Subscriber


class NIOTestCase(TestCase):

    """ Base Unit Test case class

    Allows to customize environment information when
    running NIO unit tests

    """

    def __init__(self, methodName='runTests'):
        super().__init__(methodName)

        logging.config.dictConfig(self.get_logging_config())
        self.module_proxies = []

    def get_scheduler_module_implementation(self):
        from nio.util.support.modules.scheduler import Scheduler
        return Scheduler

    def get_security_roles_implementation(self):
        from nio.util.support.modules.security.roles import RolesProvider
        return RolesProvider

    def get_security_permissions_implementation(self):
        from nio.util.support.modules.security.permissions \
            import PermissionsProvider
        return PermissionsProvider

    def get_security_auth_implementation(self):
        from nio.util.support.modules.security.auth import Authenticator
        return Authenticator

    def get_communication_publisher_implementation(self):
        from nio.util.support.modules.communication.publisher import Publisher
        return Publisher

    def get_communication_subscriber_implementation(self):
        from nio.util.support.modules.communication.subscriber \
            import Subscriber
        return Subscriber

    def setupModules(self):
        if 'scheduler' in self.get_test_modules():
            self.module_proxies.append((
                SchedulerModuleJob,
                self.get_scheduler_implementation()))

        if 'security' in self.get_test_modules():
            self.module_proxies.append((
                SecurityModuleRoles,
                self.get_security_roles_implementation()))
            self.module_proxies.append(
                (SecurityModulePermissions,
                 self.get_security_permissions_implementation()))
            self.module_proxies.append((
                SecurityModuleAuthenticator,
                self.get_security_auth_implementation()))

        if 'communication' in self.get_test_modules():
            self.module_proxies.append((
                Publisher,
                self.get_communication_publisher_implementation()))

            self.module_proxies.append((
                Subscriber,
                self.get_communication_subscriber_implementation()))

        for module_proxy, module_implementation in self.module_proxies:
            module_proxy.proxy(module_implementation)

        if 'security' in self.get_test_modules():
            # TODO: Remove once security module is refactored
            from niocore.modules.security import SecurityModule
            SecurityModule._reset({})

    def tearDownModules(self):
        for module_proxy, _ in reversed(self.module_proxies):
            module_proxy.unproxy()

    def get_test_modules(self):
        """ Returns set of modules to load during test
        Override this method to customize which modules you want to load
        during a test
        """
        return {'scheduler', 'security'}

    def setUpSettings(self):
        """ Sets Settings before running a unit test """
        pass

    def get_logging_config(self):
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
        # Initialize settings
        self.setUpSettings()
        # setup Modules
        self.setupModules()

    def tearDown(self):
        super().tearDown()
        self.tearDownModules()

    def get_provider_settings(self):
        """ Override this method for specifying settings
        for the config provider
        """
        return {}


class NIOTestCaseNoModules(NIOTestCase):

    """ NIO Test case that don't need to use modules

    """

    def get_test_modules(self):
        return set()

    def setupModules(self):
        pass  # Not using functionality modules

    def tearDownModules(self):
        pass  # Not using functionality modules
