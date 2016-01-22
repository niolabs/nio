class ModuleContext(object):

    def __init__(self, configuration=None):
        self.configuration = configuration if configuration is not None else {}
