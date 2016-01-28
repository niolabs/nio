from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.int import IntType


class IntProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(IntType, **kwargs)
