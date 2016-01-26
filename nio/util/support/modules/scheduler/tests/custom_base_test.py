from nio.util.support.test_case import NIOTestCase
from nio.modules.context import ModuleContext
from nio.util.support.modules.scheduler.module import TestingSchedulerModule


class CustomSchedulerTestCase(NIOTestCase):

    def get_scheduler_module_context(self):
        return ModuleContext()

    def get_module(self, module_name):
        if module_name == "scheduler":
            return TestingSchedulerModule()
        else:
            return super().get_module(module_name)
