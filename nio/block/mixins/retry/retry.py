from nio.block.mixins.retry.strategy import BackoffStrategy


class Retry(object):

    """ A block mixin that provides retry functionality.

    By including this mixin, your block will have access to a method that can
    retry on failure. This is useful when performing tasks that have a chance
    of failing but can then work upon retrying. Example use cases are database
    queries or other requests over a network.

    The block developer should select a retry backoff strategy from the
    pre-built strategies in nio.block.mixins.retry.strategies or can define
    their own according to the BackoffStrategy spec

    How to use this mixin:
        1. In your block's configure method, define your backoff strategy using
        the use_backoff_strategy method.
        2. Call execute_with_retry with the function that you want to execute.
        If the target function fails, it will retry until it either succeeds or
        the backoff strategy has decided it should stop retrying. If that
        occurs, this function will raise the exception that the target function
        raised originally.
        3. Optionally, override before_retry to write custom code that will be
        performed before attempting a retry.
    """

    def __init__(self):
        super().__init__()
        # Use the placeholder backoff strategy in case the block developer
        # doesn't define one. Note, this strategy will never retry
        self._backoff_strategy = BackoffStrategy(logger=self._logger)

    def execute_with_retry(self, execute_method, *args, **kwargs):
        """ Execute a method and retry if it fails

        Args:
            execute_method (callable): A function to attempt to execute. The
                function may be called multiple times if retries occur.
            args/kwargs: Optional arguments to pass to the execute method

        Returns:
            The result of execute_method upon success.

        Raises:
            Exception: The exception that execute_method raised when the
                backoff strategy decided to stop retrying.
        """
        while True:
            try:
                result = execute_method(*args, **kwargs)
                # If we got here, the request succeeded, let the backoff
                # strategy know then return the result
                self._backoff_strategy.request_succeeded()
                return result
            except Exception as exc:
                self._logger.warning(
                    "Retryable execution on method {} failed".format(
                        getattr(execute_method, '__name__', execute_method)),
                    exc_info=True)
                self._backoff_strategy.request_failed(exc)
                should_retry = self._backoff_strategy.next_retry()
                if not should_retry:
                    # Backoff strategy has said we're done retrying,
                    # so re-raise the exception
                    raise
                else:
                    # Backoff strategy has done its waiting and has instructed
                    # us to retry again. Execute any pre-work before looping
                    # and executing the method again
                    self.before_retry(*args, **kwargs)

    def use_backoff_strategy(self, strategy, *args, **kwargs):
        """ Tell this mixin which backoff strategy to use.

        This method should be called in a block's configure method.

        Args:
            strategy (class): A subclass of BackoffStrategy to use in this
                block when retrying
            args/kwargs: Optional arguments to pass to the constructor of the
                backoff strategy
        """
        if not issubclass(strategy, BackoffStrategy):
            raise TypeError("Backoff strategy must subclass BackoffStrategy")
        self._backoff_strategy = strategy(*args, **kwargs)
        self._backoff_strategy.use_logger(self._logger)

    def before_retry(self, *args, **kwargs):
        """ Perform any actions before the next retry occurs.

        Override this in your block to take action before a retry is attempted.
        This would be the function where you would make any reconnections or
        any other behavior that may make the next retry attempt succeed.
        """
        pass  # pragma: no cover
