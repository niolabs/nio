from nio.properties import BaseProperty
from nio.types import IntType


class IntProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(IntType, **kwargs)
