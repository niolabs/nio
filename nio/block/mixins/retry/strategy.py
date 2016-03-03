class BackoffStrategy(object):

    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger
        self.retry_num = 0

    def request_failed(self, exc):
        """ Called when a retryable request fails """
        self.retry_num += 1

    def request_succeeded(self):
        """ Called when a retryable request succeeds """
        self.retry_num = 0

    def next_retry(self):
        """ Do any waiting then return True to execute the retry.

        This function is responsible for determining whether or not a retry
        should take place, and if so, how long (if at all) to wait before
        doing so. If the strategy chooses to wait, it should just call sleep
        inside of this method since it will likely be running in its own
        thread.

        Returns:
            bool: True if the retry should execute. False if we are "done"
                retrying
        """
        self.logger.warning("No retry strategy specified, not retrying")
        return False

    def use_logger(self, logger):
        """Use a logger instance in this backoff strategy.

        This helper function is useful for blocks or mixins to call so that the
        backoff strategy can log from that block. This gets called
        automatically by the Retry mixin but you are free to make another call
        to use a different logger.

        Args:
            logger (Logger): A logger that the backoff strategy can use
        """
        self.logger = logger
