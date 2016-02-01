from datetime import timedelta
from nio.metadata.properties.base import BaseProperty
from nio.metadata.types.timedelta import TimeDeltaType


class TimeDeltaProperty(BaseProperty):

    def __init__(self, **kwargs):
        super().__init__(TimeDeltaType, **kwargs)
