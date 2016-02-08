from time import sleep
from nio.util.threading.thread import NIOThread


def spawn(target, *args, **kwargs):
    """ Executes given target in a new thread

    Args:
        target: method or function to execute
        *args: positional arguments in 'target'
        **kwargs: keyword arguments in 'target'

    Returns:
        newly created thread

    """
    args = (target,) + args
    t = NIOThread(target=_spawn_target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t


def _spawn_target(target, *args, **kwargs):
    SLEEP_TIME_BEFORE_LAUNCHING_THREAD = 0.00001
    sleep(SLEEP_TIME_BEFORE_LAUNCHING_THREAD)
    return target(*args, **kwargs)
