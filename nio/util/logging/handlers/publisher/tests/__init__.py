import inspect
from time import time


class LogRecordTest(object):
    def __init__(self, filename, line_number, msg, level_name=""):
        """ Creates an instance of a TestLogRecord
        """
        self.created = time()
        self.context = None
        self.levelname = level_name
        self.msg = msg
        self.filename = filename
        self.funcName = None
        self.lineno = line_number


def lineno():
    """ Returns the current line number
    """
    return inspect.currentframe().f_back.f_lineno


def get_log_record_same_line(msg):
    return LogRecordTest(__file__, lineno(), msg)
