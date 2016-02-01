from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.file import FileType


class FileProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(FileType, **kwargs)
