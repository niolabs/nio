from nio.util.versioning.dependency import DependsOn
from nio.util.versioning.tests import block_b_version, block_b_module_version

__version__ = block_b_version


@DependsOn("nio.util.versioning.tests.required_module",
           block_b_module_version)
class BlockB(object):
    pass
