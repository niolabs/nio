from logging import LogRecord
import logging
from nio.util.logging.filter import NIOFilter
from nio.testing.test_case import NIOTestCaseNoModules


class TestFilter(NIOTestCaseNoModules):

    def test_filter_withniotime(self):
        "Tests filter works fine when record has niotime"
        filter = NIOFilter()

        record1 = LogRecord("", logging.INFO, "", 1,
                            "This is an error with niottime",
                            None,
                            Exception())
        setattr(record1, "niotime", "12345")
        setattr(record1, "context", "12345")
        filter.filter(record1)
        self.assertTrue(record1.niotime, "12345")
        self.assertTrue(record1.context, "mycontext")

    def test_filter_noniotime(self):
        "Tests filter works fine when record does not have niotime"
        filter = NIOFilter()
        record1 = LogRecord("mycontext", logging.INFO, "", 1,
                            "This is an error without niottime",
                            None,
                            Exception())
        filter.filter(record1)
        self.assertIsNotNone(record1.niotime)
        self.assertTrue(record1.context, "mycontext")
