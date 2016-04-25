from nio.properties import BaseProperty
from nio.types import BoolType


class BoolProperty(BaseProperty):

    def __init__(self, title, **kwargs):
        super().__init__(title, BoolType, **kwargs)
