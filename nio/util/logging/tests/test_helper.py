from unittest.mock import patch
from nio.testing.test_case import NIOTestCase
from nio.util.logging.helper import LoggingHelper


class TestLoggingHelper(NIOTestCase):

    def setUp(self):
        super().setUp()
        LoggingHelper._deregister_prefix()

    def tearDown(self):
        LoggingHelper._deregister_prefix()
        super().tearDown()

    def test_same_logger(self):
        """Tests that the same logger is returned on subsequent calls"""
        logger1 = LoggingHelper.get_nio_logger('test logger')
        logger2 = LoggingHelper.get_nio_logger('test logger')
        logger3 = LoggingHelper.get_nio_logger('different logger')
        self.assertEqual(logger1.logger, logger2.logger)
        self.assertNotEqual(logger1.logger, logger3.logger)

    def test_default_logger(self):
        """Test that a default logger is returned with no name"""
        self._assert_logger_name(None, 'default')
        self._assert_logger_name('', 'default')

    def test_prefix(self):
        """Test that the loggers can have a prefix"""
        # We should start off with no prefix
        self._assert_logger_name('logger name', 'logger name')
        # Register a prefix and make sure that is prepended
        LoggingHelper._register_prefix('prefix')
        self.assertEqual(LoggingHelper._prefix, 'prefix')
        self._assert_logger_name('logger name', 'prefix.logger name')
        # Now deregister the prefix and make sure it is not included
        LoggingHelper._deregister_prefix()
        self._assert_logger_name('logger name', 'logger name')

    def test_must_have_prefix(self):
        """Registering a bad prefix calls deregister prefix"""
        # Can't register false as a prefix
        with patch.object(LoggingHelper, '_deregister_prefix') as dereg:
            LoggingHelper._register_prefix(False)
            self.assertEqual(dereg.call_count, 1)

        # Can't register None as a prefix
        with patch.object(LoggingHelper, '_deregister_prefix') as dereg:
            LoggingHelper._register_prefix(None)
            self.assertEqual(dereg.call_count, 1)

        # Can't register empty string as a prefix
        with patch.object(LoggingHelper, '_deregister_prefix') as dereg:
            LoggingHelper._register_prefix('')
            self.assertEqual(dereg.call_count, 1)

    def _assert_logger_name(self, logger_to_get, logger_name_to_match=None):
        """ Make sure retrieving a logger fetches the right logger name """
        if logger_name_to_match is None:
            logger_name_to_match = logger_to_get

        with patch('logging.getLogger') as logger_call:
            LoggingHelper.get_nio_logger(logger_to_get)
            logger_call.assert_called_with(logger_name_to_match)
