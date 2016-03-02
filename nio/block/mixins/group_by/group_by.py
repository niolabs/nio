from copy import copy
from collections import defaultdict, Hashable
from nio.properties.var import VarProperty


class GroupBy(object):

    """ Use this base class to extend block functionality to groups
    of signal objects.

    Use NIO's native expression syntax to configure a value by which to
    group signals. In your block's 'process_signals' method, pass the
    list of signals and a target method to self.for_each_group. The
    signals will be grouped automatically and the target method called
    on each group in turn.

    If you'd like to map a function over all the groups outside of
    process_signals, just call self.for_each_group without passing any
    signals.

    You can also make use of the default process_signals implmentation of
    grouping all incoming signals and processing them independently by not
    overriding process_signals but instead overriding process_group_signals.

    Properties:
        group_by: The expression by which signals will be grouped.

    """

    group_by = VarProperty(name="Group By", default=None, allow_none=True)

    def __init__(self):
        super().__init__()
        self._groups = set()

    def for_each_group(self, target, signals=None, *args, **kwargs):
        """ Execute a function once for every group

        If signals are provided, the target function will only be called
        for groups that appear in the provided signals. If signals are omitted,
        the function will be called for every group that has ever been
        processed in this block.

        Note that the required template for 'target' depends on
        whether or not signals are provided for grouping.

        Args:
            target (callable): The target function.
            signals (list): The list of signals to be grouped. If
                this is left off, the list of recorded groups is
                used.
            args, kwargs : Additional arguments to be passed to target

        Returns:
            list: A list of the return values of each call to the
                target function. If the target function returns a list, the
                output list will be a concatenation of results.
                So [1,2,3,4,5] not [[1,2],[3],[4,5]]
        """
        output = []
        # if there are no signals, assume that the target function has
        # only one parameter, the group key
        if signals is None:
            # We are going to map each group key over the target function
            # and produce the output along the way.
            # We need to send a copy of self._groups so that in case the target
            # function alters the groups list it doesn't affect iteration
            for group in copy(self._groups):
                result = target(group, *args, **kwargs)
                if result and isinstance(result, list):
                    output.extend(result)

        # otherwise, assume that the target function has two arguments,
        # the signal and its group key
        else:
            for group, group_sigs in self._group_signals(signals).items():
                result = target(group_sigs, group, *args, **kwargs)
                if result and isinstance(result, list):
                    output.extend(result)

        return output

    def process_signals(self, signals, input_id=None):
        """A convenient implementation of process signals for grouping blocks.

        This implementation of process_signals is provided only as a
        convenience to block developers. It prevents having to write the same
        code every time for process signals when in reality you only care about
        the signals after they are grouped.

        To use this, don't implement process_signals, but rather implement
        process_group_signals according to the signature provided in this file.
        Any signals you return from that method will be notified out of the
        block on the default output.

        If you wish to not use this implementation, just implement your own
        version of process_signals.
        """
        output_sigs = self.for_each_group(
            self.process_group_signals, signals, input_id)
        self.notify_signals(output_sigs)

    def process_group_signals(self, signals, group, input_id=None):
        """Implement this method to make use of the default behavior.

        If you wish to make use of the default implementation of
        process_signals then override this method. If you wish, you may return
        a list of signals out of this method to have them notified out of
        the block.
        """
        pass  # pragma: no cover

    def _group_signals(self, signals):
        """ Groups the provided signals according to the configuration

        Args:
            signals (list): A list of signals to group

        Returns:
            dict: A dictionary where keys are group names and values are lists
                of the signals in that group
        """
        signal_groups = defaultdict(list)
        for s in signals:
            key = self.group_by(s)

            # Need to make sure that the key is a hashable object
            if not isinstance(key, Hashable):
                self._logger.warning(
                    "{} is not hashable cannot be grouped by. Using str "
                    "representation instead".format(key))
                key = str(key)

            # Add the key to our set of groups and the signal to the list
            # corresponding to the group
            self._groups.add(key)
            signal_groups[key].append(s)

        return signal_groups
