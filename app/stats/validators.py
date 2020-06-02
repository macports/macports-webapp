import itertools

ALLOWED_DAYS_FOR_STATS = [0, 7, 30, 90, 180, 365]
ALLOWED_COLUMNS_FOR_SORT = ['port', '-port', 'total_count', '-total_count', '-req_count', 'req_count']
ALLOWED_PROPERTIES = [
    'requested',
    'version',
    'variants',
    'submission__os_version',
    'submission__xcode_version',
    'submission__clt_version',
    'submission__os_arch',
    'submission__build_arch',
    'submission__platform',
    'submission__macports_version',
    'submission__cxx_stdlib'
]

ALLOWED_GENERAL_PROPERTIES = [
    'os_version',
    'xcode_version',
    'clt_version',
    'os_arch',
    'build_arch',
    'platform',
    'macports_version',
    'cxx_stdlib'
]


def validate_stats_days(value):
    try:
        value = int(value)
        if value not in ALLOWED_DAYS_FOR_STATS:
            return False, "'{}' is an invalid value. Allowed values are: {}".format(value, ALLOWED_DAYS_FOR_STATS)
    except ValueError:
        return False, "Received '{}'. Expecting an integer.".format(value)
    return True, "Validation Successful"


def validate_columns_port_installations(columns):
    for value in columns:
        if value not in ALLOWED_COLUMNS_FOR_SORT:
            return False, "{} is an invalid column. Expecting: {}".format(value, ALLOWED_COLUMNS_FOR_SORT)
    return True, "Validation Successful"


def validate_unique_columns_port_installations(values):
    for i, j in itertools.combinations(values, 2):
        if i.replace('-', '') == j.replace('-', ''):
            return False, "'{}' and '{}' refer to the same column.".format(i, j)
    return True, "Validation Successful"
