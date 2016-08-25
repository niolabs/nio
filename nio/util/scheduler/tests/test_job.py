from time import sleep

from nio.modules.scheduler.job import Job
from unittest.mock import MagicMock
from datetime import timedelta
from nio.testing.test_case import NIOTestCase
from nio.util.scheduler.scheduler import Scheduler


class Dummy(object):

    def __init__(self):
        self.foo_called = 0

    def foo(self, add=1):
        self.foo_called += add


class TestJob(NIOTestCase):

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
        sleep(0.05)
        method.assert_called_once_with()

    def test_run_repeatedly(self):
        self.job = Job(self.dummy.foo, timedelta(milliseconds=500), True)
        # jump forward in time
        Scheduler.offset = 1.5
        # allow yielding to scheduler
        sleep(0.05)
        self.assertEqual(self.dummy.foo_called, 3)

    def test_run_with_args(self):
        self.job = Job(self.dummy.foo, timedelta(milliseconds=1), False, 2)
        sleep(0.05)
        self.assertEqual(self.dummy.foo_called, 2)

    def test_run_with_kwargs(self):
        self.job = Job(self.dummy.foo, timedelta(milliseconds=1), False, add=3)
        sleep(0.05)
        self.assertEqual(self.dummy.foo_called, 3)

    def test_cancel_job(self):
        self.job = Job(self.dummy.foo, timedelta(seconds=2), True)
        self.assertEqual(self.dummy.foo_called, 0)
        self.job.cancel()
        # jump forward in time
        Scheduler.offset = 2.5
        # allow yielding to scheduler
        sleep(0.05)
        self.assertEqual(self.dummy.foo_called, 0)
