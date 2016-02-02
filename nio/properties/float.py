from nio.properties import BaseProperty
from nio.types import FloatType


class FloatProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(FloatType, **kwargs)
