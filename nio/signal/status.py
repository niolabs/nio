"""
   Management signal for notifying changes to block or service status

"""
from nio.signal.management import ManagementSignal


class StatusSignal(ManagementSignal):

    """ An internal management signal to encapsulate status change information

    Args:
        status (RunnerStatus): The signal status.
        message (str): An optional explanation to go with the status change.

    """

    def __init__(self, status, message=None, **kwargs):
        super().__init__(**kwargs)
        self.status = status
        self.message = message


class ServiceStatusSignal(StatusSignal):

    """ A signal to use to notify service management signals.

    Args:
        status (RunnerStatus): The signal status.
        message (str): An optional explanation to go with the status change.
        service_name (str): The name of the service affected

    """

    def __init__(self, status, message=None, service_name=None, **kwargs):
        super().__init__(status, message, **kwargs)
        self.service_name = service_name


class BlockStatusSignal(StatusSignal):

    """ A signal to use to notify block management signals.

    Args:
        status (RunnerStatus): The signal status.
        message (str): An optional explanation to go with the status change.
        block_name (str): The name of the block affected
        service_name (str): The name of the service the block is contained in
    """

    def __init__(self, status, message=None,
                 block_name=None, service_name=None, **kwargs):
        super().__init__(status, message, **kwargs)
        self.block_name = block_name
        self.service_name = service_name
