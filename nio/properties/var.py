from nio.properties import BaseProperty
from nio.types.base import Type


class VarProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(Type, **kwargs)
