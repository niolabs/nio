from datetime import timedelta
from time import sleep
from nio.modules.scheduler.job import Job
from nio.util.support.test_case import NIOTestCase


arg1_parameter = "8"
kwarg1_parameter = "kwarg1_replacement"


class Dummy(object):

    def __init__(self):
        self.foo1_called = False

    def foo1(self, arg1, kwarg1='kwarg1'):
        self.foo1_called = True
        assert (arg1 == arg1_parameter)
        assert (kwarg1 == kwarg1_parameter)


class TestScheduler(NIOTestCase):

    def test_args(self):
        """ Asserts that scheduler accepts args and kwargs """
        dummy = Dummy()
        self.job1 = Job(dummy.foo1, timedelta(milliseconds=100), False,
                        arg1_parameter, kwarg1_parameter)
        sleep(0.15)
        self.assertEqual(dummy.foo1_called, True)
