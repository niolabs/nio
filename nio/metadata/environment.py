import re

ENVIRONMENT_VAR = re.compile("\[\[([^\[\]]*)\]\]")


def is_environment_var(value):
    """ Returns True if a string contains an environment variable """
    return (isinstance(value, str) and
            ENVIRONMENT_VAR.search(value) is not None)
