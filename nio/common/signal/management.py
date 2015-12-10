"""
   The base Management signal.

"""
from nio.common.signal.base import Signal


class ManagementSignal(Signal):
    """ A special type of signal for block management

    """

    def __init__(self, attributes={}, msg=None):
        super().__init__(attributes)
        self.msg = msg
