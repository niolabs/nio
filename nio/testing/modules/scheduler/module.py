from nio.modules.context import ModuleContext
from nio.util.scheduler.job import Job
from nio.util.scheduler.scheduler import Scheduler
from nio.modules.scheduler.module import SchedulerModule


class TestingSchedulerModule(SchedulerModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_job_class(Job)

        Scheduler.configure(context)
        Scheduler.start()

    def finalize(self):
        Scheduler.shutdown()
        super().finalize()

    def prepare_core_context(self):

        context = ModuleContext()
        context.min_interval = 0.1
        context.resolution = 0.1

        return context
