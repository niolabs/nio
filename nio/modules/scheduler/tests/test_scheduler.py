from unittest.mock import MagicMock
from datetime import timedelta
from time import sleep

from nio.util.support.test_case import NIOTestCase
from nio.modules.scheduler import Job


class Dummy(object):

    def __init__(self):
        self.foo_called = 0

    def foo(self, add=1):
        self.foo_called += add


class TestScheduler(NIOTestCase):

    def setUp(self):
        super().setUp()
        self.job = None
        self.dummy = Dummy()

    def tearDown(self):
        if self.job is not None:
            self.job.cancel()
        super().tearDown()

    def test_run_once(self):
        method = MagicMock()
        self.job = Job(method, timedelta(milliseconds=1), False)
        sleep(.25)
        method.assert_called_once_with()

    def test_run_repeatedly(self):
        self.job = Job(self.dummy.foo, timedelta(milliseconds=500), True)
        sleep(1.8)
        self.assertEqual(self.dummy.foo_called, 3)

    def test_run_with_args(self):
        self.job = Job(self.dummy.foo, timedelta(milliseconds=1), False, 2)
        sleep(.25)
        self.assertEqual(self.dummy.foo_called, 2)

    def test_run_with_kwargs(self):
        self.job = Job(self.dummy.foo, timedelta(milliseconds=1), False, add=3)
        sleep(.25)
        self.assertEqual(self.dummy.foo_called, 3)

    def test_cancel_job(self):
        self.job = Job(self.dummy.foo, timedelta(seconds=2), True)
        self.assertEqual(self.dummy.foo_called, 0)
        sleep(1)
        self.job.cancel()
        sleep(1.5)
        self.assertEqual(self.dummy.foo_called, 0)
