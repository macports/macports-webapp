# These are different custom validators utilised mostly in ports.views
import itertools

ALLOWED_DAYS_FOR_STATS = [0, 7, 30, 90, 180, 365]
ALLOWED_COLUMNS_FOR_SORT = ['port', '-port', 'total_count', '-total_count', '-req_count', 'req_count']


def validate_stats_days(value):
    try:
        value = int(value)
        if value not in ALLOWED_DAYS_FOR_STATS:
            return False, "Invalid value supplied. Allowed values are: {}".format(ALLOWED_DAYS_FOR_STATS)
    except ValueError:
        return False, "Invalid value supplied. Expecting an integer."
    return True, "Validation Successful"


def validate_columns_port_installations(columns):
    for value in columns:
        if value not in ALLOWED_COLUMNS_FOR_SORT:
            return False, "Invalid column value. Expecting: {}".format(ALLOWED_COLUMNS_FOR_SORT)
    return True, "Validation Successful"


def validate_unique_columns_port_installations(values):
    for i, j in itertools.combinations(values, 2):
        if i.replace('-', '') == j.replace('-', ''):
            return False, "Duplicate columns supplied. Expecting unique values for each column."
    return True, "Validation Successful"
