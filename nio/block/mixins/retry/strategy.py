class BackoffStrategy(object):

    def __init__(self, logger=None, max_retry=0, multiplier=1,
                 indefinite=False, **kwargs):
        """ Create an instance of a backoff strategy

        Args:
            logger (Logger): The logger to use when retrying
            max_retry (int): The maximum number of retries to try before
                stopping any increasing delay. Depending on the value of the
                indefinite parameter, retrying may give up at this point.
            multiplier (float): The multiplier to apply when sleeping. By
                default, this strategy will sleep a number of seconds equal to
                the current retry number. This argument allows you to alter
                that. For example, by default the 5th retry will sleep for 5
                seconds. Passing a multiplier of 1.5 will cause the 5th retry
                to sleep for 7.5 seconds instead.
            indefinite (bool): Whether to continue on retrying indefinitely
                once the max duration is reached
        """
        super().__init__()
        self.logger = logger
        self.max_retry = max_retry
        self.multiplier = multiplier
        self.indefinite = indefinite
        self.retry_num = 0

    def request_failed(self, exc):
        """ Called when a retryable request fails """
        self.retry_num += 1

    def request_succeeded(self):
        """ Called when a retryable request succeeds """
        self.retry_num = 0

    def should_retry(self):
        """ Determine whether or not we should retry this time.

        This function is responsible for determining whether or not a retry
        should take place; the wait_for_retry function will do the actual
        waiting for the retry.

        This method has a default implementation that will check if the max
        number of retries has taken place or if the indefinite retry
        setting has been checked. In your strategy, if you wish to utilize
        this behavior, you should only need to override the wait_for_retry
        function.

        Returns:
            bool: True if the retry should execute. False if we are "done"
                retrying
        """
        self.logger.info("Executing retry number {}, max retries is {}".format(
            self.retry_num, self.max_retry))
        if self.max_retry >= 0 and self.retry_num > self.max_retry:
            # There is a configured max number of retries and we are
            # officially past it, see if we continue or not
            if not self.indefinite:
                self.logger.warning(
                    "Done retrying - we have exceeded the maximum number "
                    "of retries ({})".format(self.max_retry))
                return False
        # If we got here either we are retrying indefinitely or we haven't hit
        # our max yet, let's retry
        return True

    def wait_for_retry(self):
        """ Do any waiting before the next retry is actually executed.

        The strategy implementation will want to override this method to
        define how much time should elapse between retries.
        """
        pass

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
