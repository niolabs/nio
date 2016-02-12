from nio.properties import BaseProperty
from nio.types import BoolType


class BoolProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(BoolType, **kwargs)
