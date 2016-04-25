from nio.properties import BaseProperty
from nio.types import FileType


class FileProperty(BaseProperty):

    def __init__(self, title, **kwargs):
        super().__init__(title, FileType, **kwargs)
