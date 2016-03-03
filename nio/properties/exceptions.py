class AllowNoneViolation(Exception):
    """ Raised when a property contains a None value but is not allowed to """
    pass


class NoClassVersion(Exception):
    pass


class NoInstanceVersion(Exception):

    def __init__(self, class_version):
        super().__init__()
        self.class_version = class_version


class OlderThanMinVersion(Exception):

    def __init__(self, instance_version, min_version):
        super().__init__()
        self.instance_version = instance_version
        self.min_version = min_version


class InvalidEvaluationCall(Exception):
    pass
