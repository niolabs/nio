from copy import copy
from collections import defaultdict, Hashable
from nio.properties import Property


class GroupBy(object):

    """ Use this base class to extend block functionality to groups
    of signal objects.

    Use NIO's native expression syntax to configure a value by which to
    group signals. In your block's 'process_signals' method, pass the
    list of signals and a target method to GroupBy.for_each_group. The
    signals will be grouped automatically and the target method called
    on each group in turn.

    Note that the particular groups are recorded in GroupBy._groups. If
    you'd like to map a function over all the groups outside of
    process_signals, just call GroupBy.for_each_group without a second
    argument.

    Properties:
        group_by: The expression by which signals will be grouped.

    """

    group_by = Property(name="Group By", default=None, allow_none=True)

    def __init__(self):
        super().__init__()
        self._dirty = False
        self._groups = []

    def group(self, signals):
        """ Groups the provided objects by self.group_by.

        Return:
            out (dict): A dictionary where keys are group names/keys and values
            are lists of signals
        """
        signal_groups = defaultdict(list)
        for s in signals:
            try:
                key = self.group_by(s)
            except:
                self._logger.exception(
                    "GroupBy expression failed, ignoring signal")
                continue

            # Need to make sure that the key is a hashable object
            if not isinstance(key, Hashable):
                self._logger.warning(
                    "{} is not hashable cannot be grouped by. Using str "
                    "representation instead".format(key))
                key = str(key)

            # Add the key to our list of groups, if it's not already there
            if key not in self._groups:
                self._groups.append(key)

            signal_groups[key].append(s)

        return signal_groups

    def for_each_group(self, target, signals=None, kwargs=None):
        """ Maps 'target' over the calculated signal groups.

        Note that the required template for 'target' depends on
        whether or not signals are provided for grouping.

        Args:
            target (callable): The target function.
            signals (list): The list of signals to be grouped. If
                this is left off, the list of recorded groups is
                used.
            kwargs : kwargs to be passed to target

        Returns:
            output (list): A list of the return values of each call to the
            target function. If the target function returns a list, the output
            list will be a concatenation of results.
            So [1,2,3,4,5] not [[1,2],[3],[4,5]]
        """
        kwargs = kwargs if kwargs else {}
        output = []

        # if there are no signals, assume that the target function has
        # only one parameter, the group key
        if signals is None:
            # We are going to map each group key over the target function
            # and produce the output along the way.
            # We need to send a copy of self._groups so that in case the target
            # function alters the groups list it doesn't affect iteration
            [self._output_append(output, target(k, **kwargs))
             for k in copy(self._groups)]

        # otherwise, assume that the target function has two arguments,
        # the signal and its group key
        else:
            [self._output_append(output, target(val, key, **kwargs))
             for key, val in self.group(signals).items()]

        return output

    def _output_append(self, target_list, value):
        """ Append a value to a target list.

        If value is a list, don't append the list, but rather extend the list
        with the list in value.

        Returns:
            None - list append/extend happens in place
        """
        if isinstance(value, list):
            target_list.extend(value)
        elif value:
            target_list.append(value)
