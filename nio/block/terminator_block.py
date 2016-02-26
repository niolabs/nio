from nio.block.base import Base
from nio.block.terminals import input, DEFAULT_TERMINAL


@input(DEFAULT_TERMINAL, default=True, label="default")
class TerminatorBlock(Base):
    pass
