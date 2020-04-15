import itertools

ALLOWED_DAYS_FOR_STATS = [0, 7, 30, 90, 180, 365]
ALLOWED_COLUMNS_FOR_SORT = ['port', '-port', 'total_count', '-total_count', '-req_count', 'req_count']


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
