from nio.properties import BaseProperty
from nio.types import FloatType


class FloatProperty(BaseProperty):

    def __init__(self, title, **kwargs):
        super().__init__(title, FloatType, **kwargs)
