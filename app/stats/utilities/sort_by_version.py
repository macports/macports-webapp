from distutils.version import LooseVersion


def cleaned_version(version):
    return version.replace("_", ".").replace("-", ".")


def sort_list_of_dicts_by_version(lst, key):
    return sorted(lst, key=lambda x: LooseVersion(cleaned_version(x[key])), reverse=True)


def sort_list_by_version(lst):
    return sorted(lst, key=lambda x: LooseVersion(cleaned_version(x)), reverse=True)
