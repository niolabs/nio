from nio.properties import BaseProperty
from nio.types import FileType


class FileProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(FileType, **kwargs)
