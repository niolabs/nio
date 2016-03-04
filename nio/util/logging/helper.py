import logging
from nio.util.logging.adapter import NIOAdapter


class LoggingHelper(object):

    _prefix = None

    @classmethod
    def get_nio_logger(cls, logger_name=None):
        if not logger_name:
            logger_name = 'default'

        if cls._prefix:
            logger_name = "{}.{}".format(cls._prefix, logger_name)

        return NIOAdapter(logging.getLogger(logger_name))

    @classmethod
    def _register_prefix(cls, prefix_name):
        if prefix_name:
            cls._prefix = prefix_name
        else:
            cls._deregister_prefix()

    @classmethod
    def _deregister_prefix(cls):
        cls._prefix = None
