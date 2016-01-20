"""
  NIO block support base class

"""
from collections import defaultdict
from nio.router.base import InvalidBlockOutput
from nio.util.support.test_case import NIOTestCase
from nio.router.base import BlockRouter
from nio.block.context import BlockContext
from nio.common.signal.status import StatusSignal


class TestBlockRouter(BlockRouter):

    def __init__(self):
        super().__init__()
        self._test_case = None
        self._block_signal_counts = {}
        self._block_mgmt_signal_counts = defaultdict(int)
        self._block_status = {}

    def configure(self, test_case):
        self._test_case = test_case

    def notify_signals(self, block, signals, output_id='default'):

        if not block.is_output_valid(output_id):
            msg = "Invalid output: '{0}' for block: {1}".format(
                output_id, block.name)
            raise InvalidBlockOutput(msg)

        self._block_signal_counts[block] = \
            self._block_signal_counts.get(block) or defaultdict(int)

        self._block_signal_counts[block][output_id] += len(signals)
        self._test_case.signals_notified(signals, output_id)

    def notify_management_signal(self, block, signal):
        if isinstance(signal, StatusSignal):
            self._block_status[block] = signal.status
        self._block_mgmt_signal_counts[block] += 1
        self._test_case.management_signal_notified(signal)

    def get_signals_from_block(self, block=None, output_id='default'):
        """Returns the number of signals a block has notified.

        If block is None, return the total number of signals notified.

        """
        if block is None:
            return sum([sum(blk.values()) for blk
                        in self._block_signal_counts.values()])

        block_counts = self._block_signal_counts.get(block)
        if block_counts is None:
            return 0

        return block_counts.get(output_id) or 0


class NIOBlockTestCase(NIOTestCase):

    """ Base Unit Test case class for blocks

    Allows block tests to see the signals that get notified and access some
    other data about them by setting up a router.

    Simply create the block you want to use and call configure_block with the
    properties the block should have.

    Example:
    b = MyTestableBlock()
    self.configure_block(b, {"loglevel": "DEBUG"})

    Now, whenever b notifies signals, the signals_notified function will be
    called in the test case.
    """

    def __init__(self, methodName='runTests'):
        super().__init__(methodName)
        self._router = TestBlockRouter()
        self.last_notified = defaultdict(list)

    def setUp(self):
        super().setUp()
        self._router.configure(self)

    def tearDown(self):
        super().tearDown()

    def configure_block(self, block, block_properties, hooks=None):
        block.configure(BlockContext(
            self._router,
            block_properties,
            'TestSuite',
            ''))

    def signals_notified(self, signals, output_id='default'):
        """Method to be overridden by sub-classed tests.

        This method will get called with the signals that the block notifies.
        """
        self.last_notified[output_id].extend(signals)

    def management_signal_notified(self, signal):
        """Method to be overridden by sub-classed tests.

        This method will get called with the management signals that the
        block notifies.
        """
        pass

    def assert_num_signals_notified(self, num, block=None,
                                    output_id='default'):
        """Assert that the number of signals notified is a certain number.

        Keyword Args:
            block (Block): the block which should have notified. If not
                included, all blocks will be considered.
            output_id: The output id of the block to consider.
        """
        signals = self._router.get_signals_from_block(block, output_id)
        self.assertEqual(num, signals)

    def assert_num_mgmt_signals_notified(self, num, block=None):
        """Assert the number of management signals notified is a number.

        Keyword Args:
            block (Block): the block which should have notified. If not
                included, all blocks will be considered.
        """
        if block:
            self.assertEqual(
                num, self._router._block_mgmt_signal_counts[block])
        else:
            self.assertEqual(
                num, sum(self._router._block_mgmt_signal_counts.values()))

    def assert_block_status(self, block, status):
        """ Asserts that the given block has a certain block status

        Blocks will have a status of '' if they have not had a status
        reported yet.

        Keyword Args:
            block (Block): The block to check the status of
            status (BlockStatus.xxx): The BlockStatus enum value to have
        """
        self.assertEqual(self._router._block_status.get(block, ''), status)
