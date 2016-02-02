from nio.util.versioning.tests import block_a_version, block_a_module_version
from nio.util.versioning.dependency import DependsOn
from nio.block.base import Block

__version__ = block_a_version


@DependsOn("nio.util.versioning.tests.required_module",
           block_a_module_version)
class BlockA(Block):
    pass
