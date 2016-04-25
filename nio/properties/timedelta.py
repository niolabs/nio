from nio.properties import BaseProperty
from nio.types import TimeDeltaType


class TimeDeltaProperty(BaseProperty):

    def __init__(self, title, **kwargs):
        super().__init__(title, TimeDeltaType, **kwargs)
