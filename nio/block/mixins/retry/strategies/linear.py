from time import sleep
from nio.block.mixins.retry.strategy import BackoffStrategy


class LinearBackoff(BackoffStrategy):

    def wait_for_retry(self, retry_num):
        """Sleep a certain number of seconds before we do the retry.

        We will wait the current retry number times the multiplier,
        so first retry will be 1*mult, second will be 2*mult, etc.

        The exception is when our current retry is greater than our max
        number of retries, then we want to use the max number of retries.
        This can happen if the strategy is configured to run indefinitely.
        """
        sleep(min(retry_num, self.max_retry) * self.multiplier)
