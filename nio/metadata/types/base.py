class Type:
    """ Base type for property and parameters """

    def __init__(self):
        # Type is a static class
        raise Exception

    @staticmethod
    def data_type():
        return ""

    @staticmethod
    def serialize(value, **kwargs):
        return value

    @staticmethod
    def deserialize(value, **kwargs):
        return value
