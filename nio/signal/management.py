from nio.signal.base import Signal


class ManagementSignal(Signal):

    """ A special type of signal for management of n.io components.

    A management signal is a type of signal that n.io binaries and other
    plugins will sometimes look for. Any information that needs to be passed
    between n.io components for internal use will be in the form of a
    ManagementSignal. This interface is also available to block developers
    to notify information.

    This signal does not have any other attributes or functionality forced
    on it, it is just a placeholder super class to be used.
    """
    pass
