"""
  NIO block support base class

"""
from collections import defaultdict
from nio.testing.test_case import NIOTestCase
from nio.router.base import BlockRouter
from nio.block.context import BlockContext
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.status import StatusSignal


class BlockRouterForTesting(BlockRouter):

    """ A testing router to be used in block test cases.

    Supports block tests by keeping track of signal counts per block and
    block status as provided by management signals.
    """

    def __init__(self):
        super().__init__()
        self._test_case = None
        self._block_signal_counts = {}
        self._block_mgmt_signal_counts = defaultdict(int)
        self._block_status = {}

    def configure(self, test_case):
        """ Configures router by saving the test case being supported

        Args:
            test_case (NIOTestCase): test case to call when notifying signals

        """
        self._test_case = test_case

    def notify_signals(self, block, signals, output_id):
        """ Receives block signals.

         Keeps track of the signal count per block and per output id
         Forwards notification to test_case's 'signals_notified' method

        Args:
            block (Block): notifier block
            signals (list): signals being notified
            output_id: output identifier

        """
        if output_id is None:
            output_id = DEFAULT_TERMINAL

        self._block_signal_counts[block] = \
            self._block_signal_counts.get(block) or defaultdict(int)
        self._block_signal_counts[block][output_id] += len(signals)

        self._test_case.signals_notified(block, signals, output_id)

    def notify_management_signal(self, block, signal):
        """ Receives management signal.

        Keeps track of the signal count per block
        Forwards signal to test_case's 'management_signal_notified' method

        Args:
            block (Block): notifier block
            signal (Signal): signal being notified

        """
        if isinstance(signal, StatusSignal):
            self._block_status[block] = signal.status

        self._block_mgmt_signal_counts[block] += 1
        self._test_case.management_signal_notified(block, signal)

    def get_signals_from_block(self, block=None, output_id=DEFAULT_TERMINAL):
        """ Provides signal count per block or for all blocks

        Args:
            block (Block): block instance
            output_id: output identifier

        Returns:
            The number of signals a block has notified.
            If block is None, return the total number of signals notified

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
        self._router = BlockRouterForTesting()
        self.last_notified = defaultdict(list)

    def setUp(self):
        super().setUp()
        self._router.configure(self)

    def tearDown(self):
        super().tearDown()

    def configure_block(self, block, block_properties):
        """ Configures block by assigning properties and router to given block

        Args:
            block (Block): block instance
            block_properties (dict): properties to assign

        """
        # Blocks should always have a 'name', but we'll let it pass in tests
        block_properties["name"] = block_properties.get("name", "default")
        block.configure(BlockContext(
            self._router,
            block_properties,
            'TestSuite',
            ''))

    def signals_notified(self, block, signals, output_id):
        """ Receives block signals notification

        Args:
            block (Block): notifying block
            signals (list): signals being notified
            output_id: output identifier

        """
        self.last_notified[output_id].extend(signals)

    def management_signal_notified(self, block, signal):
        """ Receives block management signal notification

        Args:
            block (Block): notifying block
            signal (Signal): signal being notified
        """
        pass

    def assert_num_signals_notified(self, num, block=None,
                                    output_id=DEFAULT_TERMINAL):
        """ Assert that the number of signals notified is a certain number.

        Args:
            num (int): number to check against
            block (Block): the block which should have notified. If not
                included, all blocks will be considered.
            output_id: The output id of the block to consider.
        """
        signals = self._router.get_signals_from_block(block, output_id)
        self.assertEqual(num, signals)

    def assert_num_mgmt_signals_notified(self, num, block=None):
        """ Assert the number of management signals notified is a number.

        Args:
            num (int): number to check against
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

        Args:
            block (Block): The block to check the status of
            status (BlockStatus.xxx): The BlockStatus enum value to have
        """
        self.assertEqual(self._router._block_status.get(block, ''), status)
