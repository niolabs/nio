LimitLock Mixin
===============
 
    A block mixin that provides lock functionality.

    By including this mixin, your block will have access to methods for lock
    functionality. This is useful when performing tasks that need a lock but
    could potentially take a long time so eventually you want to abort instead
    of having more threads wait for locks.

    How to use this mixin:
        1. Call _execute_with_lock with the method that you want to execute
        and any keyword arguments. The arg max_locks defines how many threads
        will wait for this lock before aborting.

    Note: This method can only be used in one place in your block code.


Special Methods
---------------

- **Retry._execute_with_lock(self, execute_method, max_locks, args, kwargs)**:
        Use this in your block to call `execute_method`

        Once max_locks number of threads are waiting for the lock, subsequent
        calls will immediately return None.

        Returns the return value of execute_method
