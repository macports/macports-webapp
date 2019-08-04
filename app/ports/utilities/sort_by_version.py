from distutils.version import LooseVersion


def sort_list_of_dicts_by_version(lst, key):
    return sorted(lst, key=lambda x: LooseVersion(x[key]), reverse=True)


def sort_list_by_version(lst):
    return sorted(lst, key=lambda x: LooseVersion(x), reverse=True)
