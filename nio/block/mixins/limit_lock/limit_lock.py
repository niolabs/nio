from threading import Lock


class LockQueueFull(Exception):
    pass


class LimitLock(object):

    """ A block mixin that provides lock functionality.

    By including this mixin, your block will have access to methods for lock
    functionality. This is useful when performing tasks that need a lock but
    could potentially take a long time so eventually you want to abort instead
    of having more threads wait for locks.

    How to use this mixin:
        1. Call _execute_with_lock with the method that you want to execute
        and any keyword arguments. The arg max_locks defines how many threads
        will wait for this lock before aborting.

    Note: This method can only be used in one place in your block code.

    """

    def __init__(self):
        super().__init__()
        self._exceute_lock = Lock()
        self._number_of_locks = 0

    def _execute_with_lock(self, execute_method, max_locks, *args, **kwargs):
        if self._number_of_locks >= max_locks:
            self._logger.warning(
                "Currently {} locks waiting to be acquired. This is more than "
                "the max. Aborting call to method in this thread.".format(
                    self._number_of_locks))
            raise LockQueueFull
        self._number_of_locks += 1
        with self._exceute_lock:
            try:
                return execute_method(*args, **kwargs)
            finally:
                self._number_of_locks -= 1
