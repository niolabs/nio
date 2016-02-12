from nio.properties import BaseProperty
from nio.types import StringType


class StringProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(StringType, **kwargs)
