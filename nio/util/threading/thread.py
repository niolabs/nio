from threading import Thread
from nio.util.logging import get_nio_logger


class NIOThread(Thread):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = get_nio_logger("NIOThread")

    def run(self):
        self.nio_exception = None
        try:
            self.nio_result = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            # first element in _args tuple contains the method to call
            self._logger.exception("Executing: {0}".
                                   format(self._args[0].__name__))
            self.nio_exception = e

    def join(self, timeout=None):
        super().join(timeout)
        if self.nio_exception:
            raise self.nio_exception
        return self.nio_result

    def __repr__(self):
        return "_Thread: nio_result: {0}, nio_exception: {1}".format(
            self.nio_result if hasattr(self, "nio_result") else None,
            self.nio_exception if hasattr(self, "nio_exception") else None)
