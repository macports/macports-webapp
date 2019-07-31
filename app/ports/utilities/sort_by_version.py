def sort_list_of_dicts_by_version(lst, key):
    return sorted(lst, key=lambda x: tuple(int(i) for i in x[key].split(".")), reverse=True)


def sort_list_by_version(lst):
    return sorted(lst, key=lambda x: tuple(int(i) for i in x.split(".")), reverse=True)
