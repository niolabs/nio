from nio.signal.base import Signal


class LogSignal(Signal):

    """ A log signal to encapsulate log record information

    """

    def __init__(self,
                 time,
                 context,
                 level,
                 message,
                 filename,
                 function,
                 line
                 ):
        """ Create a new LogSignal instance.

        Args:
            time: logging instruction time
            context: logging instruction context
            level: logging level
            message: logging message
            filename: filename where logging instruction resides
            function: function where logging instruction resides
            line: line number where logging instruction resides

        """
        super().__init__({"time": time,
                          "context": context,
                          "level": level,
                          "message": message,
                          "filename": filename,
                          "function": function,
                          "line": line
                          })
