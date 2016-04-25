from nio.properties import BaseProperty
from nio.types import StringType


class StringProperty(BaseProperty):

    def __init__(self, title, **kwargs):
        super().__init__(title, StringType, **kwargs)
