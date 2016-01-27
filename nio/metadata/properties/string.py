from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.string import StringType


class StringProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(StringType(), **kwargs)
