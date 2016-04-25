from nio.properties import BaseProperty
from nio.types import IntType


class IntProperty(BaseProperty):

    def __init__(self, title, **kwargs):
        super().__init__(title, IntType, **kwargs)
