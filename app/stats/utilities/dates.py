from datetime import datetime, timezone
from monthdelta import monthdelta

def get_first_day_of_month_x_months_ago(x = 12):
    return (datetime.now(tz=timezone.utc) - monthdelta(x)) \
            .replace(day=1, hour=0, minute=0, second=0)
