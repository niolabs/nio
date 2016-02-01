from nio.signal.base import Signal


class LogSignal(Signal):

    def __init__(self,
                 time,
                 context,
                 level,
                 message,
                 filename,
                 function,
                 line
                 ):
        super().__init__({"time": time,
                          "context": context,
                          "level": level,
                          "message": message,
                          "filename": filename,
                          "function": function,
                          "line": line
                          })
