from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.float import FloatType


class FloatProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(FloatType, **kwargs)
