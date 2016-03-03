from nio.util.logging import get_nio_logger
from nio.util.scheduler.scheduler_helper import SchedulerHelper
from nio.util.scheduler.scheduler_thread import SchedulerThread


class Scheduler(object):

    """Singleton class to maintain and interact with an underlying Scheduler"""

    _scheduler_thread = None
    logger = None

    _sched_min_delta = 0.1
    _sched_resolution = 0.1

    @classmethod
    def _get_logger(cls):
        if cls.logger is None:
            cls.logger = get_nio_logger("NIOScheduler")
        return cls.logger

    @classmethod
    def configure(cls, context):
        # Load in the minimum delta and resolution from the config
        cls._sched_min_delta = context.min_interval
        cls._sched_resolution = context.resolution

    @classmethod
    def schedule_task(cls, target, delta, repeatable, *args, **kwargs):
        """ Add the given task to the Scheduler.

        Args:
            target (callable): The task to be scheduled.
            delta (timedelta): The scheduling interval. The scheduler will
                wait for this interval before running 'target' for the first
                time.
            repeatable (bool): When False, 'target' is run only once.
                Otherwise, it is run repeatedly at an interval defined by
                'delta'.
            args: Positional arguments to be passed to 'target'.
            kwargs: Keyword arguments to be passed to 'target'.

        Returns:
            job (Job): The Job object.

        """
        if cls._scheduler_thread is None:
            cls.start()

        return cls._scheduler_thread.scheduler.add(target, delta, repeatable,
                                                   *args, **kwargs)

    @classmethod
    def unschedule(cls, job):
        """Remove a job from the schedule. If the given job is not
        currently scheduled, this method has no effect.

        Args:
            job (APScheduler Job): The job to remove.

        Returns:
            None

        """
        cls._get_logger().debug("Un-scheduling %s" % job)
        cls._scheduler_thread.scheduler.cancel(job)

    @classmethod
    def shutdown(cls):
        if cls._scheduler_thread:
            cls._scheduler_thread.stop()
        cls._scheduler_thread = None

    @classmethod
    def start(cls):
        try:
            if cls._scheduler_thread is None:
                cls._get_logger().info("Starting custom Scheduler")
                cls._scheduler_thread = SchedulerThread(SchedulerHelper(
                    resolution=cls._sched_resolution,
                    min_delta=cls._sched_min_delta))
                cls._scheduler_thread.start()
        except Exception:  # pragma: no cover (exception from ap)
            cls._get_logger().exception("Scheduler failed to start")
