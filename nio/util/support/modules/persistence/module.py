from nio.util.support.modules.persistence import Persistence
from nio.modules.persistence.module import PersistenceModule


class TestingPersistenceModule(PersistenceModule):

    def initialize(self, context):
        super().initialize(context)
        self.proxy_persistence_class(Persistence)

    def finalize(self):
        super().finalize()
