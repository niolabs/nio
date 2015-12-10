class BlockRouter(object):

    """An object that contains blocks and can handle when blocks notify
    signals.

    The most common instance of a BlockRouter will be a Service. Another
    example would be a block group, if that were to be implemented.
    """

    def notify_signals(self, block, signals, output_id):
        """The method to be called when a block is notifying signals.

        Args:
            block (Block): The block that is notifying
            signals (list): The signals that the block is notifying
            output_id: output identifier
        """
        pass  # pragma: no cover

    def notify_management_signal(self, block, signal):
        """The method to be called when notifying management signals

        This is called, for example, when a block changes status while starting
        or stopping, or when a block wants to notify its own error state.

        Args:
            block (Block): The block that is notifying.
            signal (ManagementSignal): The management signal to notify

        Return:
            None

        """
        pass  # pragma: no cover
