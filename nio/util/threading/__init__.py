from time import sleep
from nio.util.threading.thread import NIOThread

SLEEP_TIME_BEFORE_LAUNCHING_THREAD = 0.00001


def _spawn_target(target, *args, **kwargs):
    sleep(SLEEP_TIME_BEFORE_LAUNCHING_THREAD)
    return target(*args, **kwargs)


def spawn(target, *args, **kwargs):
    args = (target,) + args
    t = NIOThread(target=_spawn_target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t
