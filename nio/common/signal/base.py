from nio.util.logging import get_nio_logger
from nio.util.class_attributes import ClassAttributes

_signal_logger = get_nio_logger('Signal')

class Signal(object):

    """ A base signal class. No functionality to speak of

    """

    def __init__(self, attrs={}):
        super().__init__()
        self.from_dict(attrs)

    def from_dict(self, data):
        for k in data:
            try:
                if isinstance(k, str) and len(k):
                    setattr(self, k, data[k])
                else:
                    _signal_logger.warning(
                        "Member: {0} with value: {1} could not be made part "
                        "of the signal".format(k, data[k]))
            except:
                # catch all just in case, don't loose a signal over
                # an attribute
                _signal_logger.warning(
                    "Member: {0} with value: {1} could not be made part "
                    "of the signal".format(k, data[k]), exc_info=True)

    def to_dict(self, with_type=False, hidden=False):
        # determine meaningful attributes
        d = {attr: getattr(self, attr) for attr in dir(self)
             if (hidden or not attr.startswith('_')) and
             ClassAttributes.is_attr(getattr(self, attr))}
        if with_type:
            t = type(self)
            d['_type'] = '.'.join((t.__module__, t.__name__))
        return d

    def __str__(self):
        d = self.to_dict()
        return repr(d) if len(d) else self.__class__.__name__
