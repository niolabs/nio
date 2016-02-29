from nio.properties.timedelta import TimeDeltaProperty
from threading import Lock
from nio.modules.scheduler import Job


class Collector(object):

    """ A block mixin that provides collection/buffering functionality.

    By including this mixin, your block will have a `collect` property
    added to it which represents the amount of time to collect for. Any
    subsequent calls to notify signals will not be notified to the block
    router until the collection window is finished.

    This is useful for high volume blocks that wish to buffer their output.

    By setting the collect property to 0, notifying signals will happen
    immediately, as if this mixin wasn't even included.
    """

    collect = TimeDeltaProperty(
        title='Collect Timeout', default={"seconds": 1})

    def __init__(self):
        super().__init__()
        self._collect_job = None
        self._collect_lock = Lock()
        self._sigs_out = []

    def start(self):
        # Start the collection job, if we want to be collecting
        if self._are_we_collecting():
            self._collect_job = Job(self._dump_signals, self.collect(), True)
        super().start()

    def stop(self):
        if self._collect_job:
            self._collect_job.cancel()
        super().stop()

    def notify_signals(self, signals):
        """Override the notify signals call to keep collecting"""
        if self._are_we_collecting():
            with self._collect_lock:
                self._sigs_out.extend(signals)
        else:
            super().notify_signals(signals)

    def _are_we_collecting(self):
        """Return True if we should be collecting signals"""
        return self.collect().total_seconds() > 0

    def _dump_signals(self):
        """Notify any signals we have collected this window.

        This gets called by the scheduled Job.
        """
        with self._collect_lock:
            if len(self._sigs_out):
                super().notify_signals(self._sigs_out)
                self._sigs_out = []
