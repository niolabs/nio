from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.base import Type


class VarProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(Type, **kwargs)
