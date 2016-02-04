from nio.util.scheduler.scheduler import Scheduler


class Job(object):

    def __init__(self, target, delta, repeatable, *args, **kwargs):
        self._job = Scheduler.schedule_task(
            target, delta, repeatable, *args, **kwargs)

    def cancel(self):
        Scheduler.unschedule(self._job)
