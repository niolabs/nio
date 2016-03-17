def add_message_to_exception(exception, message):
    original_message = exception.args[0] if len(exception.args) else ""
    # wrap it up in new tuple
    exception.args = (original_message + message,)
