from threading import Thread


class SchedulerThread(Thread):
    """ host the scheduler.
    """

    def __init__(self, scheduler):
        """ Initializes the thread.

        Args:
            scheduler (Scheduler): scheduler instance it will run
        """
        super(SchedulerThread, self).__init__(daemon=True)

        self._scheduler = scheduler

    def run(self):
        """ Scheduler thread entry point.

        Starts the scheduler

        """
        self._scheduler.start()

    def stop(self):
        """ Stops the thread and the scheduler
        """
        self._scheduler.stop()

    @property
    def scheduler(self):
        return self._scheduler
