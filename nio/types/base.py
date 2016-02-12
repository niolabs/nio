class Type(object):
    """ Base type for property and parameters """

    def __init__(self):
        # Type is a static class
        raise RuntimeError("A Type should never be instantiated")

    @staticmethod
    def serialize(value, **kwargs):
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        return value
