from enum import Enum

from nio.util.flags_enum import FlagsEnum
from nio.util.logging import get_nio_logger


class RunnerStatus(Enum):
    """ Runner Status

    Status a runner can be at any time
    """
    created = 1
    configuring = 2
    configured = 3
    stopping = 4
    stopped = 5
    starting = 6
    started = 7
    warning = 8
    error = 9


class Runner(object):
    def __init__(self, *args, status_change_callback=None, **kwargs):
        """ Create a new runnable instance.

        Initializes runnable status

        """
        super().__init__(*args, **kwargs)
        self._status = FlagsEnum(RunnerStatus,
                                 status_change_callback=status_change_callback)
        self.status.set(RunnerStatus.created)
        # This can be overridden in subclasses if desired
        self.logger = get_nio_logger(self.__class__.__name__)

    def configure(self, context):
        """Overrideable method to be called when the runnable is configured

        Args:
            context: specific information needed for runnable's configuration
        """
        pass  # pragma: no cover

    def start(self):
        """Overrideable method to be called when the runnable starts"""
        pass  # pragma: no cover

    def stop(self):
        """Overrideable method to be called when the runnable stops"""
        pass  # pragma: no cover

    @property
    def status(self):
        """ Provides component status """
        return self._status

    @status.setter
    def status(self, status):
        """ Status

        Possible values are based on RunnerStatus

        """
        self.logger.info("Setting status to {}".format(status.name))
        self.status.set(status)

    def do_configure(self, context):
        """ Entry point method to configure runnable.

        Ensures status is correctly set based on the outcome of the operation

        Args:
            context: specific information needed for runnable's configuration

        """
        self.status.set(RunnerStatus.configuring)
        try:
            self.configure(context)
            self.status.set(RunnerStatus.configured)
        except Exception:
            self.logger.exception("Failed to configure")
            self.status.add(RunnerStatus.error)
            raise

    def do_start(self):
        """ Entry point method to start runnable.

        Ensures status is correctly set based on the outcome of the operation

        """
        self.status.set(RunnerStatus.starting)
        try:
            self.start()
            self.status.set(RunnerStatus.started)
        except Exception:
            self.logger.exception("Failed to start")
            self.status.add(RunnerStatus.error)
            raise

    def do_stop(self):
        """ Entry point method to stop runnable.

        Ensures status is correctly set based on the outcome of the operation

        """
        if self.status.is_set(RunnerStatus.stopped) or \
           self.status.is_set(RunnerStatus.stopping):
            self.logger.info("Already stopping or stopped")
            return

        self.status.set(RunnerStatus.stopping)
        try:
            self.stop()
            self.status.set(RunnerStatus.stopped)
        except Exception:
            self.logger.exception("Failed to stop")
            self.status.add(RunnerStatus.error)
