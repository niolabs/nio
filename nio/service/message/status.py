class StatusMessage(object):

    """ Defines a status message to be sent from Service to Core
    """

    def __init__(self, status):
        """ Initializes the message

        Args:
            status (FlagsEnum(RunnerStatus)): Service status
        """
        self.status = status

    def __str__(self):
        return "Service Status Message: {0}".format(self.status.name)
