class ModuleContext(object):

    """ A class containing configuration information for a module.

    This object will get passed to the Module object when it is initialized.
    """

    def __init__(self, configuration=None):
        self.configuration = configuration if configuration is not None else {}
