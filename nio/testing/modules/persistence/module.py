from nio.testing.modules.persistence import Persistence
from nio.modules.persistence.module import PersistenceModule


class TestingPersistenceModule(PersistenceModule):

    """ A version of the persistence module used for unit tests.

    This will proxy the Persistence class that does in-memory persistence
    and is usable in most unit tests.
    """

    def initialize(self, context):
        super().initialize(context)
        self.proxy_persistence_class(Persistence)

    def finalize(self):
        super().finalize()
