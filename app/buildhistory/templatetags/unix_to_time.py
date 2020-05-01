from django import template
import datetime
register = template.Library()


@register.filter('unix_to_time')
def convert_unix_to_time(timestamp):
    return datetime.datetime.fromtimestamp(int(float(timestamp)))


@register.filter('unix_to_delta')
def convert_unix_to_delta(timestamp):
    return str(datetime.timedelta(seconds=int(float(timestamp))))
