from copy import deepcopy
from nio.signal.base import Signal
from nio.properties import StringProperty, BoolProperty, \
    ObjectProperty, PropertyHolder


class EnrichProperties(PropertyHolder):
    enrich_field = StringProperty(
        title="Results Field", default="", visible=False)
    exclude_existing = BoolProperty(title="Exclude Existing?", default=True)


class EnrichSignals(object):

    enrich = ObjectProperty(EnrichProperties, title='Signal Enrichment')

    def get_output_signal(self, signal_data, incoming_signal, copy=True):
        """ Get an output signal based on the block configuration.

        This method will return a single Signal that consists of the fields
        according to the block's configuration. The signal_data may be the
        entire contents of the signal, it may be added as a field, or it may
        be added to the contents of the signal.

        Args:
            signal_data (dict): Dictionary of data representing the "results"
                to append/include with the signal
            incoming_signal (Signal): The signal object that powered this
                particular operation
            copy (bool): Whether or not to perform a deep copy on the
                incoming signal before operating on it

        Returns:
            sig (Signal): A single Signal formatted according to the block
        """
        if self.enrich(incoming_signal).exclude_existing(incoming_signal):
            # This is the easy case, we don't want any of the previous data
            return Signal(signal_data)

        if copy:
            new_sig = deepcopy(incoming_signal)
        else:
            new_sig = incoming_signal

        if self.enrich().enrich_field():
            # Just set the signal data to a result attribute
            setattr(new_sig, self.enrich().enrich_field(), signal_data)
            return new_sig

        # If we're here, we need to merge the signal data onto the incoming
        # signal. Data from the results should take precedence over data on
        # the incoming signal.
        new_sig.from_dict(signal_data)
        return new_sig

    def notify_output_signals(self, signals_data, incoming_signal,
                              copy=True, output_id=None):
        """ A helper method to notify signals after properly enriching them.

        This method will call self.notify_signals on the block's behalf. It
        will first enrich the incoming signal if the block is configured to
        do so.

        Calling this method is roughly equivalent to calling get_output_signal
        and then notifying the result.

        Args:
            signals_data (dict/list): Data about the output signals. If this
                is a list, it will be assumed to be a list of dictionaries
                whose corresponding Signals will be notified in a batch.
                Otherwise, it should be a single dict containing the signal
                data to notify.
            incoming_signal (Signal): The signal object that triggered this
                operation.
            copy (bool): Whether or not to perform a deep copy on the
                incoming signal before operating on it.
            output_id (str): The output ID to notify signals to
        """
        if not isinstance(signals_data, list):
            signals_data = [signals_data]

        self.notify_signals([
            self.get_output_signal(signal_data, incoming_signal, copy=copy)
            for signal_data in signals_data], output_id)
