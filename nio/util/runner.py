from nio.common import ComponentStatus
from nio.util.flags_enum import FlagsEnum
from nio.util.logging import get_nio_logger


class Runner(object):
    def __init__(self, status_change_callback=None):
        """ Create a new runnable instance.

        Initializes runnable status

        """
        self._status = FlagsEnum(ComponentStatus,
                                 status_change_callback=status_change_callback)
        self.status.set(ComponentStatus.created)

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
    def logger(self):
        return self.get_logger()

    @property
    def status(self):
        """ Provides component status """
        return self._status

    @status.setter
    def status(self, status):
        """ Status

        Possible values are based on ComponentStatus

        """
        self.logger.info("Setting status to {}".format(status.name))
        self.status.set(status)

    def do_configure(self, context):
        """ Entry point method to configure runnable.

        Ensures status is correctly set based on the outcome of the operation

        Args:
            context: specific information needed for runnable's configuration

        """
        self.status.set(ComponentStatus.configuring)
        try:
            self.configure(context)
            self.status.set(ComponentStatus.configured)
        except Exception:
            self.logger.exception("Failed to configure")
            self.status.add(ComponentStatus.error)
            raise

    def do_start(self):
        """ Entry point method to start runnable.

        Ensures status is correctly set based on the outcome of the operation

        """
        self.status.set(ComponentStatus.starting)
        try:
            self.start()
            self.status.set(ComponentStatus.started)
        except Exception:
            self.logger.exception("Failed to start")
            self.status.add(ComponentStatus.error)
            raise

    def do_stop(self):
        """ Entry point method to stop runnable.

        Ensures status is correctly set based on the outcome of the operation

        """
        if self.status.is_set(ComponentStatus.stopped) or \
           self.status.is_set(ComponentStatus.stopping):
            self.logger.info("Already stopping or stopped")
            return

        try:
            self.stop()
            self.status.set(ComponentStatus.stopped)
        except Exception:
            self.logger.exception("Failed to stop")
            self.status.add(ComponentStatus.error)

    def get_logger(self):
        return get_nio_logger(self.__class__.__name__)
