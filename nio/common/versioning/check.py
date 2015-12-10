from enum import Enum
import re

""" A valid version are three dotted with the format
(mayor.minor.build) where mayor and minor accept only digits and build
accept characters (accommodating for beta, release candidate (rc), etc)
"""
_version_regex = "^(?:(\d+)\.)?(?:(\d+)\.)?(\*|[a-zA-Z0-9]+)$"
_compiled_version_regex = re.compile(_version_regex)


class VersionCheckResult(Enum):
    Equal = 0
    Newer = 1
    Older = -1


class InvalidVersionFormat(Exception):
    pass


def is_version_valid(version):
    """ Allows to determine if a version string follows the version format
    """
    return _compiled_version_regex.match(version) is not None


def _pre_process(v, separator, ignore_case):
    """ Converts incoming version into a list based on separator and
    digit/character composition.

    For example:
        "1.2.1" => [1.2.1]
        "1.2.rc1" => [1.2.[rc.1]]
    """
    if ignore_case:
        v = v.lower()
    return [int(x) if x.isdigit()
            else [int(y) if y.isdigit()
                  else y for y in re.findall("\d+|[a-zA-Z]+", x)]
            for x in v.split(separator)]


def compare_versions(a, b, separator='.', ignore_case=True):
    """ Compares two versions

    Args:
        a: pivot version
        b: version to compare against

    Returns:
        (VersionCheckResult): version comparison result
    """
    # convert versions to list
    a = _pre_process(a, separator, ignore_case)
    b = _pre_process(b, separator, ignore_case)

    # compare lists
    try:
        return VersionCheckResult((a > b) - (a < b))
    except Exception as e:
        print('Versions, {0} and {1} not comparable, details: {2}'.
              format(a, b, str(e)))
        return False


def get_major_version(version_in, separator="."):
    """ Figures out a major version from a regular version.
    It does so by constructing a version starting from the major digit and
    adding zero's to it.
    """
    major = version_in.split(separator)[0]
    if not major.isdigit():
        raise ValueError("Major version must be numerical")
    return "{0}{1}0{1}0".format(major, separator)
