from threading import Thread
from nio.util.logging import get_nio_logger


class NIOThread(Thread):

    def __init__(self, **kwargs):
        """ Create a new NIOThread instance.

        Args:
            kwargs: keyword arguments

        """
        super().__init__(**kwargs)
        self.logger = get_nio_logger("NIOThread")
        self.nio_result = None
        self.nio_exception = None

    def run(self):
        """ Overrides task execution

        Execution is overriden with the purpose of providing feedback when
        the result of the asynchronous task is of interest to caller

        Target execution result is saved in 'nio_result'

        Likewise, if an exception is thrown by target, it is captured and saved
        in 'nio_exception'

        """
        try:
            self.nio_result = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            # first element in _args tuple contains the method to call
            self.logger.exception("Executing: {0}".
                                  format(self._args[0].__name__))
            self.nio_exception = e

    def join(self, timeout=None):
        """ Overrides join execution

        Args:
            timeout: join timeout

        Returns:
            target execution result

        """
        super().join(timeout)
        if self.nio_exception:
            raise self.nio_exception
        return self.nio_result

    def __repr__(self):
        return "_Thread: nio_result: {0}, nio_exception: {1}".format(
            self.nio_result, self.nio_exception)
