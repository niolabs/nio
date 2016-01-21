from nio.modules.proxy import ModuleProxy


class Job(ModuleProxy):

    """ This class encapsulates the user-facing interface to NIO's
    scheduling facilities. When Jobs are instantiated, they are
    immediately added to the process' Scheduler.
    """

    def __init__(self, target, delta, repeatable, *args, **kwargs):
        """ Job constructor.

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
            None

        """
        super().__init__(target, delta, repeatable, *args, **kwargs)

    def cancel(self):
        """ Unschedule this task.

        Returns:
            None

        """
        raise NotImplementedError()
