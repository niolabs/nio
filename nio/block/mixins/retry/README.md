Retry Mixin
===========

A block mixin that provides retry functionality.

By including this mixin, your block will have access method retry
functionality. This is useful when performing tasks that have a chance
of failing but can then work upon retrying.

Example use cases are database queries and other requests over a network.

The default behavior is to attempt one retry right away and then raise
an execption if the one retry fails.

How to use this mixin:
    1. Call _execute_with_retry with the method that you want to execute
    and any keyword arguments. _execute_with_retry will raise an Exception
    if the execute_method continues to fail after retrying.
    2. Optionally, override _before_retry to write custom code that will be
    performed before attempting a retry. Return True if you want to retry
    and False if not.
    3. In configure, update num_retries if you want to retry execute_method
    more than once. By default, a backoff approach will be used where
    retry attempt n will wait n seconds before executing execute_method.


Special Methods
---------------

- **Retry._execute_with_retry(self, execute_method, kwargs)**:
        Use this in your block to call `execute_method`

        Returns the return value of execute_method or raises an Exception if
        execute_method fails even after the alloted retry attempts.
- **Retry._before_retry(self, retry_count, kwargs)**:
        Determine if a retry should be attempted or not.

        Optionally override in block.

        If a retry is going to be executed, use this to customize any handling
        before the retry is attempted.

        Return:
            bool: True if a retry should be attempted.

