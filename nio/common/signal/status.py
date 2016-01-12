"""
   Management signal for notifying changes to block status

"""
from enum import Enum
from nio.common.signal.management import ManagementSignal


class StatusSignal(ManagementSignal):
    """ An internal signal to encapsulate status management signals.

    Args:
        status (ComponentStatus): The signal status.
        msg (str): A message/explanation to go with the status change.

    """

    def __init__(self, status=None, msg=None, source="unknown"):
        super().__init__(msg=msg)
        self.status = status
        self.source = source


class ServiceStatusSignal(StatusSignal):
    """ A signal to use to notify service management signals.

    Args:
        status (str): The signal status (ok, warning, or error).
        msg (str): A message/explanation to go with the status change.

    """

    def __init__(self, status=None, msg=None):
        super().__init__(status, msg, "service")
        # initialize auto members, these are set automatically by the system.
        self.name = None


class BlockStatusSignal(StatusSignal):
    """ A signal to use to notify block management signals.

    Args:
        status (str): The signal status (ok, warning, or error).
        msg (str): A message/explanation to go with the status change.

    """

    def __init__(self, status=None, msg=None):
        super().__init__(status, msg, "block")
        # initialize auto members, these are set automatically by the system.
        self.name = None
        self.service_name = None
