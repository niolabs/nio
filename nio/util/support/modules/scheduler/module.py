from nio.util.support.modules.scheduler import Job, NIOScheduler
from nio.modules.scheduler.module import SchedulerModule


class TestingSchedulerModule(SchedulerModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_job_class(Job)

        NIOScheduler.configure(context)
        NIOScheduler.start()

    def finalize(self):
        NIOScheduler.shutdown()
        super().finalize()
