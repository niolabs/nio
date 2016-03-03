from time import sleep
from threading import Event

from nio.util.support.test_case import NIOTestCaseNoModules
from nio.util.threading import spawn


class MyException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs


class Target(object):

    def __init__(self, event):
        self.event = event
        self.args = []
        self.kwargs = []

    def receiver(self, arg1, arg2, key1="key1_default", key2="key2_default"):
        self.args.append(arg1)
        self.args.append(arg2)

        self.kwargs.append(key1)
        self.kwargs.append(key2)
        self.event.set()

        return "verify this"


class TestSpawn(NIOTestCaseNoModules):

    def setUp(self):
        super().setUp()
        self._exception_thrown = False

    def test_spawn(self):
        """ Asserts that arguments are passed correctly """
        receiver_event = Event()
        target = Target(receiver_event)
        thread = spawn(target.receiver, "1", "2",
                       key1="key1_passed", key2="key2_passed")

        self.assertTrue(receiver_event.wait(1))

        self.assertEqual(target.args[0], "1")
        self.assertEqual(target.args[1], "2")

        self.assertEqual(target.kwargs[0], "key1_passed")
        self.assertEqual(target.kwargs[1], "key2_passed")

        result = thread.join()
        self.assertEqual(thread.nio_result, "verify this")
        self.assertEqual(result, "verify this")

    def test_spawn_kw_defaults(self):
        """ Asserts that when kwargs are not given, defaults are received """
        receiver_event = Event()
        target = Target(receiver_event)
        spawn(target.receiver, "1", "2")

        self.assertTrue(receiver_event.wait(1))

        self.assertEqual(target.args[0], "1")
        self.assertEqual(target.args[1], "2")

        self.assertEqual(target.kwargs[0], "key1_default")
        self.assertEqual(target.kwargs[1], "key2_default")

    def test_spawn_exception_no_join(self):
        """ Asserts caller not affected if join isn't called

        Asserts that, when no join is executed, the caller does not
        get affected (default python behaviour), yet if really
        looking the exception is stored in thread instance
        """
        thread = spawn(self.throw_exception, "arg1", kwarg1="2")
        # allow time for thread to execute
        sleep(0.1)
        self.assertTrue(self._exception_thrown)
        self.assertIsNotNone(thread.nio_exception)

    def test_spawn_exception_and_join1(self):
        """ Assert that exception is thrown when joining the thread """
        thread = spawn(self.throw_exception)
        with self.assertRaises(MyException):
            thread.join()
        self.assertTrue(self._exception_thrown)

    def test_spawn_exception_and_join2(self):
        """ Asserts that spawn exception comes with arguments """
        try:
            thread = spawn(self.throw_exception, "arg1", kwarg1="2")
            thread.join()
            raise RuntimeError("Join did not throw expected exception")
        except MyException as e:
            self.assertEqual(e.args, ("arg1",))
            self.assertTrue(e.kwargs["kwarg1"], "2")
        self.assertTrue(self._exception_thrown)

    def throw_exception(self, *args, **kwargs):
        self._exception_thrown = True
        raise MyException(*args, **kwargs)
