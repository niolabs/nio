

class Persistence(object):

    def __init__(self, name):
        self._name = name
        self._values = {}

    def store(self, key, value):
        self._values[key] = value

    def load(self, key, default=None):
        return self._values.get(key, default)

    def has_key(self, key):
        return key in self._values

    def clear(self, key):
        if key in self._values:
            del self._values[key]

    def save(self):
        pass

    @classmethod
    def setup(cls, configuration):
        pass

    @classmethod
    def configure(cls, service_name):
        pass
