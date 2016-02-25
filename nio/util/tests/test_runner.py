from unittest.mock import Mock

from nio.util.runner import Runner, RunnerStatus
from nio.util.support.test_case import NIOTestCase


class A(object):
    pass


class B(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.b_called = True


class C(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.c_called = True


class RunnableMultiInheritance(C, A, B, Runner):
    def __init__(self, *args, status_change_callback=None, **kwargs):
        super().__init__(status_change_callback=status_change_callback)


class Runnable(Runner):
    def __init__(self, do_error=""):
        super().__init__()
        self._do_error = do_error

    def configure(self, _):
        if self._do_error == "configure":
            raise RuntimeError

    def start(self):
        if self._do_error == "start":
            raise RuntimeError

    def stop(self):
        if self._do_error == "stop":
            raise RuntimeError


class TestCreation(NIOTestCase):

    def test_creation_multi_inheritance(self):
        """ Test a runnable making use of multi inheritance

        Shows how other participating classes need to handle the __init__
        definition and the super call in order to pass all arguments along

        """
        status_callback = Mock()
        runnable = RunnableMultiInheritance(
                status_change_callback=status_callback)
        self.assertEqual(status_callback.call_count, 1)
        self.assertTrue(hasattr(runnable, "b_called"))
        self.assertTrue(hasattr(runnable, "c_called"))

    def test_creation_no_args_no_inheritance(self):
        """ Test a runnable not specifying any arguments """
        runnable = Runnable()
        self.assertTrue(runnable.status, RunnerStatus.created)

    def test_all_ok(self):
        """ Test a runnable without errors """
        runnable = Runnable()
        runnable.do_configure(None)
        self.assertEqual(runnable.status, RunnerStatus.configured)
        runnable.do_start()
        self.assertEqual(runnable.status, RunnerStatus.started)
        runnable.do_stop()
        self.assertEqual(runnable.status, RunnerStatus.stopped)

    def test_configure_error(self):
        """ Test a runnable failing to configure """
        runnable = Runnable("configure")
        with self.assertRaises(RuntimeError):
            runnable.do_configure(None)
        self.assertTrue(runnable.status.is_set(RunnerStatus.configuring))
        self.assertTrue(runnable.status.is_set(RunnerStatus.error))

    def test_start_error(self):
        """ Test a runnable failing to start """
        runnable = Runnable("start")
        with self.assertRaises(RuntimeError):
            runnable.do_start()
        self.assertTrue(runnable.status.is_set(RunnerStatus.starting))
        self.assertTrue(runnable.status.is_set(RunnerStatus.error))

    def test_stop_error(self):
        """ Test a runnable failing to stop """
        runnable = Runnable("stop")
        runnable.do_stop()
        self.assertTrue(runnable.status.is_set(RunnerStatus.stopping))
        self.assertTrue(runnable.status.is_set(RunnerStatus.error))
