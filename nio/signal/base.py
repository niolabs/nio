""" The definition of a Signal

A signal is the fundamental unit of information in n.io. Functionally, it
is a key-value object that can contain any information that Python can
represent. Conceptually, a signal can represent any piece of information. It
can be as simple as an empty signal representing some sort of ping or as
complex as a signal with many attributes containing various pieces of
information.

The base signal does not impose very many rules or restricitions, but the class
is intended to be extended and sub-classed to have more validation and
functionality for different types of data.
"""
from nio.util.logging import get_nio_logger
from nio.util.class_attributes import ClassAttributes

_signal_logger = get_nio_logger('Signal')


class Signal(object):

    def __init__(self, attrs=None):
        """ Create a new signal - optionally with some data

        Args:
            attrs (dict): An optional dictionary containing the data for this
                signal. If specified, this will dictionary will be passed to
                from_dict.
        """
        super().__init__()
        if attrs is not None:
            self.from_dict(attrs)

    def from_dict(self, data):
        """ Create attributes on this signal based on a dictionary.

        This function will take a dictionary of data and attempt to set the
        attributes on this signal. This does not always work though because
        some values that are valid keys on a dictionary are not valid
        attribute names on an object (e.g. False, 7, None, etc). In the case
        of an invalid attribute, a warning will be logged and the attribute
        will be skipped.

        Args:
            data (dict): A dictionary of data to set on this signal

        Raises:
            TypeError: If data is not a dictionary
        """
        if not isinstance(data, dict):
            raise TypeError("Signal data from_dict must be a dictionary")

        for key, val in data.items():
            try:
                # We don't want to have the empty string be on the signal as
                # an attribute name, even though Python allows it
                if key and isinstance(key, str):
                    setattr(self, key, val)
                    # If we made it here, keep going to the next attribute
                    continue
            except:
                # In case of an exception, fail gracefully but log a warning
                pass

            # If we made it here something was wrong with the key/val,
            # otherwise we would have "continued" through the loop
            _signal_logger.warning(
                "Key: {} with value: {} could not be made part of the "
                "signal".format(key, val), exc_info=True)

    def to_dict(self, include_hidden=False, with_type=False):
        """ Create a dictionary representation of this signal.

        Args:
            include_hidden (bool): Whether or not to include hidden signal
                attributes in the resulting dictionary. Defaults to False
            with_type (str): If specified, the attribute on the resulting
                dictionary that will be the type of this signal

        Returns:
            dict: A dictionary containing the attributes of the signal
        """
        sig_dict = dict()
        for attr_name in dir(self):

            # We don't want to include attributes starting with two underscores
            # under any circumstance
            if attr_name.startswith('__'):
                continue

            attr_value = getattr(self, attr_name)

            # We don't want to include methods or functions in the dictionary
            if not ClassAttributes.is_attr(attr_value):
                continue

            # We only want the attribute if we want hidden attributes or
            # if it's not hidden
            if include_hidden or not self._is_hidden(attr_name):
                sig_dict[attr_name] = attr_value

        if with_type and isinstance(with_type, str):
            sig_dict[with_type] = self.__class__.__name__

        return sig_dict

    def _is_hidden(self, attribute_name):
        """ Returns True if a given attribute name is hidden.

        Currently, attributes that begin with an underscore are to be
        considered "hidden" attributes. This simply means they will not be
        returned in to_dict calls on this signal unless requested.

        Args:
            attribute_name (str): The name of the attribute to check

        Returns:
            bool: True if the attribute is to be considered hidden
        """
        return attribute_name.startswith('_')

    def __str__(self):
        d = self.to_dict()
        return repr(d) if len(d) else self.__class__.__name__
