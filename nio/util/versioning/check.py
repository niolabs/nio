from enum import Enum
import re

""" A valid version are three dotted with the format (major.minor.build)

Major and minor accept only digits and build accept characters (
accommodating for beta, release candidate (rc), etc)
"""
_version_regex = "^(?:(\d+)\.)?(?:(\d+)\.)?(\*|[a-zA-Z0-9]+)$"
_compiled_version_regex = re.compile(_version_regex)
_separators = "[.\-]+"


class VersionCheckResult(Enum):
    equal = 0
    newer = 1
    # not valid version results go below in decreasing numbers
    older = -1
    not_compatible = -2


class InvalidVersionFormat(Exception):
    pass


def is_version_valid(version):
    """ Allows to determine if a version string follows the version format

    Args:
        version: version to check against
    """
    return _compiled_version_regex.match(version) is not None


def compare_versions(a, b, separators=_separators, ignore_case=True):
    """ Compares two versions

    Args:
        a: pivot version
        b: version to compare against
        separators: version separator
        ignore_case: case sensitivity

    Returns:
        (VersionCheckResult): version comparison result
    """
    # convert versions to list
    a = _pre_process(a, separators, ignore_case)
    b = _pre_process(b, separators, ignore_case)

    # compare lists
    try:
        return VersionCheckResult((a > b) - (a < b))
    except:
        return VersionCheckResult.not_compatible


def get_major_version(version, separator="."):
    """ Figures out a major version from a regular version.

    It does so by constructing a version starting from the major digit and
    adding zero's to it.

    Args:
        version: version to check against
        separator: version separator

    Returns:
        major version
    """
    major = version.split(separator)[0]
    if not major.isdigit():
        raise ValueError("Major version must be numerical")
    return "{0}{1}0{1}0".format(major, separator)


def _pre_process(version, separators, ignore_case):
    """ Converts incoming version into a list based on separator

    Args:
        version: version to process
        separators: version separator
        ignore_case: case sensitivity

    For example:
        "1.2.1" => [1,2,1]
        "1.2.rc1" => [1,2,[rc,1]]
    """
    if ignore_case:
        version = version.lower()
    return [int(x) if x.isdigit()
            else [int(y) if y.isdigit()
                  else y for y in re.findall("\d+|[a-zA-Z]+", x)]
            for x in re.split(separators, version)]
