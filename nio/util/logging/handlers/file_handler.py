from threading import RLock
from logging.handlers import RotatingFileHandler
from os import path, makedirs

MAX_FILE_SIZE = 1024 * 1024 * 15  # 15 MB


class NIOFileHandler(RotatingFileHandler):

    """ File handler for logging. Automatically rolls over at maxBytes.

    Instances of this class will be registered with the base Logger on an
    as-needed basis.

    """

    def __init__(self, dirname='.', filename='log_placeholder',
                 max_bytes=MAX_FILE_SIZE, backup_count=1):
        self.dirname = dirname
        self.filename = filename
        fname = self._construct_fname()
        super().__init__(fname, maxBytes=max_bytes,
                         backupCount=backup_count)

    def _construct_fname(self):
        """ Build the log-file name based on date and the name of logger.

        Args:
            name (str): the name of the logger to which this handler is
            registered

        Returns:
            (str): The basename for the log file. Successive integers will
            be appended as logs roll over.

        """
        # create the target directory if it doesn't exist
        if not path.isdir(self.dirname):
            makedirs(self.dirname)

        f = "{0}.log".format(self.filename)
        return path.join(self.dirname, f)


class NIOShareFileHandler(NIOFileHandler):

    """ NIO File Handler that caches open streams to the log file

    In Windows when more than one stream causes:

    PermissionError: [WinError 32] The process cannot access the file because
    it is being used by another process:

    """
    file_handlers = {}

    def __init__(self, dirname='.', filename='log_placeholder',
                 max_bytes=MAX_FILE_SIZE, backup_count=1):
        self._lock = RLock()
        super().__init__(dirname, filename, max_bytes, backup_count)

    def doRollover(self):
        """ Removes the cached handler before doing the doRollOver """
        with self._lock:
            self.__class__.file_handlers[self.baseFilename] = None
        super().doRollover()

    def _open(self):
        """ Open the file used for logging

        Caches an open stream to a file so the file can be rollover
        and renamed.
        """
        with self._lock:
            stream = self.__class__.file_handlers.get(self.baseFilename)
            if not stream:
                stream = super()._open()
                self.__class__.file_handlers[self.baseFilename] = stream
            return stream
