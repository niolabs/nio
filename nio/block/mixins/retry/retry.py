from enum import Enum
from threading import Event
from nio.properties import PropertyHolder, ObjectProperty, BoolProperty, \
    IntProperty, SelectProperty, FloatProperty
from nio.block.mixins.retry.strategy import BackoffStrategy
from nio.block.mixins.retry.strategies import LinearBackoff, ExponentialBackoff


class RetryStrategies(Enum):
    linear = LinearBackoff
    exponential = ExponentialBackoff


class RetryOptions(PropertyHolder):
    """ Options the block can be configured with to control how it retries.

    The properties will be passed to the backoff strategy's constructor.
    """

    strategy = SelectProperty(RetryStrategies, title="Strategy to Use",
                              default=RetryStrategies.linear, allow_expr=False)
    max_retry = IntProperty(title="Max Number of Retries", default=5,
                            allow_expr=False)
    multiplier = FloatProperty(title="Retry Multiplier", default=1,
                               allow_expr=False)
    indefinite = BoolProperty(title="Continue Indefinitely?", default=False,
                              allow_expr=False)

    def get_options_dict(self):
        return {
            "max_retry": self.max_retry(),
            "multiplier": self.multiplier(),
            "indefinite": self.indefinite()
        }


class Retry(object):
    """ A block mixin that provides retry functionality.

    By including this mixin, your block will have access to a method that can
    retry on failure. This is useful when performing tasks that have a chance
    of failing but can then work upon retrying. Example use cases are database
    queries or other requests over a network.

    When this mixin is added to a block, some hidden retry configuration
    options will be added to the block. These options allow the block
    configurer to determine how retries should occur, including what strategy
    should be used.

    Block developers can implement their own backoff strategies and employ
    those instead by overriding the setup_backoff_strategy method.

    How to use this mixin:
        1. Configure your block by selecting a backoff strategy as well as
        providing some options to determine how long it will wait between
        retries.

        2. Call execute_with_retry with the function that you want to execute.
        If the target function raises an exception, it will retry until it
        either succeeds or the backoff strategy has decided it should stop
        retrying. If that occurs, execute_with_retry will raise the exception
        that the target function raised originally.

        3. Optionally, override before_retry to write custom code that will be
        performed before attempting a retry.

    Block parameters:
        strategy (select): A choice of pre-configured backoff strategies
        max_retry (int): The maximum number of retries to attempt. Note that
            this is based on retry number, not retry duration. Setting it to
            0 means that no retries will be attempted. Setting it to a negative
            number means that there is no maximum. Also note that this
            property works in concert with the indefinite flag. If that flag
            is set to True, then the retry duration for the retry number
            specified in max_retry will be retried indefinitely.
        multiplier (float): This property has slightly different meanings
            based on what strategy is being used, but for the most part, it
            allows you to control how much time will elapse between retries.
            The higher the number, the longer amount of time that will elapse
            between each retry attempt.
        indefinite (bool): Set to True if you wish for the max_retry retry
            attempt to be continued indefinitely. For example, if this is true
            and max_retry is 5, then the 5th retry will continue to be retried
            until the retry is successful or the block is stopped. If this
            flag is set to False, the retry mixin will stop retrying once the
            max_retry retry attempt is reached.
    """

    retry_options = ObjectProperty(RetryOptions, title="Retry Options",
                                   visible=True, default=RetryOptions())

    def configure(self, context):
        """ This implementation will use the configured backoff strategy """
        super().configure(context)
        self.setup_backoff_strategy()

    def setup_backoff_strategy(self):
        """ Define which backoff strategy the block should use.

        This implementation will use the selected backoff strategy from the
        configured retry options and pass other configured options as kwargs.

        Block developers can override this function to use a custom backoff
        strategy.
        """
        self.use_backoff_strategy(
            self.retry_options().strategy().value,
            **(self.retry_options().get_options_dict()))

    def execute_with_retry(self, execute_method, *args, stop_retry_event=None,
                           **kwargs):
        """ Execute a method and retry if it raises an exception

        Args:
            execute_method (callable): A function to attempt to execute. The
                function may be called multiple times if retries occur.
            args/kwargs: Optional arguments to pass to the execute method
            stop_retry_event (Event): Event that stops retrying-loop when set

        Returns:
            The result of execute_method upon success.

        Raises:
            Exception: The exception that execute_method raised when the
                backoff strategy decided to stop retrying.
        """
        # verify incoming event type if set
        if stop_retry_event and not isinstance(stop_retry_event, Event):
            raise TypeError("stop_retry_event must be an instance of Event")
        # Save a stringified version of the method's name
        # If it doesn't define __name__, use however we should stringify
        execute_method_name = getattr(
            execute_method, '__name__', str(execute_method))
        while not stop_retry_event or not stop_retry_event.is_set():
            try:
                result = execute_method(*args, **kwargs)
                # If we got here, the request succeeded, let the backoff
                # strategy know then return the result
                self._backoff_strategy.request_succeeded()
                return result
            except Exception as exc:
                self.logger.warning(
                    "Retryable execution on method {} failed".format(
                        execute_method_name), exc_info=True)
                self._backoff_strategy.request_failed(exc)
                should_retry = self._backoff_strategy.should_retry()
                if not should_retry:
                    # Backoff strategy has said we're done retrying,
                    # so re-raise the exception
                    self.logger.exception(
                        "Out of retries for method {}.".format(
                            execute_method_name))
                    raise
                else:
                    # Backoff strategy has instructed us to retry again. First
                    # let the strategy do any waiting, then execute any
                    # pre-work before looping and executing the method again
                    self._backoff_strategy.wait_for_retry()
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
        self._backoff_strategy.use_logger(self.logger)

    def before_retry(self, *args, **kwargs):
        """ Perform any actions before the next retry occurs.

        Override this in your block to take action before a retry is attempted.
        This would be the function where you would make any reconnections or
        any other behavior that may make the next retry attempt succeed.
        """
        pass  # pragma: no cover
