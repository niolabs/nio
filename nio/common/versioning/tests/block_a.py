from nio.common.versioning.tests import block_a_version, block_a_module_version
from nio.common.versioning.dependency import DependsOn
from nio.common.block.base import Block

__version__ = block_a_version


@DependsOn("nio.common.versioning.tests.required_module",
           block_a_module_version)
class BlockA(Block):
    pass
