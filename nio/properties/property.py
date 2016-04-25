from nio.properties import BaseProperty
from nio.types.base import Type


class Property(BaseProperty):

    """ A property that can assume any type """

    def __init__(self, title, **kwargs):
        super().__init__(title, Type, **kwargs)
