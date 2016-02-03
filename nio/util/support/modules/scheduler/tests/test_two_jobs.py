from datetime import timedelta
from time import sleep
from nio.modules.scheduler.job import Job
from nio.util.support.modules.scheduler.tests.custom_base_test \
    import CustomSchedulerTestCase


class Dummy(object):

    def __init__(self):
        self.foo1_called = False
        self.foo2_called = False

    def foo1(self):
        assert self.foo2_called
        self.foo1_called = True

    def foo2(self):
        self.foo2_called = True


class TestScheduler(CustomSchedulerTestCase):

    def test_two_jobs(self):
        """ Asserts that independently of the order, the right task is
        executed first
        """

        dummy = Dummy()
        self.job1 = Job(dummy.foo1, timedelta(milliseconds=500), False)
        self.job2 = Job(dummy.foo2, timedelta(milliseconds=100), False)
        sleep(0.8)
        self.assertEqual(dummy.foo1_called, True)
        self.assertEqual(dummy.foo2_called, True)

    def test_two_jobs_reverse_order(self):
        """ Asserts that independently of the order, the right task is
        executed first, same as above test but calls are reversed
        """
        dummy = Dummy()
        self.job2 = Job(dummy.foo2, timedelta(milliseconds=100), False)
        self.job1 = Job(dummy.foo1, timedelta(milliseconds=500), False)
        sleep(0.8)
        self.assertEqual(dummy.foo1_called, True)
        self.assertEqual(dummy.foo2_called, True)
