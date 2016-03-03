from time import sleep
from nio.block.mixins.retry.strategy import BackoffStrategy


class LinearBackoff(BackoffStrategy):

    def __init__(self, max_retries=-1, multiplier=1):
        """ Create an instance of a linear backoff strategy

        Args:
            max_retries (int): The maximum number of retries to make before
                giving up on retrying.
            multiplier (float): The multiplier to apply when sleeping. By
                default, this strategy will sleep a number of seconds equal to
                the current retry number. This argument allows you to alter
                that. For example, by default the 5th retry will sleep for 5
                seconds. Passing a multiplier of 1.5 will cause the 5th retry
                to sleep for 7.5 seconds instead.
        """
        super().__init__()
        self._max_retries = max_retries
        self._multiplier = multiplier

    def next_retry(self):
        """Sleep a certain number of seconds unless we are out of retries."""
        # Check if we have a maximum number of retries and we've passed it
        self.logger.info("Executing retry number {}, max retries is {}".format(
            self.retry_num, self._max_retries))
        if self._max_retries >= 0 and self.retry_num > self._max_retries:
            self.logger.warning(
                "Retry number {} exceeds the  max retries of {}".format(
                    self.retry_num, self._max_retries))
            return False

        # We will wait the current retry number times the multiplier,
        # so first retry will be 1*mult, second will be 2*mult, etc
        sleep(self.retry_num * self._multiplier)
        return True
