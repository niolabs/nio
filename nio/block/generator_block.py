from nio.block.base import Base
from nio.block.terminals import output, DEFAULT_TERMINAL


@output(DEFAULT_TERMINAL, default=True, label="default")
class GeneratorBlock(Base):
    pass
