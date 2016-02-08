from nio.properties import BaseProperty
from nio.types import TimeDeltaType


class TimeDeltaProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(TimeDeltaType, **kwargs)
