from os.path import isfile, abspath

from nio.types.base import Type


class FileHolder(object):
    """ Instance received when assigning this property to a variable """

    def __init__(self, value, mode):
        # actual property value
        self._value = value
        # stream obtained from __enter__ method
        self._stream = None
        # file mode to use when opening file
        self._mode = mode

    def __enter__(self):
        """ Return a file stream when a a valid file exists """
        real_file = self.file
        if real_file is not None:
            # specify mode only when it is user defined, otherwise
            # allow to pick up default value
            self._stream = open(real_file, mode=self._mode) \
                if self._mode else open(real_file)
            return self._stream

    def __exit__(self, _type, value, tb):
        """ Close file stream """
        if self._stream:
            self._stream.close()
            self._stream = None

    # Actual property value
    @property
    def value(self):
        return self._value

    @property
    def file(self):
        # First, just see if it is already a file?
        if isfile(self.value):
            return self.value

        # Next, try the absolute file path
        filename = abspath(self.value)
        if isfile(filename):
            return filename

        return None


class FileType(Type):

    @staticmethod
    def serialize(value, **kwargs):
        """ Convert a value to a JSON serializable value """
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        """ Convert value to file """
        try:
            mode = kwargs.get('mode', None)
            return FileHolder(value, mode)
        except:
            raise TypeError(
                "Unable to cast value to a file: {}".format(
                    value, **kwargs))
