from time import sleep
from nio.block.mixins.retry.strategy import BackoffStrategy


class ExponentialBackoff(BackoffStrategy):

    def wait_for_retry(self, retry_num):
        """Sleep a certain number of seconds before we do the retry.

        We will wait the multiplier times 2 raised to one less than the
        current retry number.
        So the first retry will be mult*1, then mult*2, then mult*4, etc

        The exception is when our current retry is greater than our max
        number of retries, then we want to use the max number of retries.
        This can happen if the strategy is configured to run indefinitely.
        """
        sleep(self.multiplier * 2**(min(retry_num, self.max_retry)-1))
