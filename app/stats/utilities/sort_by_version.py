import re
from functools import cmp_to_key


# Tries to apply the same version sorting algorithm as used by macports-base
# https://github.com/macports/macports-base/blob/master/src/pextlib1.0/vercomp.c
def version_compare(version1, version2):
    # Split on all non-alphanumeric characters and delete any empty ('') elements
    # that might occur due to consecutive non-alphanumerics
    version1_segments = list(filter(None, re.split('[^a-zA-Z0-9]', version1)))
    version2_segments = list(filter(None, re.split('[^a-zA-Z0-9]', version2)))

    version1_len = len(version1_segments)
    version2_len = len(version2_segments)

    # Now traverse the two lists and compare segments at each index
    i = 0
    while i < version1_len and i < version2_len:
        s1 = version1_segments[i]
        s2 = version2_segments[i]

        # If version1's segment is a numeric segment and version2's segment
        # is non-numeric, consider version1 to be a newer version
        if s1.isnumeric() and (not s2.isnumeric()):
            return -1

        # If the segments are of different types, consider version2 be newer
        if (s1.isnumeric() and s2.isalpha()) or (s1.isalpha() and s2.isnumeric()):
            return 1

        # The segments are either both numeric or both alphabetical
        # If they are numeric, convert to integers and compare
        if s1.isnumeric() and s2.isnumeric():
            if int(s1) > int(s2):
                return -1
            elif int(s1) < int(s2):
                return 1
        else:
            if s1 > s2:
                return -1
            elif s1 < s2:
                return 1

        i += 1

    # If the length of both the versions is same, means they are equal
    if i == version1_len and i == version2_len:
        return 0

    # Otherwise, the version with a greater length is newer
    return 1 if version2_len > version1_len else -1


def sort_list_of_dicts_by_version(lst, key):
    return sorted(lst, key=cmp_to_key(lambda x, y: version_compare(x[key], y[key])))


def sort_list_by_version(lst):
    return sorted(lst, key=cmp_to_key(version_compare))
