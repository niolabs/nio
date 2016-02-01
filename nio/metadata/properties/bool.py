from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.bool import BoolType


class BoolProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(BoolType, **kwargs)
