from time import sleep


class Retry(object):

    """ A block mixin that provides retry functionality.

    By including this mixin, your block will have access method retry
    functionality. This is useful when performing tasks that have a chance
    of failing but can then work upon retrying.

    Example use cases are database queries and other requests over a network.

    The default behavior is to attempt one retry right away and then raise
    an execption if the one retry fails.

    How to use this mixin:
        1. Call execute_with_retry with the method that you want to execute
        and any keyword arguments. execute_with_retry will raise an Exception
        if the execute_method continues to fail after retrying.
        2. Optionally, override before_retry to write custom code that will be
        performed before attempting a retry. Return True if you want to retry
        and False if not.
        3. In configure, update num_retries if you want to retry execute_method
        more than once. By default, a backoff approach will be used where
        retry attempt n will wait n seconds before executing execute_method.

    """

    def __init__(self):
        super().__init__()
        self.num_retries = 1

    def execute_with_retry(self, execute_method, **kwargs):
        """Use this in your block to call `execute_method`

        Returns the return value of execute_method or raises an Exception if
        execute_method fails even after the alloted retry attempts.

        """
        exc_to_raise = None
        retry_count = 0
        while True:
            try:
                return execute_method(**kwargs)
            except Exception as e:
                self._logger.warning(
                    "On attempt {}, failed to execute method {}".format(
                        retry_count+1, execute_method.__name__),
                    exc_info=True)
                if not self.before_retry(retry_count, **kwargs):
                    # Because we are done retrying, save the exception to raise
                    # later, outside of the except block.
                    exc_to_raise = e
            if exc_to_raise:
                raise exc_to_raise
            retry_count += 1

    def before_retry(self, retry_count, **kwargs):
        """Determine if a retry should be attempted or not.

        Optionally override in block.

        If a retry is going to be executed, use this to customize any handling
        before the retry is attempted.

        Return:
            bool: True if a retry should be attempted.

        """
        self._logger.debug("Determining if a retry should be attempted")
        if retry_count >= self.num_retries:
            return False
        else:
            self._logger.debug(
                "Waiting {} seconds before retrying execute method".format(
                    retry_count))
            sleep(retry_count)
            return True
