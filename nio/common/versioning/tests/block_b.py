from nio.common.versioning.dependency import DependsOn
from nio.common.versioning.tests import block_b_version, block_b_module_version

__version__ = block_b_version


@DependsOn("nio.common.versioning.tests.required_module",
           block_b_module_version)
class BlockB(object):
    pass
